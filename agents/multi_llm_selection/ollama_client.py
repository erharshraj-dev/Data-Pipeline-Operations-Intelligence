import json
import logging
import time

import requests

logger = logging.getLogger(__name__)


class OllamaProviderError(Exception):
    """
    Raised whenever a usable Ollama response could not be
    obtained — the local Ollama daemon unreachable, a request
    failure/timeout after exhausting retries, or a response
    that is not parseable JSON after exhausting retries. The
    Multi-LLM Selection Agent catches this and falls back to
    the deterministic recommendation already produced by the
    Recommendation Agent; it never propagates as an unhandled
    crash.
    """
    pass


class OllamaClient:
    """
    ==========================================================
    Ollama Client (Multi-LLM Selection Agent)

    Responsibility:
        Call a local Ollama server (llama3.2:3b by default)
        with a prepared enhancement prompt and return the
        parsed JSON response. This is the last LLM tried before
        falling back to the deterministic recommendation, so it
        is expected to be reachable even when Gemini and Grok
        are not (no external network dependency, no API key).

    Input:
        Prompt String

    Output:
        Parsed JSON Dictionary (raises OllamaProviderError if
        no usable response could be obtained)

    DOES NOT
    --------
    - Build the prompt
    - Decide whether Ollama should be tried at all (that is the
      Multi-LLM Selection Agent's responsibility — it is only
      reached after Gemini and Grok have already failed)
    - Validate the response's business fields (that is the
      LLM Response Parser's job — this only confirms the
      response is parseable JSON)
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, llm_config):

        self.llm_config = llm_config

        ollama_config = self.llm_config.get_ollama_config()

        self.base_url = ollama_config.get(
            "base_url", "http://localhost:11434"
        )

        self.model_name = ollama_config.get("model", "llama3.2:3b")

        self.temperature = ollama_config.get("temperature", 0.2)

        # Default to 90 seconds timeout for demo stability on CPU
        self.timeout_seconds = max(ollama_config.get("timeout_seconds", 30), 90)

        self.max_retries = ollama_config.get("max_retries", 1)

        self.generate_endpoint = f"{self.base_url.rstrip('/')}/api/generate"

        logger.info("Ollama Client Ready.")

    # =====================================================
    # PARSE RESPONSE TEXT AS JSON
    #
    # The prompt instructs Ollama to return only JSON, but this
    # defensively strips markdown code fences in case the model
    # wraps its response in ```json ... ``` anyway.
    # =====================================================

    def _parse_response(self, response_text):

        text = (response_text or "").strip()

        # Find the outermost JSON block
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace+1]

        # 1. Try standard JSON parsing
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2. Try Python literal evaluation by converting JSON constants to Python constants
        try:
            py_text = text.replace("true", "True").replace("false", "False").replace("null", "None")
            import ast
            parsed = ast.literal_eval(py_text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        # 3. Try replacing single quotes wrapping elements with double quotes
        try:
            import re
            cleaned_text = re.sub(r"'(.*?)'", r'"\1"', text)
            return json.loads(cleaned_text)
        except Exception:
            pass

        # Fallback to standard json.loads to raise standard JSON decode error if unrepairable
        return json.loads(text)

    # =====================================================
    # GENERATE
    # =====================================================

    def generate(self, prompt):

        payload = {

            "model": self.model_name,

            "prompt": prompt,

            "stream": False,

            "options": {
                "temperature": self.temperature
            }

        }

        last_error = None

        attempts = self.max_retries + 1

        for attempt in range(1, attempts + 1):

            try:

                response = requests.post(

                    self.generate_endpoint,

                    json=payload,

                    timeout=self.timeout_seconds

                )

                response.raise_for_status()

                body = response.json()

                content = body.get("response", "")

                parsed = self._parse_response(content)

                parsed["generated_by"] = "ollama"

                return parsed

            except requests.exceptions.Timeout as error:

                last_error = error

                logger.warning(
                    f"Ollama call timed out on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            except requests.exceptions.ConnectionError as error:

                last_error = error

                logger.warning(
                    f"Ollama server unreachable on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            except (requests.exceptions.RequestException,
                    json.JSONDecodeError, ValueError) as error:

                last_error = error

                logger.warning(
                    f"Ollama call failed on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            if attempt < attempts:

                time.sleep(0.5)

        raise OllamaProviderError(
            f"Ollama did not return a usable response after "
            f"{attempts} attempt(s): {last_error}"
        )
