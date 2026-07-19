import logging

logger = logging.getLogger(__name__)


class CategoryClassifier:
    """
    ==========================================================
    Category Classifier

    Responsibility:
        Determine WHAT KIND of operational risk an entity is
        facing (Pipeline Failure, SLA Breach, Resource
        Exhaustion, Dependency Failure, Data Quality Risk,
        Infrastructure Risk, Configuration Risk, ...) —
        completely independently of the Risk Score / Risk
        Severity, which only describe HOW MUCH risk there is.

        Classification is driven entirely by category_rules in
        risk_rules.yaml: each rule is a generic condition check
        ("<signal>_<operator>": expected_value) evaluated
        against a flat signal dictionary built from the
        Operational Entity, Observation Object and Behavior
        Object. Rules are tried highest-priority first; the
        first one whose conditions match wins. No category name
        is ever hardcoded in this file — only the generic
        operators (min / max / equals / contains) are.

    Input:
        Behavior Object

    Output:
        Risk Category (string)

    DOES NOT
    --------
    - Calculate the Risk Score
    - Classify Risk Severity
    - Use the Risk Score/Severity as an input
    ==========================================================
    """

    SUPPORTED_OPERATORS = ("min", "max", "equals", "contains")

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Category Classifier Ready.")

    # =====================================================
    # SIGNAL EXTRACTION
    # =====================================================

    def build_signals(self, behavior_object):

        behavior = behavior_object.get("behavior", {})

        observation_object = behavior_object.get("observation", {})

        observations = observation_object.get("observations", {})

        entity = observation_object.get("entity", {})

        attributes = entity.get("attributes", {})

        validation = entity.get("validation", {})

        business_context = entity.get(
            "context", {}
        ).get(
            "business_context", {}
        )

        incident_context = entity.get(
            "context", {}
        ).get(
            "incident_context", {}
        )

        trend = observations.get("trend", {})

        adverse_trend_metrics = [

            metric_name
            for metric_name, direction in trend.items()
            if self.rule_engine.is_trend_adverse(metric_name, direction)

        ]

        deviation = behavior.get("deviation", {})

        severity_map = self.rule_engine.get_behavior_severity_map()

        deviation_severities = [

            result.get("severity")
            for result in deviation.values()
            if result.get("severity") is not None

        ]

        max_deviation_severity = None

        if deviation_severities:

            max_deviation_severity = max(

                deviation_severities,

                key=lambda label: severity_map.get(label, 0.0)

            )

        signals = {

            "source_system": entity.get("source_system"),

            "execution_status": entity.get("execution_status"),

            "events": observations.get("events", []) or [],

            "patterns": behavior.get("patterns", []) or [],

            "behavior_severity": behavior.get("severity"),

            "trend": trend,

            "adverse_trend_metrics": adverse_trend_metrics,

            "adverse_trend_count": len(adverse_trend_metrics),

            "max_deviation_severity": max_deviation_severity,

            "retry_count": attributes.get("retry_count"),

            "cpu_usage": attributes.get("cpu_usage"),

            "memory_usage": attributes.get("memory_usage"),

            "elapsed_runtime": attributes.get("elapsed_runtime"),

            "throughput": attributes.get("throughput"),

            "consumer_lag": attributes.get("consumer_lag"),

            "temperature": attributes.get("temperature"),

            "humidity": attributes.get("humidity"),

            "battery_level": attributes.get("battery_level"),

            "signal_strength": attributes.get("signal_strength"),

            "is_valid": validation.get("is_valid"),

            "validation_error_count": len(
                validation.get("errors", []) or []
            ),

            "validation_warning_count": len(
                validation.get("warnings", []) or []
            ),

            "business_criticality": business_context.get("criticality"),

            "sla_minutes": business_context.get("sla_minutes"),

            "historical_incident_count":
                incident_context.get("total_incidents"),

            "historical_root_cause": incident_context.get("root_cause"),

        }

        signals["sla_margin_ratio"] = self._compute_sla_margin_ratio(
            signals.get("sla_minutes"),
            signals.get("elapsed_runtime")
        )

        return signals

    # =====================================================
    # SLA MARGIN RATIO
    #
    # Same formula the Feature Extractor uses for the
    # sla_margin_ratio risk feature, computed independently
    # here so the Category Classifier has no dependency on
    # FeatureExtractor internals.
    # =====================================================

    def _compute_sla_margin_ratio(self, sla_minutes, elapsed_runtime):

        if sla_minutes in (None, 0) or elapsed_runtime is None:

            return None

        return (sla_minutes - elapsed_runtime) / sla_minutes

    # =====================================================
    # CONDITION EVALUATION
    # =====================================================

    def evaluate_condition(self, signals, field, operator, expected):

        value = signals.get(field)

        if value is None:

            return False

        if operator == "min":

            return value >= expected

        if operator == "max":

            return value <= expected

        if operator == "equals":

            return value == expected

        if operator == "contains":

            if not isinstance(value, (list, tuple, set)):

                return False

            expected_values = (

                expected
                if isinstance(expected, (list, tuple, set))
                else [expected]

            )

            return any(item in value for item in expected_values)

        logger.warning(
            f"Unsupported category condition operator: {operator}"
        )

        return False

    def evaluate_rule(self, signals, rule):

        conditions = rule.get("conditions", {})

        if not conditions:

            return False

        match_mode = rule.get("match", "all")

        results = []

        for condition_key, expected in conditions.items():

            field, _, operator = condition_key.rpartition("_")

            if not field or operator not in self.SUPPORTED_OPERATORS:

                logger.warning(
                    f"Skipping malformed category condition: "
                    f"{condition_key}"
                )

                continue

            results.append(
                self.evaluate_condition(signals, field, operator, expected)
            )

        if not results:

            return False

        if match_mode == "any":

            return any(results)

        return all(results)

    # =====================================================
    # CLASSIFY
    # =====================================================

    def classify(self, behavior_object):

        signals = self.build_signals(behavior_object)

        category_rules = self.rule_engine.get_category_rules()

        ranked_rules = sorted(
            category_rules,
            key=lambda rule: rule.get("priority", 0),
            reverse=True
        )

        for rule in ranked_rules:

            if self.evaluate_rule(signals, rule):

                return rule.get(
                    "category",
                    self.rule_engine.get_default_risk_category()
                )

        return self.rule_engine.get_default_risk_category()
