import logging

logger = logging.getLogger(__name__)


class TrendDetector:

    def __init__(self):

        logger.info("Trend Detector Ready.")

    def detect(self, entity):

        trends = {}

        baseline = entity.get(
            "context",
            {}
        ).get(
            "historical_context",
            {}
        )

        attributes = entity.get(
            "attributes",
            {}
        )

        # ---------------------------------------
        # Runtime Trend
        # ---------------------------------------

        current_runtime = attributes.get("elapsed_runtime")
        baseline_runtime = baseline.get("avg_runtime_sec")

        if current_runtime is not None and baseline_runtime is not None:

            if current_runtime > baseline_runtime:

                trends["runtime"] = "Increasing"

            elif current_runtime < baseline_runtime:

                trends["runtime"] = "Decreasing"

            else:

                trends["runtime"] = "Stable"

        # ---------------------------------------
        # CPU Trend
        # ---------------------------------------

        current_cpu = attributes.get("cpu_usage")
        baseline_cpu = baseline.get("avg_cpu")

        if current_cpu is not None and baseline_cpu is not None:

            if current_cpu > baseline_cpu:

                trends["cpu_usage"] = "Increasing"

            elif current_cpu < baseline_cpu:

                trends["cpu_usage"] = "Decreasing"

            else:

                trends["cpu_usage"] = "Stable"

        # ---------------------------------------
        # Memory Trend
        # ---------------------------------------

        current_memory = attributes.get("memory_usage")
        baseline_memory = baseline.get("avg_memory")

        if current_memory is not None and baseline_memory is not None:

            if current_memory > baseline_memory:

                trends["memory_usage"] = "Increasing"

            elif current_memory < baseline_memory:

                trends["memory_usage"] = "Decreasing"

            else:

                trends["memory_usage"] = "Stable"

        # ---------------------------------------
        # Throughput Trend
        # ---------------------------------------

        current_tp = attributes.get("throughput")
        baseline_tp = baseline.get("avg_throughput")

        if current_tp is not None and baseline_tp is not None:

            if current_tp > baseline_tp:

                trends["throughput"] = "Increasing"

            elif current_tp < baseline_tp:

                trends["throughput"] = "Decreasing"

            else:

                trends["throughput"] = "Stable"

        return trends