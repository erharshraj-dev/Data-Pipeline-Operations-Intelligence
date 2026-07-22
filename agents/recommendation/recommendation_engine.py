import logging

from agents.recommendation.recommendation_context_builder import (
    RecommendationContextBuilder
)
from agents.recommendation.priority_calculator import PriorityCalculator
from agents.recommendation.impact_estimator import ImpactEstimator

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    ==========================================================
    Recommendation Engine

    Responsibility:
        The deterministic analysis stage of the Recommendation
        Agent. Extracts recommendation context from the
        Behavior, Risk, and Integrity Objects and the
        Operational Entity, calculates priority, and estimates
        expected impact, recovery time, automation possibility,
        and human approval requirement — all before Gemini is
        ever involved.

    Input:
        Behavior Object, Risk Object, Integrity Object,
        Operational Entity (optional)

    Output:
        Recommendation Context Dictionary (context + priority
        + impact estimate, merged into one dict for the Prompt
        Builder and the fallback path to consume)

    DOES NOT
    --------
    - Retrieve knowledge
    - Call Gemini
    - Validate or build the final Recommendation Object
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        self.context_builder = RecommendationContextBuilder()

        self.priority_calculator = PriorityCalculator(rule_engine)

        self.impact_estimator = ImpactEstimator(rule_engine)

        logger.info("Recommendation Engine Ready.")

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(
        self,
        behavior_object,
        risk_object,
        integrity_object,
        operational_entity=None
    ):

        context = self.context_builder.build(

            behavior_object,

            risk_object,

            integrity_object,

            operational_entity

        )

        priority = self.priority_calculator.calculate(context)

        impact_estimate = self.impact_estimator.estimate(
            priority, context
        )

        context["priority"] = priority

        context.update(impact_estimate)

        return context
