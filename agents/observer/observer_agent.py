import logging

from agents.observer.state_detector import StateDetector
from agents.observer.metric_observer import MetricObserver
from agents.observer.observation_builder import ObservationBuilder
from agents.observer.baseline_comparator import BaselineComparator
from agents.observer.trend_detector import TrendDetector
from agents.observer.event_correlator import EventCorrelator

logger = logging.getLogger(__name__)


class ObserverAgent:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Initializing Observer Agent...")

        self.state_detector = StateDetector()
        self.metric_observer = MetricObserver()
        self.observation_builder = ObservationBuilder()
        self.baseline_comparator = BaselineComparator()
        self.trend_detector = TrendDetector()
        self.event_correlator = EventCorrelator()

        self.total_entities = 0
        self.total_observations = 0

        logger.info("Observer Agent Ready.")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Running Observer Agent Health Check...")

        self.state_detector.health_check()

        logger.info("Metric Observer Ready.")

        logger.info("Observation Builder Ready.")

        logger.info("Observer Agent Health Check PASSED.")
        logger.info("Baseline Comparator Ready.")
        logger.info("Trend Detector Ready.")
        logger.info("Event Correlator Ready.")

    # =====================================================
    # OBSERVE SINGLE ENTITY
    # =====================================================
    
    def observe_entity(self, entity):

        observations = {

            "state": self.state_detector.detect(entity),

            "metrics": self.metric_observer.observe(entity),

            "baseline": self.baseline_comparator.compare(entity),

            "trend": self.trend_detector.detect(entity),

            "events": self.event_correlator.correlate(entity)
        }

        observation_object = self.observation_builder.build(

            entity,

            observations

        )
        return observation_object

    # =====================================================
    # OBSERVE DATASET
    # =====================================================

    def observe_dataset(self, records):

        observation_objects = []

        for entity in records:

            observation_objects.append(

                self.observe_entity(entity)

            )

        return observation_objects

    # =====================================================
    # OBSERVE ALL DATASETS
    # =====================================================

    def observe_all(self, operational_entities):

        logger.info("Generating Observation Objects...")

        observation_objects = {}

        self.total_entities = 0
        self.total_observations = 0

        for dataset_name, records in operational_entities.items():

            logger.info(f"Observing Dataset : {dataset_name}")

            dataset_observations = self.observe_dataset(records)

            observation_objects[dataset_name] = dataset_observations

            self.total_entities += len(records)

            self.total_observations += len(dataset_observations)

        logger.info(
            f"Operational Entities Received : {self.total_entities}"
        )

        logger.info(
            f"Observation Objects Generated : {self.total_observations}"
        )

        logger.info("Observer Agent Completed Successfully.")

        return observation_objects

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        return {
            "operational_entities": self.total_entities,
            "observation_objects": self.total_observations
        }