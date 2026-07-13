import logging

from connectors.csv_connector import CSVConnector
from parsers.tabular_parser import TabularParser
from mapping.mapping_engine import MappingEngine
from normalizer.normalizer import Normalizer
from enricher.context_enricher import ContextEnricher
from validation.validation_engine import ValidationEngine
from entity_builder.operational_entity_builder import OperationalEntityBuilder

# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("=" * 80)
    logger.info("ADAPTIVE INTELLIGENCE FABRIC (AIF)")
    logger.info("CAPABILITY ADAPTER LAYER")
    logger.info("=" * 80)

    # ======================================================
    # STEP 1 : CSV CONNECTOR
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 1 : CSV CONNECTOR")
    logger.info("=" * 60)

    connector = CSVConnector("config/sources.yaml")

    connector.connect()

    datasets = connector.read_all()

    connector.disconnect()

    # ======================================================
    # Separate Raw Sources & Lookup Tables
    # ======================================================

    raw_dataset_names = [

        "airflow",
        "kafka",
        "kubernetes",
        "azure_data_factory",
        "sap",
        "manufacturing",
        "iot"

    ]

    lookup_dataset_names = [

        "business_context",
        "historical_baselines",
        "incident_history",
        "pipeline_lineage",
        "recommendation_history"

    ]

    raw_datasets = {

        name: datasets[name]

        for name in raw_dataset_names

    }

    lookup_datasets = {

        name: datasets[name]

        for name in lookup_dataset_names

    }

    logger.info(f"Raw Datasets Loaded    : {len(raw_datasets)}")
    logger.info(f"Lookup Datasets Loaded : {len(lookup_datasets)}")

    # ======================================================
    # STEP 2 : TABULAR PARSER
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 2 : TABULAR PARSER")
    logger.info("=" * 60)

    parser = TabularParser()

    parsed_raw = parser.parse_all(raw_datasets)

    parsed_lookup = parser.parse_all(lookup_datasets)

    logger.info("Parsing Completed Successfully.")

    # ======================================================
    # STEP 3 : MAPPING ENGINE
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 3 : MAPPING ENGINE")
    logger.info("=" * 60)

    mapper = MappingEngine("config/mapping.yaml")

    mapped_data = mapper.map_all(parsed_raw)

    logger.info("Mapping Completed Successfully.")

    # ======================================================
    # STEP 4 : NORMALIZER
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 4 : NORMALIZER")
    logger.info("=" * 60)

    normalizer = Normalizer()

    normalized_data = normalizer.normalize_all(mapped_data)

    logger.info("Normalization Completed Successfully.")

    # ======================================================
    # STEP 5 : CONTEXT ENRICHER
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 5 : CONTEXT ENRICHER")
    logger.info("=" * 60)

    enricher = ContextEnricher(parsed_lookup)

    if hasattr(enricher, "health_check"):
        enricher.health_check()

    enriched_data = enricher.enrich_all(normalized_data)

    logger.info("Context Enrichment Completed Successfully.")

    # ======================================================
    # STEP 6 : VALIDATION ENGINE
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 6 : VALIDATION ENGINE")
    logger.info("=" * 60)

    validator = ValidationEngine()

    validator.health_check()

    validation_results = validator.validate_all(enriched_data)

    logger.info("Validation Completed Successfully.")

    # ======================================================
    # STEP 7 : OPERATIONAL ENTITY BUILDER
    # ======================================================

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 7 : OPERATIONAL ENTITY BUILDER")
    logger.info("=" * 60)

    entity_builder = OperationalEntityBuilder()

    operational_entities = entity_builder.build_all(
        validation_results
    )

    logger.info("Operational Entity Generation Completed.")

    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n")
    print("=" * 100)
    print("CANONICAL OPERATIONAL ENTITIES")
    print("=" * 100)

    for dataset_name, entities in operational_entities.items():

        print(f"\nDataset : {dataset_name}")

        print(f"Operational Entities : {len(entities)}")

        print("\nFirst Operational Entity\n")

        first_entity = entities[0]

        for key, value in first_entity.items():

            print(f"{key} : {value}")

        print("-" * 100)

    print("\n")
    print("=" * 100)
    print("VALIDATION SUMMARY")
    print("=" * 100)

    for dataset_name, records in validation_results.items():

        first = records[0]

        print(f"\nDataset : {dataset_name}")

        print("Validation Score :", first["validation_score"])

        print("Errors :", first["errors"])

        print("Warnings :", first["warnings"])

        print("-" * 100)

    logger.info("")
    logger.info("=" * 80)
    logger.info("CAPABILITY ADAPTER LAYER EXECUTED SUCCESSFULLY")
    logger.info("=" * 80)


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()