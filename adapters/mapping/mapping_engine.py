import yaml
import logging

logger = logging.getLogger(__name__)


class MappingEngine:
    """
    Generic Mapping Engine

    Responsibilities
    ----------------
    1. Load mapping configuration
    2. Select mapping profile
    3. Transform source fields into Canonical Data Model
    4. Support:
       - source mapping
       - const mapping
       - default mapping

    DOES NOT
    --------
    - Normalize
    - Enrich
    - Validate
    """

    def __init__(self, mapping_file):

        self.mapping_file = mapping_file
        self.dataset_profiles = {}
        self.profiles = {}

        self.load_mapping()

    # --------------------------------------------------

    def load_mapping(self):

        logger.info("Loading Mapping Configuration...")

        with open(self.mapping_file, "r") as file:

            config = yaml.safe_load(file)

        self.dataset_profiles = config["dataset_profiles"]
        self.profiles = config["profiles"]

        logger.info("Mapping configuration loaded successfully.")

    # --------------------------------------------------

    def get_profile(self, dataset_name):

        profile_name = self.dataset_profiles.get(dataset_name)

        if profile_name is None:
            raise Exception(f"No mapping profile for {dataset_name}")

        return self.profiles[profile_name]

    # --------------------------------------------------

    def map_record(self, record, profile):

        mapped_record = {}

        for target_field, rule in profile.items():

            # --------------------------
            # Source Mapping
            # --------------------------

            if "source" in rule:

                source_field = rule["source"]

                mapped_record[target_field] = record.get(source_field)

            # --------------------------
            # Constant Mapping
            # --------------------------

            elif "const" in rule:

                mapped_record[target_field] = rule["const"]

            # --------------------------
            # Default Mapping
            # --------------------------

            elif "default" in rule:

                mapped_record[target_field] = rule["default"]

        return mapped_record

    # --------------------------------------------------

    def map_dataset(self, dataset_name, records):

        logger.info(f"Mapping dataset : {dataset_name}")

        profile = self.get_profile(dataset_name)

        mapped_records = []

        for record in records:

            mapped_records.append(
                self.map_record(record, profile)
            )

        logger.info(f"{len(mapped_records)} records mapped.")

        return mapped_records

    # --------------------------------------------------

    def map_all(self, parsed_datasets):

        logger.info("Mapping all datasets...")

        mapped = {}

        for dataset_name, records in parsed_datasets.items():

            mapped[dataset_name] = self.map_dataset(
                dataset_name,
                records
            )

        logger.info("All datasets mapped successfully.")

        return mapped