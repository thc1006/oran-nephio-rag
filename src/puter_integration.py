"""
Puter.js Integration Module
Implements Anthropic Claude access exclusively through Puter.js browser API
Following: https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/
"""

import logging
import os
import tempfile
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

# Only import Selenium if not in mock mode
API_MODE = os.getenv("API_MODE", "browser")

if API_MODE != "mock":
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        from webdriver_manager.chrome import ChromeDriverManager

        SELENIUM_AVAILABLE = True
    except ImportError as e:
        SELENIUM_AVAILABLE = False
        logger = logging.getLogger(__name__)
        logger.warning(f"Selenium dependencies not available: {e}")
else:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class PuterClaudeAdapter:
    """
    Proper Puter.js Claude integration using browser automation
    Complies with constraint: https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/
    """

    AVAILABLE_MODELS = ["claude-sonnet-4", "claude-opus-4", "claude-sonnet-3.7", "claude-sonnet-3.5"]

    def __init__(self, model: str = "claude-sonnet-4", headless: bool = True) -> None:
        """
        Initialize Puter.js adapter with browser automation

        Args:
            model: Claude model to use
            headless: Whether to run browser in headless mode
        """
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model} not supported. Available: {self.AVAILABLE_MODELS}")

        self.model = model
        self.headless = headless
        self.driver: Optional[Any] = None  # webdriver.Chrome type
        self.mock_mode = API_MODE == "mock"

        if self.mock_mode:
            logger.info("Running in mock mode - browser initialization skipped")
        else:
            if not SELENIUM_AVAILABLE:
                raise RuntimeError(
                    "Selenium dependencies required for browser mode but not available. "
                    "Install with: pip install selenium webdriver-manager"
                )
            self._html_template = self._create_html_template()

    def _create_html_template(self) -> str:
        """Create HTML template with Puter.js integration"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>O-RAN Nephio RAG - Puter.js Integration</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        #output {{ border: 1px solid #ccc; padding: 10px; min-height: 200px; margin-top: 10px; }}
        .status {{ color: #666; font-style: italic; }}
        .error {{ color: red; }}
        .success {{ color: green; }}
    </style>
</head>
<body>
    <h1>O-RAN × Nephio RAG System</h1>
    <h2>Puter.js Claude Integration</h2>
    <div id="status" class="status">Ready for queries...</div>
    <div id="output"></div>
    
    <script>
        // Global variables for communication with Python
        window.ragResponse = null;
        window.ragError = null;
        window.ragProcessing = false;
        
        // Puter.js Claude integration function
        async function queryClaudeViaPuter(prompt, model = '{self.model}') {{
            try {{
                window.ragProcessing = true;
                window.ragResponse = null;
                window.ragError = null;
                
                document.getElementById('status').textContent = `Querying Claude ${{model}}...`;
                document.getElementById('status').className = 'status';
                
                console.log('Sending query to Claude via Puter.js:', prompt);
                
                // Use Puter.js API as specified in the tutorial
                const response = await puter.ai.chat(prompt, {{
                    model: model
                }});
                
                console.log('Received response:', response);
                
                // Extract text content from response
                let responseText = '';
                if (response && response.message && response.message.content) {{
                    responseText = response.message.content[0].text;
                }} else if (response && response.text) {{
                    responseText = response.text;
                }} else if (typeof response === 'string') {{
                    responseText = response;
                }} else {{
                    responseText = JSON.stringify(response);
                }}
                
                // Store response for Python to retrieve
                window.ragResponse = {{
                    answer: responseText,
                    model: model,
                    timestamp: new Date().toISOString(),
                    success: true
                }};
                
                // Update UI
                document.getElementById('output').innerHTML = 
                    '<h3>Response:</h3><p>' + responseText.replace(/\\n/g, '<br>') + '</p>';
                document.getElementById('status').textContent = 'Query completed successfully';
                document.getElementById('status').className = 'status success';
                
                window.ragProcessing = false;
                return window.ragResponse;
                
            }} catch (error) {{
                console.error('Puter.js query failed:', error);
                
                window.ragError = {{
                    error: error.message || 'Unknown error',
                    timestamp: new Date().toISOString()
                }};
                
                document.getElementById('output').innerHTML = 
                    '<h3>Error:</h3><p class="error">' + error.message + '</p>';
                document.getElementById('status').textContent = 'Query failed';
                document.getElementById('status').className = 'status error';
                
                window.ragProcessing = false;
                throw error;
            }}
        }}
        
        // Streaming query function (for long responses)
        async function streamClaudeViaPuter(prompt, model = '{self.model}') {{
            try {{
                window.ragProcessing = true;
                document.getElementById('status').textContent = `Streaming from Claude ${{model}}...`;
                
                const response = await puter.ai.chat(prompt, {{
                    model: model,
                    stream: true
                }});
                
                let fullResponse = '';
                document.getElementById('output').innerHTML = '<h3>Streaming Response:</h3><div id="stream-content"></div>';
                const streamDiv = document.getElementById('stream-content');
                
                for await (const part of response) {{
                    if (part && part.text) {{
                        fullResponse += part.text;
                        streamDiv.innerHTML = fullResponse.replace(/\\n/g, '<br>');
                    }}
                }}
                
                window.ragResponse = {{
                    answer: fullResponse,
                    model: model,
                    timestamp: new Date().toISOString(),
                    success: true,
                    streamed: true
                }};
                
                window.ragProcessing = false;
                return window.ragResponse;
                
            }} catch (error) {{
                console.error('Streaming query failed:', error);
                window.ragError = {{ error: error.message }};
                window.ragProcessing = false;
                throw error;
            }}
        }}
        
        // Initialize Puter.js
        console.log('Puter.js integration initialized');
        document.getElementById('status').textContent = 'Puter.js loaded - Ready for queries';
    </script>
</body>
</html>
        """

    @contextmanager
    def _browser_session(self) -> Generator[None, None, None]:
        """Context manager for browser session"""
        try:
            # Setup Chrome options
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            if self.driver is not None:
                self.driver.implicitly_wait(10)

            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
                f.write(self._html_template)
                html_file = f.name

            # Load the HTML page
            if self.driver is not None:
                self.driver.get(f"file://{html_file}")

            # Wait for Puter.js to load
            if self.driver is not None:
                WebDriverWait(self.driver, 20).until(
                    lambda driver: driver.execute_script("return typeof puter !== 'undefined'")
                )

            logger.info("Puter.js browser session initialized successfully")
            yield

        except Exception as e:
            logger.error(f"Browser session error: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
            # Clean up temp file
            try:
                os.unlink(html_file)
            except:
                pass

    def query(self, prompt: str, stream: bool = False, timeout: int = 60) -> Dict[str, Any]:
        """
        Query Claude via Puter.js browser integration or mock response

        Args:
            prompt: The question/prompt to send to Claude
            stream: Whether to use streaming response
            timeout: Maximum wait time in seconds

        Returns:
            Dict containing response, model info, and metadata
        """
        if self.mock_mode:
            return self._mock_query(prompt, stream)

        with self._browser_session():
            try:
                # Execute the query via JavaScript
                js_function = "streamClaudeViaPuter" if stream else "queryClaudeViaPuter"

                logger.info(f"Executing Puter.js query with model {self.model}")

                # Start the query
                if self.driver is not None:
                    self.driver.execute_script(
                        f"""
                        window.{js_function}(arguments[0], arguments[1])
                            .then(result => console.log('Query completed:', result))
                            .catch(error => console.error('Query failed:', error));
                    """,
                        prompt,
                        self.model,
                    )

                # Wait for completion
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Check if processing is complete
                    if self.driver is not None:
                        is_processing = self.driver.execute_script("return window.ragProcessing")

                        if not is_processing:
                            # Check for response
                            response = self.driver.execute_script("return window.ragResponse")
                            error = self.driver.execute_script("return window.ragError")

                        if response:
                            logger.info("Successfully received response from Puter.js")
                            return {
                                "answer": response["answer"],
                                "model": response["model"],
                                "timestamp": response["timestamp"],
                                "success": True,
                                "adapter_type": "puter_js_browser",
                                "query_time": time.time() - start_time,
                                "streamed": response.get("streamed", False),
                            }

                        if error:
                            logger.error(f"Puter.js query failed: {error['error']}")
                            return {
                                "error": error["error"],
                                "success": False,
                                "adapter_type": "puter_js_browser",
                                "timestamp": error["timestamp"],
                            }

                    time.sleep(0.5)  # Poll every 500ms

                # Timeout occurred
                logger.error(f"Puter.js query timed out after {timeout} seconds")
                return {
                    "error": f"Query timed out after {timeout} seconds",
                    "success": False,
                    "adapter_type": "puter_js_browser",
                }

            except Exception as e:
                logger.error(f"Puter.js query execution error: {e}")
                return {
                    "error": f"Query execution failed: {str(e)}",
                    "success": False,
                    "adapter_type": "puter_js_browser",
                }

    def _mock_query(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """
        Mock query response for testing without browser
        """
        logger.info(f"Mock query: {prompt[:100]}...")

        # Generate a basic mock response
        mock_response = f"Mock response to: '{prompt[:50]}...'"
        if "nephio" in prompt.lower():
            mock_response = "This is a mock response about Nephio network function orchestration."
        elif "oran" in prompt.lower() or "o-ran" in prompt.lower():
            mock_response = "This is a mock response about O-RAN architecture and components."

        return {
            "answer": mock_response,
            "model": self.model,
            "timestamp": time.time(),
            "success": True,
            "adapter_type": "puter_js_mock",
            "query_time": 0.1,
            "streamed": stream,
        }

    def is_available(self) -> bool:
        """Check if Puter.js integration is available"""
        if self.mock_mode:
            return True

        if not SELENIUM_AVAILABLE:
            return False

        try:
            with self._browser_session():
                # Test if Puter.js is loaded
                if self.driver is not None:
                    puter_available = self.driver.execute_script("return typeof puter !== 'undefined'")
                    ai_available = self.driver.execute_script("return typeof puter.ai !== 'undefined'")
                    return bool(puter_available and ai_available)
                return False
        except Exception as e:
            logger.error(f"Availability check failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available Claude models"""
        return self.AVAILABLE_MODELS.copy()

    def get_info(self) -> Dict[str, Any]:
        """Get adapter information"""
        return {
            "adapter_type": "PuterClaudeAdapter",
            "model": self.model,
            "available_models": self.AVAILABLE_MODELS,
            "integration_method": "mock" if self.mock_mode else "browser_automation",
            "tutorial_source": "https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/",
            "headless_mode": self.headless,
            "mock_mode": self.mock_mode,
            "selenium_available": SELENIUM_AVAILABLE,
        }


class PuterRAGManager:
    """
    RAG system manager using Puter.js Claude integration
    Replaces the old LLMManager with constraint-compliant implementation
    """

    def __init__(self, model: str = "claude-sonnet-4", headless: bool = True) -> None:
        """
        Initialize RAG manager with Puter.js integration

        Args:
            model: Claude model to use
            headless: Whether to run browser in headless mode
        """
        # Check API_MODE before initializing browser components
        if API_MODE == "mock":
            logger.info("Running in mock mode - browser initialization skipped")

        try:
            self.adapter = PuterClaudeAdapter(model=model, headless=headless)
            logger.info(f"PuterRAGManager initialized with model: {model} (mode: {API_MODE})")
        except RuntimeError as e:
            if "Selenium dependencies" in str(e):
                logger.error(f"Browser initialization failed: {e}")
                logger.info("Consider setting API_MODE=mock for browser-free operation")
                raise
            else:
                raise

    def query(self, prompt: str, context: str = "", **kwargs) -> Dict[str, Any]:
        """
        Query with RAG context using Puter.js

        Args:
            prompt: User question
            context: Retrieved document context
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        # Combine context and prompt for better responses
        if context:
            enhanced_prompt = f"""Based on the following context about O-RAN and Nephio technologies, please answer the question:

CONTEXT:
{context}

QUESTION:
{prompt}

Please provide a comprehensive answer based primarily on the provided context, and indicate if you're drawing from general knowledge when the context doesn't fully address the question."""
        else:
            enhanced_prompt = f"""Please answer this question about O-RAN and Nephio technologies:

{prompt}"""

        return self.adapter.query(enhanced_prompt, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        adapter_info = self.adapter.get_info()
        return {
            "integration_type": "puter_js_mock" if API_MODE == "mock" else "puter_js_browser",
            "adapter_available": self.adapter.is_available(),
            "adapter_info": adapter_info,
            "constraint_compliant": True,
            "tutorial_source": "https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/",
            "api_mode": API_MODE,
            "selenium_available": SELENIUM_AVAILABLE,
        }


# Factory functions for backward compatibility
def create_puter_rag_manager(model: str = "claude-sonnet-4", headless: bool = True) -> PuterRAGManager:
    """Create a Puter.js RAG manager"""
    return PuterRAGManager(model=model, headless=headless)


def quick_puter_query(prompt: str, model: str = "claude-sonnet-4") -> str:
    """Quick query using Puter.js integration"""
    manager = create_puter_rag_manager(model=model)
    result = manager.query(prompt)

    if result.get("success"):
        answer = result.get("answer", "No answer received")
        return str(answer) if answer is not None else "No answer received"
    else:
        error = result.get("error", "Unknown error")
        return f"Error: {str(error)}"
