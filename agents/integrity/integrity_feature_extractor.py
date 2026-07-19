import logging

logger = logging.getLogger(__name__)


class IntegrityFeatureExtractor:
    """
    ==========================================================
    Integrity Feature Extractor

    Responsibility:
        Pull the raw, unvalidated signals each of the five
        Integrity checks needs out of the Operational Entity
        and Observation Object — record count inputs, the
        Validation Engine's own data quality block, a flat
        record for business rule evaluation, required-field
        presence for schema, and the lineage context.

        Extraction only. No thresholds, no scoring, no
        PASS/WARNING/FAILED decisions are made here.

    Input:
        Observation Object
        Operational Entity (optional — the Observation Object
        already carries it under "entity"; pass this
        explicitly only to evaluate against a different or
        overridden entity than the one embedded)

    Output:
        Raw Signal Dictionary, one entry per check

    DOES NOT
    --------
    - Validate anything
    - Calculate scores
    - Classify status
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Integrity Feature Extractor Ready.")

    # =====================================================
    # EXTRACT ALL
    # =====================================================

    def extract(self, observation_object, entity=None):

        if entity is None:

            entity = observation_object.get("entity", {})

        signals = {

            "record_count": self.extract_record_count_signals(entity),

            "data_quality": self.extract_data_quality_signals(entity),

            "business_rules": self.extract_business_rule_record(entity),

            "schema": self.extract_schema_signals(entity),

            "lineage": self.extract_lineage_signals(entity)

        }

        return signals

    # =====================================================
    # RECORD COUNT SIGNALS
    # =====================================================

    def extract_record_count_signals(self, entity):

        source_system = entity.get("source_system")

        field_mapping = self.rule_engine.get_record_count_fields(
            source_system
        )

        if not field_mapping:

            # No expected-vs-actual source configured for this
            # domain — the validator will mark this NOT_EVALUATED
            # rather than guessing.

            return {"available": False}

        attributes = entity.get("attributes", {})

        actual_value = attributes.get(field_mapping.get("actual_field"))

        expected_context_name = field_mapping.get("expected_context")

        expected_field_name = field_mapping.get("expected_field")

        expected_context = entity.get(
            "context", {}
        ).get(expected_context_name, {})

        expected_value = expected_context.get(expected_field_name)

        if actual_value is None or expected_value is None:

            return {"available": False}

        return {

            "available": True,
            "actual_value": actual_value,
            "expected_value": expected_value

        }

    # =====================================================
    # DATA QUALITY SIGNALS
    # =====================================================

    def extract_data_quality_signals(self, entity):

        validation = entity.get("validation", {})

        return {

            "validation_score": validation.get("validation_score"),

            "is_valid": validation.get("is_valid"),

            "error_count": len(validation.get("errors", []) or []),

            "warning_count": len(validation.get("warnings", []) or [])

        }

    # =====================================================
    # BUSINESS RULE RECORD
    #
    # Flattens the entity's top-level fields and its attributes
    # into a single dict so business rules can reference either
    # by name without caring where the field actually lives.
    # =====================================================

    def extract_business_rule_record(self, entity):

        record = {

            "entity_id": entity.get("entity_id"),
            "entity_name": entity.get("entity_name"),
            "entity_type": entity.get("entity_type"),
            "source_system": entity.get("source_system"),
            "execution_status": entity.get("execution_status"),
            "event_timestamp": entity.get("event_timestamp"),

        }

        record.update(entity.get("attributes", {}))

        return record

    # =====================================================
    # SCHEMA SIGNALS
    # =====================================================

    def extract_schema_signals(self, entity):

        return {

            "entity": entity,

            "attributes": entity.get("attributes", {}),

            "source_system": entity.get("source_system")

        }

    # =====================================================
    # LINEAGE SIGNALS
    # =====================================================

    def extract_lineage_signals(self, entity):

        lineage_context = entity.get(
            "context", {}
        ).get("lineage_context", {}) or {}

        return {

            "has_lineage_record": bool(lineage_context),

            "depends_on": lineage_context.get("depends_on"),

            "downstream": lineage_context.get("downstream"),

            "dependency_type": lineage_context.get("dependency_type")

        }
