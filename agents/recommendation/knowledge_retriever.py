import json
import logging
import os

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    ==========================================================
    Knowledge Retriever

    Responsibility:
        Retrieve relevant operational knowledge for a given
        recommendation context — a relevant SOP, a similar
        past incident, and a platform best practice.

        Implemented today as lightweight local-JSON retrieval
        (agents/recommendation/knowledge/*.json). The public
        interface (retrieve()) returns the same shape
        regardless of backing store, so this can later be
        replaced by a vector database without any change to
        the Recommendation Agent, Recommendation Engine, or
        Prompt Builder.

    Input:
        Recommendation Context Dictionary

    Output:
        Retrieved Knowledge Dictionary
        (relevant_sop, similar_incident, platform_best_practice)

    DOES NOT
    --------
    - Calculate priority or impact
    - Call Gemini
    - Validate or build the Recommendation Object
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        config = self.rule_engine.get_knowledge_retrieval_config()

        self.knowledge_dir = config.get(
            "knowledge_dir", "agents/recommendation/knowledge"
        )

        self.sources = config.get("sources", {})

        self.max_results_per_source = config.get(
            "max_results_per_source", 1
        )

        self.incident_playbook = self._load_source("incident_playbook")

        self.platform_best_practices = self._load_source(
            "platform_best_practices"
        )

        self.sop_library = self._load_source("sop_library")

        logger.info("Knowledge Retriever Ready.")

    # =====================================================
    # LOAD ONE SOURCE
    # =====================================================

    def _load_source(self, source_key):

        filename = self.sources.get(source_key)

        if not filename:

            return []

        path = os.path.join(self.knowledge_dir, filename)

        try:

            with open(path, "r", encoding="utf-8") as file:

                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError) as error:

            logger.warning(
                f"Knowledge source '{source_key}' unavailable "
                f"({path}): {error}"
            )

            return []

    # =====================================================
    # RETRIEVE RELEVANT SOP
    # =====================================================

    def retrieve_relevant_sop(self, context):

        priority = context.get("priority")

        for entry in self.sop_library:

            if priority in entry.get("applies_to_priorities", []):

                return entry.get("sop")

        return None

    # =====================================================
    # RETRIEVE SIMILAR INCIDENT
    # =====================================================

    def retrieve_similar_incident(self, context):

        risk_category = context.get("risk_category")

        priority = context.get("priority")

        for entry in self.incident_playbook:

            if risk_category and risk_category in entry.get(
                "applies_to_categories", []
            ):

                if not entry.get("applies_to_priorities") or (
                    priority in entry.get("applies_to_priorities", [])
                ):

                    return entry.get("playbook")

        return None

    # =====================================================
    # RETRIEVE PLATFORM BEST PRACTICE
    # =====================================================

    def retrieve_platform_best_practice(self, context):

        platform = context.get("platform")

        if not platform:

            return None

        normalized_platform = platform.replace(" ", "").lower()

        for entry in self.platform_best_practices:

            entry_platform = (entry.get("platform") or "").replace(
                " ", ""
            ).lower()

            if entry_platform == normalized_platform:

                return entry.get("practice")

        return None

    # =====================================================
    # RETRIEVE ALL
    # =====================================================

    def retrieve(self, context):

        return {

            "relevant_sop": self.retrieve_relevant_sop(context),

            "similar_incident": self.retrieve_similar_incident(context),

            "platform_best_practice":
                self.retrieve_platform_best_practice(context)

        }
