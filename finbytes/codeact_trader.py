"""
CodeAct-powered trading analysis system.
Allows traders to build analysis scenarios using natural language.
"""
import tempfile
import os
import json
import logging
from typing import Dict, Optional
import pandas as pd

# Try multiple import patterns for CodeAct
CODEACT_AVAILABLE = False
CodeActAgent = None

# Option 1: Try direct CodeAct package import
try:
    from codeact import CodeActAgent
    CODEACT_AVAILABLE = True
except ImportError:
    try:
        from codeact.agent import CodeActAgent
        CODEACT_AVAILABLE = True
    except ImportError:
        try:
            from code_act import CodeActAgent
            CODEACT_AVAILABLE = True
        except ImportError:
            CODEACT_AVAILABLE = False

# Option 2: Try CodeAct API client (OpenAI-compatible API)
CODEACT_API_AVAILABLE = False
try:
    from .codeact_api_client import CodeActAPIClient
    CODEACT_API_AVAILABLE = True
except ImportError:
    CODEACT_API_AVAILABLE = False

# Check if either method is available
if not CODEACT_AVAILABLE and not CODEACT_API_AVAILABLE:
    # Don't raise error - allow SimpleTrader to be used instead
    CODEACT_AVAILABLE = False

from .ohlca_api import fetch_ohlc_data

logger = logging.getLogger(__name__)


class TraderCodeAct:
    """
    CodeAct-powered trader that executes natural language trading queries.
    """
    
    def __init__(
        self,
        model_name: str = None,
        api_base: str = None,
        jupyter_url: str = None,
        use_api: bool = None
    ):
        """
        Initialize CodeAct agent.
        
        Args:
            model_name: Model name (Hugging Face ID or API model name)
            api_base: OpenAI-compatible API base URL (e.g., http://localhost:8080/v1)
            jupyter_url: Jupyter execution engine URL (e.g., http://localhost:8081/execute)
            use_api: Force use of API client (True) or direct model (False). Auto-detect if None.
        """
        self.model_name = model_name or "xingyaoww/CodeActAgent-Mistral-7b-v0.1"
        self.use_api = use_api
        
        # Auto-detect: prefer API if available and configured
        if self.use_api is None:
            if CODEACT_API_AVAILABLE and (api_base or os.getenv("CODEACT_API_BASE")):
                self.use_api = True
            elif CODEACT_AVAILABLE:
                self.use_api = False
            else:
                raise ImportError(
                    "CodeAct not available. Options:\n"
                    "1. Install CodeAct package: git clone https://github.com/xingyaoww/code-act.git\n"
                    "2. Set up CodeAct API: See CODEACT_FULL_SETUP.md\n"
                    "3. Use SimpleTrader instead (works without CodeAct)"
                )
        
        if self.use_api:
            # Use API client
            if not CODEACT_API_AVAILABLE:
                raise ImportError("CodeAct API client not available")
            logger.info(f"Initializing CodeAct API client: {self.model_name}")
            self.api_client = CodeActAPIClient(
                api_base=api_base,
                model_name=self.model_name,
                jupyter_url=jupyter_url
            )
            logger.info("CodeAct API client initialized successfully")
        else:
            # Use direct model
            if not CODEACT_AVAILABLE:
                raise ImportError("CodeAct package not available")
            try:
                logger.info(f"Loading CodeAct model: {self.model_name}")
                self.agent = CodeActAgent.from_pretrained(self.model_name)
                logger.info("CodeAct agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CodeAct agent: {e}")
                raise
    
    def analyze(
        self,
        user_query: str,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Execute trading analysis using natural language query.
        
        Args:
            user_query: Natural language trading strategy/analysis request
            symbol: Stock symbol (e.g., 'AAPL')
            interval: Time interval ('1d', '1w', '1mo')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            Dictionary with analysis results including:
            - summary: Text summary of analysis
            - total_return_pct: Total return percentage
            - sharpe: Sharpe ratio
            - max_dd_pct: Maximum drawdown percentage
            - trades: Number of trades
            - win_rate_pct: Win rate percentage
            - plot: Path to generated plot (if any)
        """
        tmp_csv = None
        
        try:
            # 1. Fetch data from API
            logger.info(f"Fetching OHLC data for {symbol}")
            df = fetch_ohlc_data(symbol, interval, start_date, end_date)
            
            # 2. Save to temporary CSV
            tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w')
            df.to_csv(tmp_csv.name)
            tmp_csv.close()
            
            logger.info(f"Data saved to {tmp_csv.name}")
            
            # 3. Build prompt for CodeAct
            prompt = f"""
You are a professional quantitative trader analyzing real market data.

OHLC DATA:
- CSV file location: '{tmp_csv.name}'
- Columns: Date (index), Open, High, Low, Close, Volume
- Symbol: {symbol}
- Interval: {interval}
- Date range: {start_date} to {end_date}
- Number of rows: {len(df)}

TASK:
{user_query}

REQUIREMENTS:
1. Load the CSV using pandas: df = pd.read_csv('{tmp_csv.name}', index_col='Date', parse_dates=True)
2. Use appropriate libraries: pandas, numpy, matplotlib, vectorbt, ta
3. Perform the requested analysis/backtest
4. Generate visualizations if applicable (save to /tmp/result.png)
5. Calculate key metrics: total return, Sharpe ratio, max drawdown, number of trades, win rate

OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
  "summary": "Brief text summary of the analysis (2-3 sentences)",
  "total_return_pct": float or null,
  "sharpe": float or null,
  "max_dd_pct": float or null,
  "trades": int or null,
  "win_rate_pct": float or null,
  "plot": "/tmp/result.png" or null
}}

If a metric is not applicable, use null. Save plots to /tmp/result.png if visualizations are created.

IMPORTANT:
- Write clean, production-ready code
- Handle errors gracefully
- Use proper pandas datetime indexing
- If backtesting, use vectorbt for accurate results
- Return ONLY the JSON object, no additional text
"""
            
            # 4. Execute CodeAct
            logger.info("Executing CodeAct analysis...")
            if self.use_api:
                # Use API client
                result_data = self.api_client.run_interactive(
                    user_query=prompt,
                    system_prompt="You are a professional quantitative trader analyzing real market data."
                )
                raw_output = result_data['final_response']
            else:
                # Use direct agent
                raw_output = self.agent.run(prompt)
            logger.info("CodeAct execution completed")
            
            # 5. Parse result
            result = self._parse_output(raw_output)
            
            # 6. Add metadata
            result["symbol"] = symbol
            result["interval"] = interval
            result["start_date"] = start_date
            result["end_date"] = end_date
            result["data_points"] = len(df)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "summary": f"Analysis failed: {str(e)}",
                "symbol": symbol,
                "interval": interval,
                "start_date": start_date,
                "end_date": end_date
            }
        finally:
            # Cleanup temporary file
            if tmp_csv and os.path.exists(tmp_csv.name):
                try:
                    os.unlink(tmp_csv.name)
                    logger.info(f"Cleaned up temporary file: {tmp_csv.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
    
    def _parse_output(self, raw_output: str) -> Dict:
        """
        Parse CodeAct output to extract JSON result.
        
        Args:
            raw_output: Raw output from CodeAct agent
            
        Returns:
            Parsed dictionary result
        """
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in raw_output:
                start = raw_output.find("```json") + 7
                end = raw_output.find("```", start)
                json_str = raw_output[start:end].strip()
            elif "```" in raw_output:
                start = raw_output.find("```") + 3
                end = raw_output.find("```", start)
                json_str = raw_output[start:end].strip()
            else:
                # Try to find JSON object in output
                start = raw_output.find("{")
                end = raw_output.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = raw_output[start:end]
                else:
                    raise ValueError("No JSON found in output")
            
            result = json.loads(json_str)
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from output: {e}")
            logger.debug(f"Raw output: {raw_output[:500]}")
            return {
                "summary": raw_output[:500],
                "error": "Failed to parse JSON output",
                "raw_output": raw_output[:1000]
            }
        except Exception as e:
            logger.warning(f"Error parsing output: {e}")
            return {
                "summary": raw_output[:500],
                "error": f"Parse error: {str(e)}"
            }

