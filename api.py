"""
FastAPI endpoint for CodeAct trading analysis.
Deploy to Cloud Run for production use.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
import uvicorn

# Try to import TraderCodeAct, but handle gracefully if CodeAct is not installed
CODEACT_AVAILABLE = False
try:
    from finbytes.codeact_trader import TraderCodeAct
    CODEACT_AVAILABLE = True
except ImportError as e:
    CODEACT_AVAILABLE = False

# Always import SimpleTrader as fallback
from finbytes.simple_trader import SimpleTrader
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinBytes CodeAct Trading Analysis API",
    description="Natural language trading analysis powered by CodeAct" + (" (CodeAct not installed - limited mode)" if not CODEACT_AVAILABLE else ""),
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize traders (lazy loading)
_trader_agent = None
_simple_trader = None

def get_trader():
    """Get trader instance (CodeAct if available, otherwise SimpleTrader)."""
    global _trader_agent, _simple_trader
    
    # Try CodeAct first if available
    if CODEACT_AVAILABLE:
        try:
            if _trader_agent is None:
                logger.info("Initializing CodeAct agent...")
                _trader_agent = TraderCodeAct()
            return _trader_agent
        except Exception as e:
            logger.warning(f"CodeAct initialization failed: {e}, falling back to SimpleTrader")
            # Fall through to SimpleTrader
    
    # Use SimpleTrader as fallback
    if _simple_trader is None:
        logger.info("Using SimpleTrader (CodeAct not available or failed)")
        _simple_trader = SimpleTrader()
    return _simple_trader


class AnalysisRequest(BaseModel):
    """Request model for trading analysis."""
    query: str = Field(..., description="Natural language trading strategy/analysis query")
    symbol: str = Field(..., description="Stock symbol (e.g., 'AAPL')")
    interval: str = Field(default="1w", description="Time interval: '1d', '1w', or '1mo'")
    start_date: str = Field(..., description="Start date in 'YYYY-MM-DD' format")
    end_date: str = Field(..., description="End date in 'YYYY-MM-DD' format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Backtest RSI(14) + SMA(20) crossover strategy. Enter long when RSI < 30 and Close > SMA(20). Exit when RSI > 70.",
                "symbol": "AAPL",
                "interval": "1w",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31"
            }
        }


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FinBytes CodeAct Trading Analysis API",
        "version": "1.0.0",
        "codeact_available": CODEACT_AVAILABLE,
        "message": "CodeAct installed and ready" if CODEACT_AVAILABLE else "CodeAct not installed - install using ./install_codeact.sh"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze")
def analyze(request: AnalysisRequest):
    """
    Execute trading analysis using natural language query.
    
    Example request:
    ```json
    {
        "query": "Backtest MACD crossover with volume filter",
        "symbol": "AAPL",
        "interval": "1w",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31"
    }
    ```
    """
    try:
        logger.info(f"Received analysis request for {request.symbol}")
        
        # Get trader (CodeAct or SimpleTrader)
        trader = get_trader()
        
        # Execute analysis
        result = trader.analyze(
            user_query=request.query,
            symbol=request.symbol,
            interval=request.interval,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Add mode information
        result["mode"] = "codeact" if CODEACT_AVAILABLE else "simple"
        
        # Check for errors
        if "error" in result:
            logger.error(f"Analysis error: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        # Ensure all values are JSON serializable
        import json
        try:
            # Test JSON serialization
            json.dumps(result)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization issue, cleaning result: {e}")
            # Clean up non-serializable values
            result = _clean_for_json(result)
        
        logger.info(f"Analysis completed successfully for {request.symbol} (mode: {result['mode']})")
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _clean_for_json(obj):
    """Recursively clean object for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_for_json(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        return str(obj)
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict() if isinstance(obj, pd.Series) else obj.to_dict('records')
    else:
        return obj


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False
    )

