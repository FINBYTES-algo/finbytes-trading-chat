"""
CodeAct API Client
Connects to CodeAct's OpenAI-compatible API and Jupyter execution engine.
"""
import requests
import json
import logging
from typing import Dict, Optional, List
import os

logger = logging.getLogger(__name__)


class CodeActAPIClient:
    """
    Client for interacting with CodeAct via OpenAI-compatible API.
    """
    
    def __init__(
        self,
        api_base: str = None,
        model_name: str = None,
        jupyter_url: str = None
    ):
        """
        Initialize CodeAct API client.
        
        Args:
            api_base: Base URL for OpenAI-compatible API (e.g., http://localhost:8080/v1)
            model_name: Model name (e.g., xingyaoww/CodeActAgent-Mistral-7b-v0.1)
            jupyter_url: Jupyter execution engine URL (e.g., http://localhost:8081/execute)
        """
        self.api_base = api_base or os.getenv("CODEACT_API_BASE", "http://localhost:8080/v1")
        self.model_name = model_name or os.getenv("CODEACT_MODEL_NAME", "xingyaoww/CodeActAgent-Mistral-7b-v0.1")
        self.jupyter_url = jupyter_url or os.getenv("CODEACT_JUPYTER_URL", "http://localhost:8081/execute")
        
        # Ensure API base doesn't end with /
        if self.api_base.endswith('/'):
            self.api_base = self.api_base[:-1]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict:
        """
        Send chat completion request to CodeAct API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            API response
        """
        url = f"{self.api_base}/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"CodeAct API request failed: {e}")
            raise
    
    def execute_code(self, code: str, session_id: str = None) -> Dict:
        """
        Execute code via Jupyter execution engine.
        
        Args:
            code: Python code to execute
            session_id: Session ID for maintaining state
        
        Returns:
            Execution result
        """
        url = f"{self.jupyter_url}"
        
        payload = {
            "code": code,
            "session_id": session_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Code execution failed: {e}")
            raise
    
    def run_interactive(
        self,
        user_query: str,
        system_prompt: str = None,
        max_iterations: int = 10
    ) -> Dict:
        """
        Run an interactive session with CodeAct.
        Handles the conversation loop where CodeAct generates code and executes it.
        
        Args:
            user_query: User's natural language query
            system_prompt: System prompt for the agent
            max_iterations: Maximum number of iterations
        
        Returns:
            Final result
        """
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant that can execute Python code.
When you need to perform calculations or analysis, write Python code and it will be executed.
You can see the results and iterate based on them."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        session_id = None
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")
            
            # Get response from CodeAct
            response = self.chat(messages)
            
            # Extract assistant's message
            assistant_message = response['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Check if CodeAct wants to execute code
            # CodeAct typically wraps code in ```python blocks
            if "```python" in assistant_message or "```" in assistant_message:
                # Extract code
                code = self._extract_code(assistant_message)
                
                if code:
                    logger.info(f"Executing code: {code[:100]}...")
                    
                    # Execute code
                    exec_result = self.execute_code(code, session_id)
                    
                    # Extract session ID if provided
                    if 'session_id' in exec_result:
                        session_id = exec_result['session_id']
                    
                    # Add execution result to conversation
                    result_text = self._format_execution_result(exec_result)
                    messages.append({
                        "role": "user",
                        "content": f"Code execution result:\n{result_text}"
                    })
                else:
                    # No code to execute, return final result
                    break
            else:
                # No code execution needed, return final result
                break
        
        return {
            "final_response": assistant_message,
            "messages": messages,
            "iterations": iteration
        }
    
    def _extract_code(self, text: str) -> Optional[str]:
        """Extract Python code from markdown code blocks."""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        return None
    
    def _format_execution_result(self, result: Dict) -> str:
        """Format execution result for display."""
        if 'error' in result:
            return f"Error: {result['error']}"
        elif 'output' in result:
            return str(result['output'])
        elif 'result' in result:
            return str(result['result'])
        else:
            return json.dumps(result, indent=2)


def test_connection(api_base: str = None, model_name: str = None) -> bool:
    """
    Test connection to CodeAct API.
    
    Args:
        api_base: API base URL
        model_name: Model name
    
    Returns:
        True if connection successful
    """
    try:
        client = CodeActAPIClient(api_base=api_base, model_name=model_name)
        response = client.chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' if you can hear me."}
        ])
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

