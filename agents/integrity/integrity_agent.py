import logging
import time

from agents.integrity.integrity_rule_engine import IntegrityRuleEngine
from agents.integrity.integrity_feature_extractor import (
    IntegrityFeatureExtractor
)
from agents.integrity.integrity_validator import IntegrityValidator
from agents.integrity.integrity_score_calculator import (
    IntegrityScoreCalculator
)
from agents.integrity.integrity_status_classifier import (
    IntegrityStatusClassifier
)
from agents.integrity.integrity_object_builder import (
    IntegrityObjectBuilder
)

logger = logging.getLogger(__name__)


class IntegrityAgent:
    """
    ==========================================================
    Integrity Agent

    Responsibility:
        Validate output correctness, data quality, business
        rule compliance, and lineage completeness for each
        Operational Entity, and determine whether downstream
        consumers (starting with the future Recommendation
        Agent) can trust the produced data.

    Input:
        Observation Object
        Operational Entity (optional — the Observation Object
        already carries it under "entity"; see
        evaluate_integrity() for when to pass this explicitly)

    Output:
        Integrity Object

    DOES NOT
    --------
    - Detect anomalies
    - Predict future risk
    - Generate recommendations
    - Perform root cause analysis
    - Modify pipeline execution
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file="config/integrity_rules.yaml"):

        logger.info("Initializing Integrity Agent...")

        self.rule_engine = IntegrityRuleEngine(config_file)

        self.feature_extractor = IntegrityFeatureExtractor(
            self.rule_engine
        )

        self.validator = IntegrityValidator(self.rule_engine)

        self.score_calculator = IntegrityScoreCalculator(
            self.rule_engine
        )

        self.status_classifier = IntegrityStatusClassifier(
            self.rule_engine
        )

        self.integrity_object_builder = IntegrityObjectBuilder(
            self.rule_engine.get_agent_version()
        )

        self.total_observations = 0
        self.total_integrities = 0

        logger.info("Integrity Agent Ready.")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Running Integrity Agent Health Check...")

        self.rule_engine.health_check()

        logger.info("Integrity Feature Extractor Ready.")
        logger.info("Integrity Validator Ready.")
        logger.info("Integrity Score Calculator Ready.")
        logger.info("Integrity Status Classifier Ready.")
        logger.info("Integrity Object Builder Ready.")

        logger.info("Integrity Agent Health Check PASSED.")

    # =====================================================
    # EVALUATE SINGLE ENTITY
    # =====================================================

    def evaluate_integrity(self, observation_object, operational_entity=None):
        """
        operational_entity is optional. The Observation Object
        already carries the Operational Entity under
        observation_object["entity"], so passing this is only
        necessary when evaluating against a different or
        overridden entity than the one embedded — the default
        behavior (and every existing call site) is unaffected.
        """

        start_time = time.perf_counter()

        entity = (
            operational_entity
            if operational_entity is not None
            else observation_object.get("entity", {})
        )

        signals = self.feature_extractor.extract(
            observation_object, entity
        )

        validation_results = self.validator.validate_all(signals)

        integrity_score = self.score_calculator.calculate(
            validation_results
        )

        integrity_status = self.status_classifier.classify_status(
            integrity_score
        )

        output_trust_level = self.status_classifier.classify_trust_level(
            integrity_score
        )

        primary_failure_reason = (
            self.status_classifier.determine_primary_failure(
                validation_results
            )
        )

        execution_time_ms = round(
            (time.perf_counter() - start_time) * 1000, 3
        )

        integrity_object = self.integrity_object_builder.build(

            observation_object,

            validation_results,

            integrity_score,

            integrity_status,

            output_trust_level,

            primary_failure_reason,

            execution_time_ms

        )

        return integrity_object

    # =====================================================
    # EVALUATE DATASET
    # =====================================================

    def evaluate_dataset(self, observation_objects):

        integrity_objects = []

        for observation_object in observation_objects:

            integrity_objects.append(
                self.evaluate_integrity(observation_object)
            )

        return integrity_objects

    # =====================================================
    # EVALUATE ALL DATASETS
    # =====================================================

    def evaluate_all(self, observation_objects_by_dataset):

        logger.info("Generating Integrity Objects...")

        integrity_objects = {}

        self.total_observations = 0
        self.total_integrities = 0

        for dataset_name, observations in (
            observation_objects_by_dataset.items()
        ):

            logger.info(f"Evaluating Integrity : {dataset_name}")

            dataset_integrities = self.evaluate_dataset(observations)

            integrity_objects[dataset_name] = dataset_integrities

            self.total_observations += len(observations)

            self.total_integrities += len(dataset_integrities)

        logger.info(
            f"Observation Objects Received : {self.total_observations}"
        )

        logger.info(
            f"Integrity Objects Generated : {self.total_integrities}"
        )

        logger.info("Integrity Agent Completed Successfully.")

        return integrity_objects

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print("\n")
        print("=" * 70)
        print("INTEGRITY AGENT SUMMARY")
        print("=" * 70)

        print(f"Observation Objects : {self.total_observations}")
        print(f"Integrity Objects   : {self.total_integrities}")

        print("=" * 70)
