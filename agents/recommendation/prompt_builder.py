import logging

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    ==========================================================
    Prompt Builder

    Responsibility:
        Build the structured prompt sent to Gemini from the
        Behavior Summary, Risk Summary, Integrity Summary,
        Business Context, and Retrieved Knowledge. The prompt
        text itself lives entirely in
        config/prompt_template.txt — never hardcoded here.

    Input:
        Recommendation Context Dictionary, Retrieved Knowledge
        Dictionary

    Output:
        Prompt String

    DOES NOT
    --------
    - Calculate priority or impact
    - Retrieve knowledge
    - Call Gemini
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, template_file="config/prompt_template.txt"):

        self.template_file = template_file

        self.template = self._load_template()

        logger.info("Prompt Builder Ready.")

    # =====================================================
    # LOAD TEMPLATE
    # =====================================================

    def _load_template(self):

        with open(self.template_file, "r", encoding="utf-8") as file:

            return file.read()

    # =====================================================
    # FORMAT A VALUE FOR PROMPT INSERTION
    # =====================================================

    def _format_value(self, value):

        if value is None:

            return "Unknown"

        if isinstance(value, list):

            return ", ".join(str(item) for item in value) if value else "None"

        return str(value)

    # =====================================================
    # BUILD
    # =====================================================

    def build(self, context, retrieved_knowledge, base_candidate=None):

        fields = dict(context)

        fields.update(retrieved_knowledge)

        if base_candidate:

            fields.update(base_candidate)

        formatted_fields = {

            key: self._format_value(value)

            for key, value in fields.items()

        }

        try:

            return self.template.format(**formatted_fields)

        except KeyError as error:

            logger.warning(
                f"Prompt template references an unknown field: {error}. "
                "Falling back to safe substitution."
            )

            return self.template.format_map(
                _SafeMissingDict(formatted_fields)
            )


class _SafeMissingDict(dict):
    """
    Used only as a fallback if config/prompt_template.txt is
    edited to reference a field the context does not provide —
    substitutes "Unknown" instead of raising, so a template
    typo cannot crash the agent.
    """

    def __missing__(self, key):

        return "Unknown"
