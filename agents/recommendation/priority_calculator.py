import logging

logger = logging.getLogger(__name__)


class PriorityCalculator:
    """
    ==========================================================
    Priority Calculator

    Responsibility:
        Determine recommendation priority (CRITICAL / HIGH /
        MEDIUM / LOW) from the recommendation context — driven
        entirely by priority_rules in recommendation_rules.yaml.
        Mirrors the Risk Prediction Agent's CategoryClassifier
        pattern exactly: each rule is a set of
        "<signal>_<operator>": expected_value conditions, rules
        are tried highest "priority" number first, and the
        first rule whose conditions match wins. No priority
        name or threshold is ever hardcoded here — only the
        generic operators (min / max / equals / contains) are.

        No escalation logic — every entity receives exactly one
        priority, including LOW; nothing is ever skipped.

    Input:
        Recommendation Context Dictionary

    Output:
        Priority Label (string)

    DOES NOT
    --------
    - Estimate impact / recovery time / automation
    - Retrieve knowledge
    - Call Gemini
    ==========================================================
    """

    SUPPORTED_OPERATORS = ("min", "max", "equals", "contains")

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Priority Calculator Ready.")

    # =====================================================
    # CONDITION EVALUATION
    # =====================================================

    def evaluate_condition(self, context, field, operator, expected):

        value = context.get(field)

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
            f"Unsupported priority condition operator: {operator}"
        )

        return False

    def evaluate_rule(self, context, rule):

        conditions = rule.get("conditions", {})

        if not conditions:

            return False

        match_mode = rule.get("match", "all")

        results = []

        for condition_key, expected in conditions.items():

            field, _, operator = condition_key.rpartition("_")

            if not field or operator not in self.SUPPORTED_OPERATORS:

                logger.warning(
                    f"Skipping malformed priority condition: "
                    f"{condition_key}"
                )

                continue

            results.append(
                self.evaluate_condition(context, field, operator, expected)
            )

        if not results:

            return False

        if match_mode == "any":

            return any(results)

        return all(results)

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, context):

        priority_rules = self.rule_engine.get_priority_rules()

        ranked_rules = sorted(
            priority_rules,
            key=lambda rule: rule.get("priority", 0),
            reverse=True
        )

        for rule in ranked_rules:

            if self.evaluate_rule(context, rule):

                return rule.get(
                    "priority_label",
                    self.rule_engine.get_default_priority()
                )

        return self.rule_engine.get_default_priority()
