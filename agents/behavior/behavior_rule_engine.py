import yaml
import logging

logger = logging.getLogger(__name__)


class BehaviorRuleEngine:
    """
    ==========================================================
    Behavior Rule Engine

    Responsibility:
        Load Behavior Agent configuration and expose it to
        every other Behavior Agent module. Single source of
        truth for metric mappings, thresholds, weights, and
        rule parameters.

    Input:
        Path to config/behavior_rules.yaml

    Output:
        Behavior Rule Configuration

    DOES NOT
    --------
    - Perform deviation analysis
    - Perform drift detection
    - Perform pattern detection
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file):

        self.config_file = config_file

        self.metric_baseline_map = {}
        self.severity_thresholds = {}
        self.severity_scores = {}
        self.drift_config = {}
        self.pattern_rules = {}
        self.behavior_score_config = {}
        self.confidence_config = {}

        self.load_config()

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def load_config(self):

        logger.info("Loading Behavior Rule Configuration...")

        with open(self.config_file, "r") as file:

            config = yaml.safe_load(file)

        self.metric_baseline_map = config.get("metric_baseline_map", {})

        self.severity_thresholds = config.get("severity_thresholds", {})

        self.severity_scores = config.get("severity_scores", {})

        self.drift_config = config.get("drift_detection", {})

        self.pattern_rules = config.get("pattern_rules", {})

        self.behavior_score_config = config.get("behavior_score", {})

        self.confidence_config = config.get("confidence", {})

        logger.info("Behavior Rule Configuration loaded successfully.")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Behavior Rule Engine Ready.")

        return True

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_metric_baseline_map(self):

        return self.metric_baseline_map

    def get_baseline_field(self, metric_name):

        return self.metric_baseline_map.get(metric_name)

    def get_severity_thresholds(self):

        return self.severity_thresholds

    def get_severity_scores(self):

        return self.severity_scores

    def get_severity_order(self):

        return sorted(
            self.severity_scores,
            key=self.severity_scores.get
        )

    def get_severity_score(self, severity):

        return self.severity_scores.get(severity, 0)

    def get_drift_config(self):

        return self.drift_config

    def get_pattern_rules(self):

        return self.pattern_rules

    def get_behavior_score_config(self):

        return self.behavior_score_config

    def get_metric_weight(self, metric_name):

        weights = self.behavior_score_config.get("metric_weights", {})

        default_weight = self.behavior_score_config["default_weight"]

        return weights.get(metric_name, default_weight)

    def get_confidence_config(self):

        return self.confidence_config
