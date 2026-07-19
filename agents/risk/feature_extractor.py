import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    ==========================================================
    Feature Extractor

    Responsibility:
        Extract raw risk features from the Operational Entity,
        Observation Object, and Behavior Object produced by
        earlier pipeline stages. The Behavior Object nests the
        Observation Object, which in turn nests the
        Operational Entity, so a single Behavior Object gives
        access to all three.

        A feature is only included if the data needed to
        compute it was actually available — missing data is
        skipped, never guessed.

    Input:
        Behavior Object

    Output:
        Raw Feature Dictionary

    DOES NOT
    --------
    - Normalize features
    - Calculate risk score
    - Classify severity
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Feature Extractor Ready.")

    # =====================================================
    # WORST-CASE BEHAVIOR SEVERITY
    # =====================================================

    def extract_behavior_severity_label(self, behavior):

        deviation = behavior.get("deviation", {})

        if not deviation:

            return None

        severity_map = self.rule_engine.get_behavior_severity_map()

        worst_value = None
        worst_label = None

        for result in deviation.values():

            label = result.get("severity", "UNKNOWN")

            value = severity_map.get(label, 0.0)

            if worst_value is None or value > worst_value:

                worst_value = value
                worst_label = label

        return worst_label

    # =====================================================
    # MAX METRIC DEVIATION
    # =====================================================

    def extract_metric_deviation(self, behavior):

        deviation = behavior.get("deviation", {})

        deviations = [

            abs(result["deviation_percent"])

            for result in deviation.values()

            if result.get("deviation_percent") is not None

        ]

        if not deviations:

            return None

        return max(deviations)

    # =====================================================
    # ADVERSE TREND RATIO
    # =====================================================

    def extract_adverse_trend_ratio(self, observations):

        trend = observations.get("trend", {})

        if not trend:

            return None

        # Issue 4: adversity now depends on BOTH the metric
        # name and its direction (e.g. throughput increasing
        # is good, cpu_usage increasing is bad), rather than
        # treating every "Increasing"/"Decreasing" as adverse
        # regardless of which metric it belongs to.

        adverse_count = sum(

            1 for metric_name, direction in trend.items()

            if self.rule_engine.is_trend_adverse(
                metric_name, direction
            )

        )

        return adverse_count / len(trend)

    # =====================================================
    # BUSINESS CRITICALITY
    # =====================================================

    def extract_business_criticality(self, entity):

        business_context = entity.get(
            "context", {}
        ).get(
            "business_context", {}
        )

        criticality = business_context.get("criticality")

        if criticality is None:

            return None

        criticality_map = self.rule_engine.get_business_criticality_map()

        return criticality_map.get(criticality)

    # =====================================================
    # SLA MARGIN RATIO
    #
    # margin_ratio = (sla_minutes - elapsed_runtime) / sla_minutes
    #
    # NOTE: elapsed_runtime units are whatever the source
    # system reports (seconds for most sources, milliseconds
    # for Azure Data Factory). This ratio is only meaningful
    # for sources where elapsed_runtime is minutes-comparable;
    # it is a known limitation inherited from the upstream
    # mapping layer, not something this agent can correct.
    # =====================================================

    def extract_sla_margin_ratio(self, entity):

        business_context = entity.get(
            "context", {}
        ).get(
            "business_context", {}
        )

        attributes = entity.get("attributes", {})

        sla_minutes = business_context.get("sla_minutes")

        elapsed_runtime = attributes.get("elapsed_runtime")

        if sla_minutes in (None, 0) or elapsed_runtime is None:

            return None

        return (sla_minutes - elapsed_runtime) / sla_minutes

    # =====================================================
    # EXTRACT ALL FEATURES
    # =====================================================

    def extract(self, behavior_object):

        behavior = behavior_object.get("behavior", {})

        observation_object = behavior_object.get("observation", {})

        observations = observation_object.get("observations", {})

        entity = observation_object.get("entity", {})

        attributes = entity.get("attributes", {})

        incident_context = entity.get(
            "context", {}
        ).get(
            "incident_context", {}
        )

        features = {}

        # ------------------------------------------------
        # Behavior Agent derived features
        # ------------------------------------------------

        behavior_score = behavior.get("behavior_score")

        if behavior_score is not None:

            features["behavior_score"] = behavior_score

        behavior_severity_label = self.extract_behavior_severity_label(
            behavior
        )

        if behavior_severity_label is not None:

            severity_map = self.rule_engine.get_behavior_severity_map()

            features["behavior_severity"] = severity_map.get(
                behavior_severity_label, 0.0
            )

        # NOTE (Issue 2): behavior_confidence is intentionally
        # NOT extracted as a Risk Score feature here. It is a
        # measurement-quality signal, not an operational risk
        # signal, so it must not influence the weighted score.
        # It still reaches the Confidence Calculator directly
        # via behavior.get("confidence") in RiskPredictionAgent.

        metric_deviation = self.extract_metric_deviation(behavior)

        if metric_deviation is not None:

            features["metric_deviation"] = metric_deviation

        # ------------------------------------------------
        # Observer Agent derived features
        # ------------------------------------------------

        adverse_trend_ratio = self.extract_adverse_trend_ratio(
            observations
        )

        if adverse_trend_ratio is not None:

            features["adverse_trend_ratio"] = adverse_trend_ratio

        events = observations.get("events", [])

        features["event_count"] = len(events)

        # ------------------------------------------------
        # Operational Entity derived features
        # ------------------------------------------------

        incident_count = incident_context.get("total_incidents")

        if incident_count is not None:

            features["historical_incident_count"] = incident_count

        business_criticality = self.extract_business_criticality(entity)

        if business_criticality is not None:

            features["business_criticality"] = business_criticality

        sla_margin_ratio = self.extract_sla_margin_ratio(entity)

        if sla_margin_ratio is not None:

            features["sla_margin_ratio"] = sla_margin_ratio

        retry_count = attributes.get("retry_count")

        if retry_count is not None:

            features["retry_count"] = retry_count

        cpu_usage = attributes.get("cpu_usage")

        if cpu_usage is not None:

            features["cpu_usage"] = cpu_usage

        memory_usage = attributes.get("memory_usage")

        if memory_usage is not None:

            features["memory_usage"] = memory_usage

        execution_runtime = attributes.get("elapsed_runtime")

        if execution_runtime is not None:

            features["execution_runtime"] = execution_runtime

        return features
