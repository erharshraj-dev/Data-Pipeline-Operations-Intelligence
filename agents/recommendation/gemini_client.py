import json
import logging
import os
import time

logger = logging.getLogger(__name__)


class GeminiUnavailableError(Exception):
    """
    Raised whenever a usable Gemini response could not be
    obtained — missing SDK, missing API key, a request
    failure/timeout after exhausting retries, or a response
    that is not parseable JSON after exhausting retries. The
    Recommendation Agent catches this and falls back to the
    deterministic fallback recommendation; it never propagates
    as an unhandled crash.
    """
    pass


class GeminiClient:
    """
    ==========================================================
    Gemini Client

    Responsibility:
        Call the Gemini API (via the official Google
        Generative AI SDK) with a prepared prompt and return
        the parsed JSON recommendation. Handles missing SDK,
        missing API key, request failures, timeouts, and
        invalid JSON responses, with one configurable retry.

    Input:
        Prompt String

    Output:
        Parsed JSON Dictionary (raises GeminiUnavailableError
        if no usable response could be obtained)

    DOES NOT
    --------
    - Build the prompt
    - Validate the recommendation's business fields (that is
      the Recommendation Validator's job — this only confirms
      the response is parseable JSON)
    - Ever read the API key from anywhere but the environment
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        gemini_config = self.rule_engine.get_gemini_config()

        self.model_name = gemini_config.get("model", "gemini-2.5-flash")

        self.temperature = gemini_config.get("temperature", 0.2)

        self.max_output_tokens = gemini_config.get(
            "max_output_tokens", 512
        )

        self.timeout_seconds = gemini_config.get("timeout_seconds", 20)

        self.max_retries = gemini_config.get("max_retries", 1)

        self.api_key = os.getenv("GEMINI_API_KEY")

        if self.api_key:
            self.api_key = self.api_key.strip()
            if self.api_key in ("", "<API_KEY>", '"<API_KEY>"'):
                self.api_key = None

        self._model = None
        self.quota_exceeded = False

        if not self.api_key:

            logger.warning(
                "GEMINI_API_KEY is not set — Gemini Client will be "
                "unavailable and every recommendation will use the "
                "deterministic fallback path."
            )

        logger.info("Gemini Client Ready.")

    # =====================================================
    # LAZY MODEL INITIALIZATION
    #
    # google-generativeai is imported here, not at module
    # level, so the rest of the Recommendation Agent still
    # works (via the fallback path) in environments where the
    # SDK is not installed.
    # =====================================================

    def _get_model(self):

        if self._model is not None:

            return self._model

        if not self.api_key:

            raise GeminiUnavailableError("GEMINI_API_KEY is not set.")

        try:

            import google.generativeai as genai

        except ImportError as error:

            raise GeminiUnavailableError(
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

        if getattr(self, "quota_exceeded", False):
            raise GeminiUnavailableError("Gemini API quota exceeded in a previous call. Failing fast.")

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

                return self._parse_response(response.text)

            except GeminiUnavailableError:

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
                if "quota" in err_msg or "429" in err_msg or "limit" in err_msg:
                    self.quota_exceeded = True
                    raise GeminiUnavailableError(f"Gemini API quota exceeded: {error}")

                logger.warning(
                    f"Gemini API call failed on attempt "
                    f"{attempt}/{attempts}: {error}"
                )

            if attempt < attempts:

                time.sleep(0.5)

        raise GeminiUnavailableError(
            f"Gemini did not return a usable response after "
            f"{attempts} attempt(s): {last_error}"
        )
