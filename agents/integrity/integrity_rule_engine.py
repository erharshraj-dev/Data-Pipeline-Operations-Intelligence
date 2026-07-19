import yaml
import logging

logger = logging.getLogger(__name__)


class IntegrityRuleEngine:
    """
    ==========================================================
    Integrity Rule Engine

    Responsibility:
        Load Integrity Agent configuration and expose it to
        every other Integrity Agent module. Single source of
        truth for check weights, per-check score thresholds,
        overall status/trust-level thresholds, validation
        priority, schema requirements, business rules, record
        count field mappings, lineage requirements, and agent
        metadata (e.g. agent_version).

    Input:
        Path to config/integrity_rules.yaml

    Output:
        Integrity Rule Configuration

    DOES NOT
    --------
    - Extract validation signals
    - Run any validation
    - Calculate the Integrity Score
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file):

        self.config_file = config_file

        self.weights = {}
        self.check_thresholds = {}
        self.status_thresholds = {}
        self.trust_level_thresholds = {}
        self.validation_priority = {}
        self.check_display_names = {}
        self.record_count_config = {}
        self.data_quality_config = {}
        self.schema_config = {}
        self.business_rules_config = {}
        self.lineage_config = {}
        self.agent_config = {}

        self.load_config()

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def load_config(self):

        logger.info("Loading Integrity Rule Configuration...")

        with open(self.config_file, "r") as file:

            config = yaml.safe_load(file)

        self.weights = config.get("weights", {})

        self.check_thresholds = config.get("check_thresholds", {})

        self.status_thresholds = config.get("status_thresholds", {})

        self.trust_level_thresholds = config.get(
            "trust_level_thresholds", {}
        )

        self.validation_priority = config.get(
            "validation_priority", {}
        )

        self.check_display_names = config.get(
            "check_display_names", {}
        )

        self.record_count_config = config.get("record_count", {})

        self.data_quality_config = config.get("data_quality", {})

        self.schema_config = config.get("schema", {})

        self.business_rules_config = config.get("business_rules", {})

        self.lineage_config = config.get("lineage", {})

        self.agent_config = config.get("agent", {})

        logger.info(
            "Integrity Rule Configuration loaded successfully."
        )

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Integrity Rule Engine Ready.")

        return True

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_weights(self):

        return self.weights

    def get_check_thresholds(self, check_name):

        default_thresholds = self.check_thresholds.get("default", {})

        return self.check_thresholds.get(check_name, default_thresholds)

    def get_status_thresholds(self):

        return self.status_thresholds

    def get_trust_level_thresholds(self):

        return self.trust_level_thresholds

    def get_validation_priority(self):

        return self.validation_priority

    def get_check_display_name(self, check_name):

        return self.check_display_names.get(check_name, check_name)

    def get_record_count_config(self):

        return self.record_count_config

    def get_record_count_fields(self, source_system):

        return self.record_count_config.get(
            "fields", {}
        ).get(source_system)

    def get_data_quality_config(self):

        return self.data_quality_config

    def get_schema_required_top_level_fields(self):

        return self.schema_config.get("required_top_level_fields", [])

    def get_schema_required_attributes(self, source_system):

        # Same merge pattern as risk_rule_engine's normalization
        # profiles: "default" always applies, a source_system
        # entry is additive on top of it.

        required_attributes = self.schema_config.get(
            "required_attributes", {}
        )

        default_required = required_attributes.get("default", [])

        source_required = required_attributes.get(source_system, [])

        return list(dict.fromkeys(default_required + source_required))

    def get_business_rules(self):

        return self.business_rules_config.get("rules", [])

    def get_lineage_config(self):

        return self.lineage_config

    def get_agent_version(self):

        return self.agent_config.get("version", "1.0")
