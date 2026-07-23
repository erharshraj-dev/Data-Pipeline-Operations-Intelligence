import logging
import os

logger = logging.getLogger(__name__)


class LLMConfig:
    """
    ==========================================================
    LLM Config

    Responsibility:
        Single source of truth for every setting the Multi-LLM
        Selection Agent and its provider clients (Gemini, Grok,
        Ollama) need — model names, timeouts, retry counts,
        the provider fallback order, and API credentials. API
        keys are read only from environment variables; nothing
        secret is ever hardcoded here or in any client that
        consumes this config.

    Input:
        None (reads process environment variables at
        construction time)

    Output:
        LLM Config object exposing one accessor per provider
        plus the configured selection order

    DOES NOT
    --------
    - Call any LLM
    - Decide which provider to use for a given recommendation
      (that is the Multi-LLM Selection Agent's responsibility)
    - Validate or parse any LLM response
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Loading LLM Config...")

        self.selection_order = self._load_selection_order()

        self.gemini_config = self._load_gemini_config()

        self.grok_config = self._load_grok_config()

        self.ollama_config = self._load_ollama_config()

        logger.info("LLM Config loaded successfully.")

    # =====================================================
    # ENVIRONMENT HELPERS
    #
    # A key is only considered "set" if it is non-empty after
    # stripping and is not an obvious unfilled placeholder left
    # over from a .env.example file.
    # =====================================================

    def _clean_secret(self, raw_value):

        if raw_value is None:

            return None

        value = raw_value.strip()

        if value in ("", "<API_KEY>", '"<API_KEY>"', "<GROK_API_KEY>",
                     "<GEMINI_API_KEY>"):

            return None

        return value

    def _env_int(self, name, default):

        raw_value = os.getenv(name)

        if raw_value is None or raw_value.strip() == "":

            return default

        try:

            return int(raw_value)

        except ValueError:

            logger.warning(
                f"Environment variable {name}={raw_value!r} is not a "
                f"valid integer. Using default: {default}"
            )

            return default

    def _env_float(self, name, default):

        raw_value = os.getenv(name)

        if raw_value is None or raw_value.strip() == "":

            return default

        try:

            return float(raw_value)

        except ValueError:

            logger.warning(
                f"Environment variable {name}={raw_value!r} is not a "
                f"valid float. Using default: {default}"
            )

            return default

    # =====================================================
    # SELECTION ORDER
    #
    # Overridable via LLM_SELECTION_ORDER, a comma-separated
    # list e.g. "gemini,grok,ollama". Falls back to the
    # documented default priority: Gemini, then Grok, then
    # Ollama. The Multi-LLM Selection Agent always falls back
    # to the deterministic recommendation after every provider
    # in this list has been tried.
    # =====================================================

    def _load_selection_order(self):

        raw_order = os.getenv("LLM_SELECTION_ORDER")

        default_order = ["gemini", "grok", "ollama"]

        if not raw_order or not raw_order.strip():

            return default_order

        parsed_order = [
            provider.strip().lower()
            for provider in raw_order.split(",")
            if provider.strip()
        ]

        return parsed_order or default_order

    # =====================================================
    # GEMINI CONFIG
    # =====================================================

    def _load_gemini_config(self):

        api_key = self._clean_secret(os.getenv("GEMINI_API_KEY"))

        if not api_key:

            logger.warning(
                "GEMINI_API_KEY is not set — Gemini will be skipped by "
                "the Multi-LLM Selection Agent."
            )

        return {

            "api_key": api_key,

            "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),

            "temperature": self._env_float("GEMINI_TEMPERATURE", 0.2),

            "max_output_tokens": self._env_int(
                "GEMINI_MAX_OUTPUT_TOKENS", 512
            ),

            "timeout_seconds": self._env_int("GEMINI_TIMEOUT_SECONDS", 20),

            "max_retries": self._env_int("GEMINI_MAX_RETRIES", 2),

        }

    # =====================================================
    # GROK CONFIG
    # =====================================================

    def _load_grok_config(self):

        api_key = self._clean_secret(os.getenv("GROK_API_KEY"))

        if not api_key:

            logger.warning(
                "GROK_API_KEY is not set — Grok will be skipped by the "
                "Multi-LLM Selection Agent."
            )

        return {

            "api_key": api_key,

            "base_url": os.getenv(
                "GROK_BASE_URL", "https://api.x.ai/v1/chat/completions"
            ),

            "model": os.getenv("GROK_MODEL", "grok-4-latest"),

            "temperature": self._env_float("GROK_TEMPERATURE", 0.2),

            "max_output_tokens": self._env_int(
                "GROK_MAX_OUTPUT_TOKENS", 512
            ),

            "timeout_seconds": self._env_int("GROK_TIMEOUT_SECONDS", 20),

            "max_retries": self._env_int("GROK_MAX_RETRIES", 2),

        }

    # =====================================================
    # OLLAMA CONFIG
    #
    # Ollama is a local model server — it has no API key, only
    # a reachable URL, so it is treated as available whenever
    # OLLAMA_BASE_URL resolves (default: local daemon).
    # =====================================================

    def _load_ollama_config(self):

        return {

            "base_url": os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            ),

            "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),

            "temperature": self._env_float("OLLAMA_TEMPERATURE", 0.2),

            "timeout_seconds": self._env_int("OLLAMA_TIMEOUT_SECONDS", 30),

            "max_retries": self._env_int("OLLAMA_MAX_RETRIES", 1),

        }

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_selection_order(self):

        return list(self.selection_order)

    def get_gemini_config(self):

        return dict(self.gemini_config)

    def get_grok_config(self):

        return dict(self.grok_config)

    def get_ollama_config(self):

        return dict(self.ollama_config)

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("LLM Config Ready.")

        logger.info(f"Selection Order : {self.selection_order}")

        return True
