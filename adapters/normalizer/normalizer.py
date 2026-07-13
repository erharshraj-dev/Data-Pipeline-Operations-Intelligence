import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Normalizer:

    """
    Generic Data Normalizer

    Responsibilities
    ----------------
    1. Normalize execution status
    2. Normalize timestamps
    3. Normalize strings
    4. Normalize numeric values
    5. Preserve schema

    DOES NOT

    - Enrich data
    - Validate business rules
    - Remove fields
    """

    def __init__(self):

        logger.info("Normalizer Initialized.")

    ##########################################################
    # STATUS NORMALIZATION
    ##########################################################

    def normalize_status(self, status):

        if status is None:
            return None

        status = str(status).strip().upper()

        mapping = {

            "RUNNING": "RUNNING",
            "SUCCESS": "SUCCESS",
            "FAILED": "FAILED",
            "FAIL": "FAILED",
            "QUEUED": "QUEUED",
            "WAITING": "QUEUED",
            "PENDING": "PENDING",
            "ACTIVE": "RUNNING",
            "COMPLETED": "SUCCESS"

        }

        return mapping.get(status, status)

    ##########################################################
    # TIMESTAMP NORMALIZATION
    ##########################################################

    def normalize_timestamp(self, value):

        if value is None:
            return None

        formats = [

            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S"

        ]

        for fmt in formats:

            try:

                dt = datetime.strptime(str(value), fmt)

                return dt.isoformat()

            except:

                continue

        return value

    ##########################################################
    # STRING NORMALIZATION
    ##########################################################

    def normalize_string(self, value):

        if value is None:
            return None

        return str(value).strip()

    ##########################################################
    # NUMBER NORMALIZATION
    ##########################################################

    def normalize_number(self, value):

        if value is None:
            return None

        if isinstance(value, float):

            return round(value, 2)

        return value

    ##########################################################
    # RECORD NORMALIZATION
    ##########################################################

    def normalize_record(self, record):

        normalized = {}

        for key, value in record.items():

            # Status

            if key == "execution_status":

                normalized[key] = self.normalize_status(value)

            # Timestamp

            elif "time" in key.lower() or "timestamp" in key.lower():

                normalized[key] = self.normalize_timestamp(value)

            # Numbers

            elif isinstance(value, (int, float)):

                normalized[key] = self.normalize_number(value)

            # Strings

            elif isinstance(value, str):

                normalized[key] = self.normalize_string(value)

            else:

                normalized[key] = value

        return normalized

    ##########################################################
    # DATASET NORMALIZATION
    ##########################################################

    def normalize_dataset(self, dataset_name, records):

        logger.info(f"Normalizing dataset : {dataset_name}")

        normalized = []

        for record in records:

            normalized.append(

                self.normalize_record(record)

            )

        logger.info(f"{len(normalized)} records normalized.")

        return normalized

    ##########################################################
    # ALL DATASETS
    ##########################################################

    def normalize_all(self, mapped_data):

        logger.info("Normalizing all datasets...")

        normalized = {}

        for dataset_name, records in mapped_data.items():

            normalized[dataset_name] = self.normalize_dataset(

                dataset_name,

                records

            )

        logger.info("Normalization Completed.")

        return normalized