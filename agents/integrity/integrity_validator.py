import logging

logger = logging.getLogger(__name__)


class IntegrityValidator:
    """
    ==========================================================
    Integrity Validator

    Responsibility:
        Run the five Integrity checks — Record Count, Data
        Quality, Business Rules, Schema, Lineage — against the
        signals produced by the Feature Extractor, using
        thresholds and rule definitions from the Rule Engine.
        Each check produces a 0-100 score (or None if it could
        not be evaluated for this entity) and a
        PASS / WARNING / FAILED / NOT_EVALUATED status.

    Input:
        Raw Signal Dictionary (from Feature Extractor)

    Output:
        Validation Results Dictionary, one entry per check:
            {status, score, details}

    DOES NOT
    --------
    - Extract signals
    - Calculate the overall weighted Integrity Score
    - Classify overall status or trust level
    ==========================================================
    """

    SUPPORTED_OPERATORS = ("exists", "min", "max", "equals", "in")

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Integrity Validator Ready.")

    # =====================================================
    # SCORE -> STATUS
    # =====================================================

    def classify_check_status(self, check_name, score):

        thresholds = self.rule_engine.get_check_thresholds(check_name)

        pass_min = thresholds.get("pass_min", 90)

        warning_min = thresholds.get("warning_min", 70)

        if score >= pass_min:

            return "PASS"

        elif score >= warning_min:

            return "WARNING"

        else:

            return "FAILED"

    # =====================================================
    # 1. RECORD COUNT VALIDATION
    # =====================================================

    def validate_record_count(self, signals):

        if not signals.get("available"):

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No expected-vs-actual record count "
                            "source configured for this source_system."

            }

        actual_value = signals["actual_value"]

        expected_value = signals["expected_value"]

        record_count_config = self.rule_engine.get_record_count_config()

        tolerance_percent = record_count_config.get(
            "tolerance_percent", 10
        )

        if expected_value == 0:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "Expected value is zero; percentage "
                            "deviation is undefined."

            }

        deviation_percent = (
            abs(actual_value - expected_value) / abs(expected_value) * 100
        )

        score = max(0.0, 100.0 - max(0.0, deviation_percent - tolerance_percent))

        score = round(score, 2)

        status = self.classify_check_status("record_count", score)

        details = (
            f"actual={actual_value}, expected={expected_value}, "
            f"deviation={round(deviation_percent, 1)}%"
        )

        return {"status": status, "score": score, "details": details}

    # =====================================================
    # 2. DATA QUALITY VALIDATION
    # =====================================================

    def validate_data_quality(self, signals):

        validation_score = signals.get("validation_score")

        if validation_score is None:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No validation_score present on entity."

            }

        score = round(float(validation_score), 2)

        status = self.classify_check_status("data_quality", score)

        details = (
            f"validation_score={score}, "
            f"errors={signals.get('error_count', 0)}, "
            f"warnings={signals.get('warning_count', 0)}"
        )

        return {"status": status, "score": score, "details": details}

    # =====================================================
    # 3. BUSINESS RULE VALIDATION
    # =====================================================

    def evaluate_business_rule(self, record, rule):

        field = rule.get("field")

        operator = rule.get("operator")

        expected = rule.get("value")

        value = record.get(field)

        if operator == "exists":

            return value is not None

        # Every other operator requires the field to actually be
        # applicable to this entity — a domain that simply has no
        # such attribute is excluded, not failed.

        if value is None:

            return None

        if operator == "min":

            return value >= expected

        if operator == "max":

            return value <= expected

        if operator == "equals":

            return value == expected

        if operator == "in":

            return value in expected

        logger.warning(f"Unsupported business rule operator: {operator}")

        return None

    def validate_business_rules(self, record):

        rules = self.rule_engine.get_business_rules()

        if not rules:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No business rules configured."

            }

        passed_rules = []

        failed_rules = []

        for rule in rules:

            result = self.evaluate_business_rule(record, rule)

            if result is None:

                continue

            if result:

                passed_rules.append(rule.get("name"))

            else:

                failed_rules.append(rule.get("name"))

        rules_evaluated = len(passed_rules) + len(failed_rules)

        if rules_evaluated == 0:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No configured business rule applied "
                            "to this entity."

            }

        score = round(len(passed_rules) / rules_evaluated * 100, 2)

        status = self.classify_check_status("business_rules", score)

        details = (
            f"{len(passed_rules)}/{rules_evaluated} rules passed"
            + (f"; failed: {', '.join(failed_rules)}" if failed_rules else "")
        )

        return {"status": status, "score": score, "details": details}

    # =====================================================
    # 4. SCHEMA VALIDATION
    # =====================================================

    def validate_schema(self, signals):

        entity = signals.get("entity", {})

        attributes = signals.get("attributes", {})

        source_system = signals.get("source_system")

        required_top_level = (
            self.rule_engine.get_schema_required_top_level_fields()
        )

        required_attributes = (
            self.rule_engine.get_schema_required_attributes(source_system)
        )

        missing_fields = [

            field_name for field_name in required_top_level
            if entity.get(field_name) is None

        ]

        missing_attributes = [

            attribute_name for attribute_name in required_attributes
            if attributes.get(attribute_name) is None

        ]

        total_required = len(required_top_level) + len(required_attributes)

        missing = missing_fields + missing_attributes

        if total_required == 0:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No schema requirements configured "
                            "for this source_system."

            }

        present_count = total_required - len(missing)

        score = round(present_count / total_required * 100, 2)

        status = self.classify_check_status("schema", score)

        details = (
            "All required fields present" if not missing
            else f"Missing: {', '.join(missing)}"
        )

        return {"status": status, "score": score, "details": details}

    # =====================================================
    # 5. LINEAGE VALIDATION
    # =====================================================

    def validate_lineage(self, signals):

        lineage_config = self.rule_engine.get_lineage_config()

        if not signals.get("has_lineage_record"):

            return {

                "status": "FAILED",
                "score": 0.0,
                "details": "No lineage record found for this entity "
                            "— broken lineage."

            }

        checks = []

        if lineage_config.get("require_depends_on", True):

            checks.append(bool(signals.get("depends_on")))

        if lineage_config.get("require_downstream", True):

            checks.append(bool(signals.get("downstream")))

        if not checks:

            return {

                "status": "NOT_EVALUATED",
                "score": None,
                "details": "No lineage requirements configured."

            }

        score = round(sum(checks) / len(checks) * 100, 2)

        status = self.classify_check_status("lineage", score)

        details = (
            f"depends_on={signals.get('depends_on')}, "
            f"downstream={signals.get('downstream')}, "
            f"dependency_type={signals.get('dependency_type')}"
        )

        return {"status": status, "score": score, "details": details}

    # =====================================================
    # VALIDATE ALL
    # =====================================================

    def validate_all(self, signals):

        validation_results = {

            "record_count": self.validate_record_count(
                signals["record_count"]
            ),

            "data_quality": self.validate_data_quality(
                signals["data_quality"]
            ),

            "business_rules": self.validate_business_rules(
                signals["business_rules"]
            ),

            "schema": self.validate_schema(
                signals["schema"]
            ),

            "lineage": self.validate_lineage(
                signals["lineage"]
            )

        }

        return validation_results
