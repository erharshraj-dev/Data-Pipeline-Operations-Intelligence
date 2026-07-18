import logging

logger = logging.getLogger(__name__)


class BaselineComparator:
    """
    ==========================================================
    Baseline Comparator

    Responsibility:
        Compare current operational metrics with
        historical baseline metrics.

    Input:
        Operational Entity

    Output:
        Baseline Comparison Observation
    ==========================================================
    """

    def __init__(self):

        logger.info("Baseline Comparator Ready.")

    # ==========================================================
    # SAFE DEVIATION CALCULATION
    # ==========================================================

    def calculate_deviation(self, current, baseline):

        if baseline in (None, 0):
            return None

        return round(((current - baseline) / baseline) * 100, 2)

    # ==========================================================
    # COMPARE
    # ==========================================================

    def compare(self, entity):

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

        comparison = {}

        # ------------------------------------------------------
        # Runtime
        # ------------------------------------------------------

        current_runtime = attributes.get("elapsed_runtime")
        baseline_runtime = baseline.get("avg_runtime_sec")

        if current_runtime is not None and baseline_runtime is not None:

            deviation = self.calculate_deviation(
                current_runtime,
                baseline_runtime
            )

            comparison["runtime"] = {

                "current": current_runtime,

                "baseline": baseline_runtime,

                "deviation_percent": deviation,

                "status": self.get_status(deviation)

            }

        # ------------------------------------------------------
        # CPU
        # ------------------------------------------------------

        current_cpu = attributes.get("cpu_usage")
        baseline_cpu = baseline.get("avg_cpu")

        if current_cpu is not None and baseline_cpu is not None:

            deviation = self.calculate_deviation(
                current_cpu,
                baseline_cpu
            )

            comparison["cpu"] = {

                "current": current_cpu,

                "baseline": baseline_cpu,

                "deviation_percent": deviation,

                "status": self.get_status(deviation)

            }

        # ------------------------------------------------------
        # Memory
        # ------------------------------------------------------

        current_memory = attributes.get("memory_usage")
        baseline_memory = baseline.get("avg_memory")

        if current_memory is not None and baseline_memory is not None:

            deviation = self.calculate_deviation(
                current_memory,
                baseline_memory
            )

            comparison["memory"] = {

                "current": current_memory,

                "baseline": baseline_memory,

                "deviation_percent": deviation,

                "status": self.get_status(deviation)

            }

        # ------------------------------------------------------
        # Throughput
        # ------------------------------------------------------

        current_tp = attributes.get("throughput")
        baseline_tp = baseline.get("avg_throughput")

        if current_tp is not None and baseline_tp is not None:

            deviation = self.calculate_deviation(
                current_tp,
                baseline_tp
            )

            comparison["throughput"] = {

                "current": current_tp,

                "baseline": baseline_tp,

                "deviation_percent": deviation,

                "status": self.get_status(deviation)

            }

        return comparison

    # ==========================================================
    # STATUS
    # ==========================================================

    def get_status(self, deviation):

        if deviation is None:
            return "UNKNOWN"

        if abs(deviation) <= 10:
            return "NORMAL"

        elif abs(deviation) <= 30:
            return "WARNING"

        else:
            return "CRITICAL"