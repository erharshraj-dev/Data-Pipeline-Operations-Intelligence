import logging

logger = logging.getLogger(__name__)


class ContextEnricher:

    def __init__(self, lookup_datasets):

        logger.info("Initializing Context Enricher...")

        self.lookup = lookup_datasets

        self.business_index = {}
        self.history_index = {}
        self.incident_index = {}
        self.lineage_index = {}
        self.recommendation_index = {}

        self.build_indexes()

    #######################################################
    # Build Indexes
    #######################################################

    def build_indexes(self):

        logger.info("Building Lookup Indexes...")

        self.business_index = self.create_index(
            self.lookup.get("business_context", [])
        )

        self.history_index = self.create_index(
            self.lookup.get("historical_baselines", [])
        )

        self.incident_index = self.create_index(
            self.lookup.get("incident_history", [])
        )

        self.lineage_index = self.create_index(
            self.lookup.get("pipeline_lineage", [])
        )

        self.recommendation_index = self.create_index(
            self.lookup.get("recommendation_history", [])
        )

        logger.info("Lookup Indexes Created Successfully.")

    #######################################################
    # Generic Index Creator
    #######################################################

    def create_index(self, dataset):

        index = {}

        for row in dataset:

            entity_id = row.get("entity_id")

            if entity_id is not None:

                index[entity_id] = row

        return index
    #######################################################
    # Business Context
    #######################################################

    def enrich_business_context(self, record):

        entity_id = record["entity_id"]

        if entity_id in self.business_index:

            record["business_context"] = self.business_index.get(entity_id, {})

        else:

            record["business_context"] = {}

        return record

    #######################################################
    # Historical Baseline
    #######################################################

    def enrich_historical_context(self, record):

        entity_id = record["entity_id"]

        if entity_id in self.history_index:

            record["historical_context"] = self.history_index.get(entity_id, {})

        else:

            record["historical_context"] = {}

        return record
    #######################################################
    # Incident Context
    #######################################################

    def enrich_incident_context(self, record):

        entity_id = record["entity_id"]

        if entity_id in self.incident_index:

            record["incident_context"] = self.incident_index.get(entity_id, {})

        else:

            record["incident_context"] = {}

        return record
    #######################################################
    # Lineage Context
    #######################################################

    def enrich_lineage_context(self, record):

        entity_id = record["entity_id"]

        if entity_id in self.lineage_index:

            record["lineage_context"] = self.lineage_index.get(entity_id, {})

        else:

            record["lineage_context"] = {}

        return record
    #######################################################
    # Recommendation Context
    #######################################################

    def enrich_recommendation_context(self, record):

        entity_id = record["entity_id"]

        if entity_id in self.recommendation_index:

            record["recommendation_context"] = self.recommendation_index.get(entity_id, {})

        else:

            record["recommendation_context"] = {}

        return record
    #######################################################
    # Enrich One Record
    #######################################################

    def enrich_record(self, record):
        logger.debug(
            f"Enriching Entity : {record['entity_id']}"
            )
        record = self.enrich_business_context(record)

        record = self.enrich_historical_context(record)

        record = self.enrich_incident_context(record)

        record = self.enrich_lineage_context(record)

        record = self.enrich_recommendation_context(record)

        return record
    #######################################################
    # Enrich Dataset
    #######################################################

    def enrich_dataset(self, dataset_name, records):

        logger.info(f"Enriching Dataset : {dataset_name}")

        enriched = []

        for record in records:

            enriched.append(

                self.enrich_record(record)

            )

        logger.info(f"{len(enriched)} records enriched.")

        return enriched
    #######################################################
    # Enrich All Datasets
    #######################################################

    def enrich_all(self, normalized_data):

        logger.info("Starting Context Enrichment...")

        enriched = {}

        for dataset_name, records in normalized_data.items():

            enriched[dataset_name] = self.enrich_dataset(

                dataset_name,

                records

            )

        logger.info("Context Enrichment Completed.")

        return enriched
    
    def health_check(self):

        logger.info("Running Context Enricher Health Check...")

        print("Business Context :", len(self.business_index))

        print("Historical :", len(self.history_index))

        print("Incident :", len(self.incident_index))

        print("Lineage :", len(self.lineage_index))

        print("Recommendation :", len(self.recommendation_index))

        return True