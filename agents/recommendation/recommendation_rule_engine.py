import yaml
import logging

logger = logging.getLogger(__name__)


class RecommendationRuleEngine:
    """
    ==========================================================
    Recommendation Rule Engine

    Responsibility:
        Load Recommendation Agent configuration and expose it
        to every other Recommendation Agent module. Single
        source of truth for priority rules, impact/recovery
        mappings, automation and human-approval rules,
        knowledge retrieval settings, Gemini client settings,
        validation rules, fallback content, and agent metadata.

    Input:
        Path to config/recommendation_rules.yaml

    Output:
        Recommendation Rule Configuration

    DOES NOT
    --------
    - Build recommendation context
    - Calculate priority
    - Call Gemini
    - Validate or build the Recommendation Object
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file):

        self.config_file = config_file

        self.agent_config = {}
        self.priority_rules_config = {}
        self.impact_mapping = {}
        self.recovery_time_mapping = {}
        self.automation_rules = {}
        self.human_approval_rules = {}
        self.knowledge_retrieval_config = {}
        self.gemini_config = {}
        self.grok_config = {}
        self.ollama_config = {}
        self.llm_selection_config = {}
        self.validation_config = {}
        self.fallback_config = {}

        self.load_config()

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def load_config(self):

        logger.info("Loading Recommendation Rule Configuration...")

        with open(self.config_file, "r") as file:

            config = yaml.safe_load(file)

        self.agent_config = config.get("agent", {})

        self.priority_rules_config = config.get("priority_rules", {})

        self.impact_mapping = config.get("impact_mapping", {})

        self.recovery_time_mapping = config.get(
            "recovery_time_mapping", {}
        )

        self.automation_rules = config.get("automation_rules", {})

        self.human_approval_rules = config.get(
            "human_approval_rules", {}
        )

        self.knowledge_retrieval_config = config.get(
            "knowledge_retrieval", {}
        )

        self.gemini_config = config.get("gemini", {})

        self.grok_config = config.get("grok", {})

        self.ollama_config = config.get("ollama", {})

        self.llm_selection_config = config.get("llm_selection", {})

        self.validation_config = config.get("validation", {})

        self.fallback_config = config.get("fallback", {})

        logger.info(
            "Recommendation Rule Configuration loaded successfully."
        )

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Recommendation Rule Engine Ready.")

        return True

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_agent_version(self):

        return self.agent_config.get("version", "1.0")

    def get_priority_rules(self):

        return self.priority_rules_config.get("rules", [])

    def get_default_priority(self):

        return self.priority_rules_config.get("default_priority", "LOW")

    def get_impact_mapping(self):

        return self.impact_mapping

    def get_recovery_time_mapping(self):

        return self.recovery_time_mapping

    def get_automation_rules(self):

        return self.automation_rules

    def get_human_approval_rules(self):

        return self.human_approval_rules

    def get_knowledge_retrieval_config(self):

        return self.knowledge_retrieval_config

    def get_gemini_config(self):

        return self.gemini_config

    def get_grok_config(self):

        return self.grok_config

    def get_ollama_config(self):

        return self.ollama_config

    def get_llm_selection_config(self):

        return self.llm_selection_config

    def get_validation_config(self):

        return self.validation_config

    def get_fallback_config(self):

        return self.fallback_config
