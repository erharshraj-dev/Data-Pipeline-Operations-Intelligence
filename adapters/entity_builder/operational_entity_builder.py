import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OperationalEntityBuilder:

    def __init__(self):

        logger.info("Initializing Operational Entity Builder...")

        self.version = "1.0"

        logger.info("Operational Entity Builder Ready.")

    ###########################################################
    # Metadata
    ###########################################################

    def build_metadata(self):

        metadata = {

            "adapter_version": self.version,

            "pipeline_stage": "Capability Adapter",

            "generated_at": datetime.now().isoformat()

        }

        return metadata

    ###########################################################
    # Validation Block
    ###########################################################

    def build_validation(self, record):

        validation = {

            "validation_score":
                record.get("validation_score", 0),

            "is_valid":
                record.get("is_valid", False),

            "errors":
                record.get("errors", []),

            "warnings":
                record.get("warnings", [])

        }

        return validation

    ###########################################################
    # Context Block
    ###########################################################

    def build_context(self, record):

        context = {

            "business_context":
                record.get("business_context", {}),

            "historical_context":
                record.get("historical_context", {}),

            "incident_context":
                record.get("incident_context", {}),

            "lineage_context":
                record.get("lineage_context", {}),

            "recommendation_context":
                record.get("recommendation_context", {})

        }

        return context

    ###########################################################
    # Build One Entity
    ###########################################################

    def build_entity(self, record):

        entity = {

            "entity_id":
                record.get("entity_id"),

            "entity_name":
                record.get("entity_name"),

            "entity_type":
                record.get("entity_type"),

            "source_system":
                record.get("source_system"),

            "execution_status":
                record.get("execution_status"),

            "event_timestamp":
                record.get("event_timestamp"),

            "attributes": {},

            "context":
                self.build_context(record),

            "validation":
                self.build_validation(record),

            "metadata":
                self.build_metadata()

        }

        reserved = {

            "entity_id",
            "entity_name",
            "entity_type",
            "source_system",
            "execution_status",
            "event_timestamp",

            "business_context",
            "historical_context",
            "incident_context",
            "lineage_context",
            "recommendation_context",

            "validation_score",
            "is_valid",
            "errors",
            "warnings"

        }

        for key, value in record.items():

            if key not in reserved:

                entity["attributes"][key] = value

        return entity

    ###########################################################
    # Build Dataset
    ###########################################################

    def build_dataset(self, dataset_name, records):

        logger.info(f"Building Operational Entities : {dataset_name}")

        entities = []

        for record in records:

            entities.append(

                self.build_entity(record)

            )

        logger.info(f"{len(entities)} Operational Entities Created.")

        return entities

    ###########################################################
    # Build All
    ###########################################################

    def build_all(self, validated_data):

        logger.info("Building Canonical Operational Entities...")

        entities = {}

        for dataset_name, records in validated_data.items():

            entities[dataset_name] = self.build_dataset(

                dataset_name,

                records

            )

        logger.info("Operational Entity Generation Completed.")

        return entities