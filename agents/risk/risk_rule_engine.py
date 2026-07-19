import yaml
import logging

logger = logging.getLogger(__name__)


class RiskRuleEngine:
    """
    ==========================================================
    Risk Rule Engine

    Responsibility:
        Load Risk Prediction Agent configuration and expose
        it to every other Risk Prediction Agent module.
        Single source of truth for feature weights,
        normalization bounds, category mappings, severity
        thresholds, and probability/confidence parameters.

    Input:
        Path to config/risk_rules.yaml

    Output:
        Risk Rule Configuration

    DOES NOT
    --------
    - Extract features
    - Calculate risk score
    - Classify severity
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file):

        self.config_file = config_file

        self.feature_definitions = {}
        self.behavior_severity_map = {}
        self.business_criticality_map = {}
        self.adverse_trend_values = []
        self.severity_thresholds = {}
        self.category_mapping = {}
        self.probability_config = {}
        self.confidence_config = {}
        self.normalization_profiles = {}
        self.trend_adversity = {}
        self.category_rules = []
        self.default_risk_category = "Operational Risk"

        self.load_config()

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def load_config(self):

        logger.info("Loading Risk Rule Configuration...")

        with open(self.config_file, "r") as file:

            config = yaml.safe_load(file)

        self.feature_definitions = config.get("features", {})

        self.behavior_severity_map = config.get(
            "behavior_severity_map", {}
        )

        self.business_criticality_map = config.get(
            "business_criticality_map", {}
        )

        self.adverse_trend_values = config.get(
            "adverse_trend_values", []
        )

        self.severity_thresholds = config.get(
            "severity_thresholds", {}
        )

        self.category_mapping = config.get("category_mapping", {})

        self.probability_config = config.get("probability", {})

        self.confidence_config = config.get("confidence", {})

        self.normalization_profiles = config.get(
            "normalization_profiles", {}
        )

        self.trend_adversity = config.get("trend_adversity", {})

        self.category_rules = config.get("category_rules", [])

        self.default_risk_category = config.get(
            "default_risk_category", "Operational Risk"
        )

        logger.info("Risk Rule Configuration loaded successfully.")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Risk Rule Engine Ready.")

        return True

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_feature_definitions(self, source_system=None):

        if source_system is None:

            return self.feature_definitions

        # ------------------------------------------------
        # Issue 3: Domain-Agnostic Normalization
        #
        # Layer normalization bounds on top of the base
        # feature definitions: base -> "default" profile ->
        # the profile matching this entity's source_system.
        # Only min/max are ever overridden this way; weight
        # and invert always come from the base definition.
        # ------------------------------------------------

        merged_definitions = {

            feature_name: dict(feature_config)

            for feature_name, feature_config in
            self.feature_definitions.items()

        }

        default_profile = self.normalization_profiles.get(
            "default", {}
        )

        source_profile = self.normalization_profiles.get(
            source_system, {}
        )

        for profile in (default_profile, source_profile):

            for feature_name, bounds in profile.items():

                if feature_name in merged_definitions:

                    merged_definitions[feature_name].update(bounds)

        return merged_definitions

    def get_feature_weight(self, feature_name):

        return self.feature_definitions.get(
            feature_name, {}
        ).get("weight", 0.0)

    def get_normalization_profiles(self):

        return self.normalization_profiles

    def get_behavior_severity_map(self):

        return self.behavior_severity_map

    def get_business_criticality_map(self):

        return self.business_criticality_map

    def get_adverse_trend_values(self):

        return self.adverse_trend_values

    def get_severity_thresholds(self):

        return self.severity_thresholds

    def get_category_mapping(self):

        return self.category_mapping

    def get_probability_config(self):

        return self.probability_config

    def get_confidence_config(self):

        return self.confidence_config

    # =====================================================
    # TREND ADVERSITY (Issue 4)
    # =====================================================

    def get_trend_adversity_config(self):

        return self.trend_adversity

    def is_trend_adverse(self, metric_name, direction):

        # Metric-aware lookup first: metric_name -> direction,
        # falling back to the "default" entry for a metric
        # with no dedicated mapping.

        if self.trend_adversity:

            metric_map = self.trend_adversity.get(
                metric_name,
                self.trend_adversity.get("default", {})
            )

            if direction in metric_map:

                return bool(metric_map[direction])

        # Legacy fallback: trend_adversity missing entirely,
        # or the metric/direction pair isn't covered by it.

        return direction in self.adverse_trend_values

    # =====================================================
    # RISK CATEGORY RULES (Issue 1)
    # =====================================================

    def get_category_rules(self):

        return self.category_rules

    def get_default_risk_category(self):

        return self.default_risk_category
