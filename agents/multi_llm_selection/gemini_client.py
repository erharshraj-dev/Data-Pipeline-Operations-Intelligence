import json
import logging
import time

logger = logging.getLogger(__name__)


class GeminiProviderError(Exception):
    """
    Raised whenever a usable Gemini response could not be
    obtained — missing SDK, missing API key, a request
    failure/timeout after exhausting retries, or a response
    that is not parseable JSON after exhausting retries. The
    Multi-LLM Selection Agent catches this and moves on to the
    next provider in the selection order; it never propagates
    to the Recommendation Agent.
    """
    pass


class GeminiClient:
    """
    ==========================================================
    Gemini Client (Multi-LLM Selection Agent)

    Responsibility:
        Call the Gemini API (via the official Google
        Generative AI SDK) with a prepared enhancement prompt
        and return the parsed JSON response. Handles missing
        SDK, missing API key, request failures, timeouts, and
        invalid JSON responses, retrying according to
        LLMConfig.

    Input:
        Prompt String

    Output:
        Parsed JSON Dictionary (raises GeminiProviderError if
        no usable response could be obtained)

    DOES NOT
    --------
    - Build the prompt
    - Decide whether Gemini should be tried at all (that is
      the Multi-LLM Selection Agent's responsibility)
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

        gemini_config = self.llm_config.get_gemini_config()

        self.api_key = gemini_config.get("api_key")

        self.model_name = gemini_config.get("model", "gemini-2.5-flash")

        self.temperature = gemini_config.get("temperature", 0.2)

        self.max_output_tokens = gemini_config.get(
            "max_output_tokens", 512
        )

        self.timeout_seconds = gemini_config.get("timeout_seconds", 20)

        self.max_retries = gemini_config.get("max_retries", 2)

        self._model = None
        self.quota_exceeded = False

        logger.info("Multi-LLM Gemini Client Ready.")

    # =====================================================
    # LAZY MODEL INITIALIZATION
    #
    # google-generativeai is imported here, not at module
    # level, so the rest of the Multi-LLM Selection Agent
    # still works (falling through to Grok / Ollama /
    # deterministic) in environments where the SDK is not
    # installed.
    # =====================================================

    def _get_model(self):

        if self._model is not None:

            return self._model

        if not self.api_key:

            raise GeminiProviderError("GEMINI_API_KEY is not set.")

        try:

            import google.generativeai as genai

        except ImportError as error:

            raise GeminiProviderError(
                f"google-generativeai SDK is not installed: {error}"
            )

        genai.configure(api_key=self.api_key)

        self._model = genai.GenerativeModel(self.model_name)

        return self._model

    # =====================================================
    # PARSE RESPONSE TEXT AS JSON
    #
    # The prompt instructs Gemini to return only JSON, but
    # this defensively strips markdown code fences in case the
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

        if self.quota_exceeded:

            raise GeminiProviderError(
                "Gemini API quota exceeded in a previous call. "
                "Failing fast."
            )

        last_error = None

        attempts = self.max_retries + 1

        for attempt in range(1, attempts + 1):

            try:

                model = self._get_model()

                generation_config = {

                    "temperature": self.temperature,

                    "max_output_tokens": self.max_output_tokens

                }

                response = model.generate_content(

                    prompt,

                    generation_config=generation_config,

                    request_options={"timeout": self.timeout_seconds}

                )

                parsed = self._parse_response(response.text)

                parsed["generated_by"] = "gemini"

                return parsed

            except GeminiProviderError:

                # SDK missing / API key missing — retrying will
                # not help, fail fast.
                raise

            except (json.JSONDecodeError, ValueError) as error:

                last_error = error

                logger.warning(
                    f"Gemini response was not valid JSON on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            except Exception as error:

                last_error = error

                err_msg = str(error).lower()

                if "quota" in err_msg or "429" in err_msg or \
                        "limit" in err_msg:

                    self.quota_exceeded = True

                    raise GeminiProviderError(
                        f"Gemini API quota exceeded: {error}"
                    )

                logger.warning(
                    f"Gemini API call failed on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            if attempt < attempts:

                time.sleep(0.5)

        raise GeminiProviderError(
            f"Gemini did not return a usable response after "
            f"{attempts} attempt(s): {last_error}"
        )
