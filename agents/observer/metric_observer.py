import logging

logger = logging.getLogger(__name__)


class MetricObserver:

    def __init__(self):

        logger.info("Metric Observer Ready.")

    def observe(self, entity):

        metrics = {}

        attributes = entity.get("attributes", {})

        metric_fields = [

            "elapsed_runtime",
            "runtime",
            "cpu_usage",
            "memory_usage",
            "throughput",
            "consumer_lag",
            "retry_count",
            "temperature",
            "battery_level",
            "defect_count"

        ]

        for field in metric_fields:

            if field in attributes:

                metrics[field] = attributes[field]

        return metrics