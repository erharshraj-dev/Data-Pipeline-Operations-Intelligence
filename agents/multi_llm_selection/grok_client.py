import json
import logging
import time

import requests

logger = logging.getLogger(__name__)


class GrokProviderError(Exception):
    """
    Raised whenever a usable Grok response could not be
    obtained — missing API key, authentication failure, rate
    limiting, a request failure/timeout after exhausting
    retries, or a response that is not parseable JSON after
    exhausting retries. The Multi-LLM Selection Agent catches
    this and moves on to Ollama; it never propagates to the
    Recommendation Agent.
    """
    pass


class GrokClient:
    """
    ==========================================================
    Grok Client (Multi-LLM Selection Agent)

    Responsibility:
        Call the Grok (xAI) chat completions REST API with a
        prepared enhancement prompt and return the parsed JSON
        response. Handles missing API key, authentication
        errors, rate limiting, timeouts, and invalid JSON
        responses, retrying according to LLMConfig.

    Input:
        Prompt String

    Output:
        Parsed JSON Dictionary (raises GrokProviderError if no
        usable response could be obtained)

    DOES NOT
    --------
    - Build the prompt
    - Decide whether Grok should be tried at all (that is the
      Multi-LLM Selection Agent's responsibility — it is only
      reached after Gemini has already failed)
    - Validate the response's business fields (that is the
      LLM Response Parser's job — this only confirms the
      response is parseable JSON)
    - Ever read the API key from anywhere but LLMConfig /
      the environment
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, llm_config):

        self.llm_config = llm_config

        grok_config = self.llm_config.get_grok_config()

        self.api_key = grok_config.get("api_key")

        self.base_url = grok_config.get(
            "base_url", "https://api.x.ai/v1/chat/completions"
        )

        self.model_name = grok_config.get("model", "grok-4-latest")

        self.temperature = grok_config.get("temperature", 0.2)

        self.max_output_tokens = grok_config.get(
            "max_output_tokens", 512
        )

        self.timeout_seconds = grok_config.get("timeout_seconds", 20)

        self.max_retries = grok_config.get("max_retries", 2)

        logger.info("Grok Client Ready.")

    # =====================================================
    # PARSE RESPONSE TEXT AS JSON
    #
    # The prompt instructs Grok to return only JSON, but this
    # defensively strips markdown code fences in case the
    # model wraps its response in ```json ... ``` anyway.
    # =====================================================

    def _parse_response(self, response_text):

        text = (response_text or "").strip()

        if text.startswith("```"):

            text = text.strip("`")

            if text.lower().startswith("json"):

                text = text[4:]

            text = text.strip()

        return json.loads(text)

    # =====================================================
    # GENERATE
    # =====================================================

    def generate(self, prompt):

        if not self.api_key:

            raise GrokProviderError("GROK_API_KEY is not set.")

        headers = {

            "Authorization": f"Bearer {self.api_key}",

            "Content-Type": "application/json"

        }

        payload = {

            "model": self.model_name,

            "temperature": self.temperature,

            "max_tokens": self.max_output_tokens,

            "messages": [
                {"role": "user", "content": prompt}
            ]

        }

        last_error = None

        attempts = self.max_retries + 1

        for attempt in range(1, attempts + 1):

            try:

                response = requests.post(

                    self.base_url,

                    headers=headers,

                    json=payload,

                    timeout=self.timeout_seconds

                )

                if response.status_code in (401, 403):

                    raise GrokProviderError(
                        f"Grok authentication failed "
                        f"(HTTP {response.status_code}): {response.text}"
                    )

                if response.status_code == 429:

                    raise GrokProviderError(
                        f"Grok rate limit exceeded "
                        f"(HTTP {response.status_code}): {response.text}"
                    )

                response.raise_for_status()

                body = response.json()

                content = body["choices"][0]["message"]["content"]

                parsed = self._parse_response(content)

                parsed["generated_by"] = "grok"

                return parsed

            except GrokProviderError:

                # Authentication / rate-limit — retrying will
                # not help within this call, fail fast.
                raise

            except requests.exceptions.Timeout as error:

                last_error = error

                logger.warning(
                    f"Grok API call timed out on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            except (requests.exceptions.RequestException,
                    json.JSONDecodeError, KeyError, IndexError,
                    ValueError) as error:

                last_error = error

                logger.warning(
                    f"Grok API call failed on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            if attempt < attempts:

                time.sleep(0.5)

        raise GrokProviderError(
            f"Grok did not return a usable response after "
            f"{attempts} attempt(s): {last_error}"
        )
