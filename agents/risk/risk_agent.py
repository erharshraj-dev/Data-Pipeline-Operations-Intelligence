import logging

from agents.risk.risk_rule_engine import RiskRuleEngine
from agents.risk.feature_extractor import FeatureExtractor
from agents.risk.feature_normalizer import FeatureNormalizer
from agents.risk.risk_score_calculator import RiskScoreCalculator
from agents.risk.severity_classifier import SeverityClassifier
from agents.risk.category_classifier import CategoryClassifier
from agents.risk.probability_calculator import ProbabilityCalculator
from agents.risk.confidence_calculator import ConfidenceCalculator
from agents.risk.risk_object_builder import RiskObjectBuilder

logger = logging.getLogger(__name__)


class RiskPredictionAgent:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, config_file="config/risk_rules.yaml"):

        logger.info("Initializing Risk Prediction Agent...")

        self.rule_engine = RiskRuleEngine(config_file)

        self.feature_extractor = FeatureExtractor(self.rule_engine)

        self.feature_normalizer = FeatureNormalizer(self.rule_engine)

        self.risk_score_calculator = RiskScoreCalculator(self.rule_engine)

        self.severity_classifier = SeverityClassifier(self.rule_engine)

        self.category_classifier = CategoryClassifier(self.rule_engine)

        self.probability_calculator = ProbabilityCalculator(
            self.rule_engine
        )

        self.confidence_calculator = ConfidenceCalculator(self.rule_engine)

        self.risk_object_builder = RiskObjectBuilder()

        self.total_behaviors = 0
        self.total_risks = 0

        logger.info("Risk Prediction Agent Ready.")

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Running Risk Prediction Agent Health Check...")

        self.rule_engine.health_check()

        logger.info("Feature Extractor Ready.")
        logger.info("Feature Normalizer Ready.")
        logger.info("Risk Score Calculator Ready.")
        logger.info("Severity Classifier Ready.")
        logger.info("Category Classifier Ready.")
        logger.info("Probability Calculator Ready.")
        logger.info("Confidence Calculator Ready.")
        logger.info("Risk Object Builder Ready.")

        logger.info("Risk Prediction Agent Health Check PASSED.")

    # =====================================================
    # PREDICT SINGLE RISK
    # =====================================================

    def predict_risk(self, behavior_object):

        behavior = behavior_object.get("behavior", {})

        source_system = behavior_object.get("source_system")

        raw_features = self.feature_extractor.extract(behavior_object)

        # Issue 3: source_system selects the matching
        # normalization profile (e.g. Azure Data Factory's
        # millisecond execution_runtime vs. Airflow's seconds).

        normalized_features = self.feature_normalizer.normalize(
            raw_features,
            source_system
        )

        risk_score = self.risk_score_calculator.calculate(
            normalized_features
        )

        risk_severity = self.severity_classifier.classify(risk_score)

        # Issue 1: Risk Category now describes the TYPE of risk
        # (Pipeline Failure, SLA Breach, ...) via its own
        # rule-based classifier, evaluated independently of
        # Risk Score / Risk Severity rather than derived from
        # the severity label.

        risk_category = self.category_classifier.classify(
            behavior_object
        )

        risk_probability = self.probability_calculator.calculate(
            risk_score
        )

        prediction_confidence = self.confidence_calculator.calculate(

            raw_features,

            behavior.get("confidence")

        )

        risk_analysis = {

            "risk_score": risk_score,

            "risk_severity": risk_severity,

            "risk_category": risk_category,

            "risk_probability": risk_probability,

            "prediction_confidence": prediction_confidence

        }

        risk_object = self.risk_object_builder.build(

            behavior_object,

            risk_analysis

        )

        return risk_object

    # =====================================================
    # PREDICT DATASET
    # =====================================================

    def predict_dataset(self, behavior_objects):

        risk_objects = []

        for behavior_object in behavior_objects:

            risk_objects.append(

                self.predict_risk(behavior_object)

            )

        return risk_objects

    # =====================================================
    # PREDICT ALL DATASETS
    # =====================================================

    def predict_all(self, behavior_objects_by_dataset):

        logger.info("Generating Risk Objects...")

        risk_objects = {}

        self.total_behaviors = 0
        self.total_risks = 0

        for dataset_name, behaviors in behavior_objects_by_dataset.items():

            logger.info(f"Predicting Risk : {dataset_name}")

            dataset_risks = self.predict_dataset(behaviors)

            risk_objects[dataset_name] = dataset_risks

            self.total_behaviors += len(behaviors)

            self.total_risks += len(dataset_risks)

        logger.info(
            f"Behavior Objects Received : {self.total_behaviors}"
        )

        logger.info(
            f"Risk Objects Generated : {self.total_risks}"
        )

        logger.info("Risk Prediction Agent Completed Successfully.")

        return risk_objects

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print("\n")
        print("=" * 70)
        print("RISK PREDICTION AGENT SUMMARY")
        print("=" * 70)

        print(f"Behavior Objects : {self.total_behaviors}")
        print(f"Risk Objects     : {self.total_risks}")

        print("=" * 70)
