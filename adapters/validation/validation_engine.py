import logging
from datetime import datetime
from pyexpat import errors

logger = logging.getLogger(__name__)


class ValidationEngine:

    def __init__(self):

        logger.info("Initializing Validation Engine...")

        # Required Canonical Fields
        self.required_fields = [

            "entity_id",
            "entity_name",
            "entity_type",
            "source_system",
            "execution_status",
            "event_timestamp"

        ]

        # Allowed Status Values
        self.allowed_status = {

            "SUCCESS",
            "FAILED",
            "RUNNING",
            "QUEUED",
            "CANCELLED"

        }

        # Expected Datatypes
        self.expected_types = {

            "entity_id": str,
            "entity_name": str,
            "entity_type": str,
            "source_system": str,
            "execution_status": str,
            "event_timestamp": str,

            "elapsed_runtime": (int, float),
            "retry_count": int,
            "cpu_usage": (int, float),
            "memory_usage": (int, float),
            "battery_level": (int, float),
            "temperature": (int, float),
            "throughput": (int, float),
            "consumer_lag": (int, float)

        }

        logger.info("Validation Engine Ready.")
        ##########################################################
        # RANGE RULES
            ##########################################################

        self.range_rules = {

        "cpu_usage": (0, 100),

        "memory_usage": (0, 100),

        "battery_level": (0, 100),

        "temperature": (-50, 150),

        "retry_count": (0, 20),

        "consumer_lag": (0, 1000000),

        "throughput": (0, 100000000),

        "elapsed_runtime": (0, 86400)

    }
    ##########################################################
    # DUPLICATE TRACKER
    ##########################################################

        self.seen_entities = set()

        logger.info("Validation Engine Ready.")
    ##########################################################
    # HEALTH CHECK
    ##########################################################

    def health_check(self):

        logger.info("Running Validation Engine Health Check...")

        print()

        print("Required Fields :", len(self.required_fields))

        print("Datatype Rules :", len(self.expected_types))

        print("Allowed Status :", self.allowed_status)

        print()

        logger.info("Validation Engine Health Check PASSED.")

        return True

    ##########################################################
    # REQUIRED FIELD VALIDATION
    ##########################################################

    def validate_required_fields(self, record):

        errors = []

        for field in self.required_fields:

            if field not in record:

                errors.append(f"Missing Field : {field}")

            elif record[field] is None:

                errors.append(f"Null Value : {field}")

            elif record[field] == "":

                errors.append(f"Empty Value : {field}")

        return errors

    ##########################################################
    # DATATYPE VALIDATION
    ##########################################################

    def validate_datatypes(self, record):

        errors = []

        for field, datatype in self.expected_types.items():

            if field not in record:

                continue

            value = record[field]

            if value is None:

                continue

            if not isinstance(value, datatype):

                errors.append(

                    f"{field} should be {datatype}"

                )

        return errors

    ##########################################################
    # STATUS ENUM VALIDATION
    ##########################################################

    def validate_status(self, record):

        errors = []

        status = record.get("execution_status")

        if status is None:

            return errors

        if status not in self.allowed_status:

            errors.append(

                f"Invalid execution_status : {status}"

            )

        return errors

    ##########################################################
    # TIMESTAMP VALIDATION
    ##########################################################

    def validate_timestamp(self, record):

        errors = []

        timestamp = record.get("event_timestamp")

        if timestamp is None:

            return errors

        try:

            datetime.fromisoformat(timestamp)

        except Exception:

            errors.append(

                f"Invalid Timestamp : {timestamp}"

            )

        return errors
    ##########################################################
    # RANGE VALIDATION
    ##########################################################

    def validate_ranges(self, record):

        errors = []

        for field, (minimum, maximum) in self.range_rules.items():

            if field not in record:
                continue

            value = record[field]

            if value is None:
                continue

            if value < minimum or value > maximum:

                errors.append(

                    f"{field} out of range ({value})"

                )

            return errors

    ##########################################################
    # BUSINESS RULE VALIDATION
    ##########################################################

    def validate_business_rules(self, record):

        errors = []

        runtime = record.get("elapsed_runtime")

        if runtime is not None and runtime < 0:

            errors.append("Negative Runtime")

        retry = record.get("retry_count")

        if retry is not None and retry < 0:

            errors.append("Negative Retry Count")

        throughput = record.get("throughput")

        if throughput is not None and throughput < 0:

            errors.append("Negative Throughput")

        return errors

    ##########################################################
    # CONTEXT VALIDATION
    ##########################################################

    def validate_context(self, record):

        warnings = []

        contexts = [

            "business_context",

            "historical_context",

            "incident_context",

            "lineage_context",

            "recommendation_context"
        ]

        for context in contexts:

            if not record.get(context):

                warnings.append(

                    f"{context} missing"

             )

        return warnings

##########################################################
# CONTEXT VALIDATION
##########################################################

    def validate_context(self, record):

        warnings = []

        contexts = [

            "business_context",

            "historical_context",

            "incident_context",

            "lineage_context",

            "recommendation_context"

        ]

        for context in contexts:

            if not record.get(context):

                warnings.append(

                    f"{context} missing"

                )

        return warnings
    
    ##########################################################
# DUPLICATE VALIDATION
##########################################################

    def validate_duplicate(self, record):

        errors = []

        entity = record.get("entity_id")

        if entity in self.seen_entities:

            errors.append(
                f"Duplicate Entity : {entity}"
            )

        else:

            self.seen_entities.add(entity)

        return errors

##########################################################
# QUALITY SCORE
##########################################################

    def calculate_score(self, errors, warnings):

        score = 100

        score -= len(errors) * 10

        score -= len(warnings) * 2

        if score < 0:

            score = 0

        return score
    
    ##########################################################
# VALIDATE SINGLE RECORD
##########################################################

    def validate_record(self, record):

        errors = []
        warnings = []

        # Required Fields
        errors.extend(
            self.validate_required_fields(record)
        )

        # Datatypes
        errors.extend(
            self.validate_datatypes(record)
        )

        # Status
        errors.extend(
            self.validate_status(record)
        )

        # Timestamp
        errors.extend(
            self.validate_timestamp(record)
        )

        # Numeric Ranges
        errors.extend(
            self.validate_ranges(record)
        )

        # Business Rules
        errors.extend(
            self.validate_business_rules(record)
        )

        # Duplicate Detection
        errors.extend(
        self.validate_duplicate(record)
        )

        # Context Validation
        warnings.extend(
            self.validate_context(record)
        )

        score = self.calculate_score(
            errors,
            warnings
        )

        validated_record = record.copy()

        validated_record["validation_score"] = score
        validated_record["errors"] = errors
        validated_record["warnings"] = warnings
        validated_record["is_valid"] = len(errors) == 0

        return validated_record
    
    ##########################################################
    # VALIDATE DATASET
    ##########################################################

    def validate_dataset(self, dataset_name, records):

        logger.info(f"Validating Dataset : {dataset_name}")

        validated = []

        valid_count = 0
        invalid_count = 0

        for record in records:

            result = self.validate_record(record)

            if result["is_valid"]:
                valid_count += 1
            else:
                invalid_count += 1

            validated.append(result)

        logger.info(
            f"{dataset_name} -> "
            f"Valid : {valid_count} | "
            f"Invalid : {invalid_count}"
        )

        return validated
    
    ##########################################################
# VALIDATE ALL DATASETS
##########################################################

    def validate_all(self, enriched_data):

        logger.info("Starting Validation Engine...")

        validated_data = {}

        for dataset_name, records in enriched_data.items():

            validated_data[dataset_name] = self.validate_dataset(

                dataset_name,

                records

            )

        logger.info("Validation Engine Completed.")

        return validated_data