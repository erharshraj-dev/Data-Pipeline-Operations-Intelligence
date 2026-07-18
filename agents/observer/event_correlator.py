import logging

logger = logging.getLogger(__name__)


class EventCorrelator:

    def __init__(self):

        logger.info("Event Correlator Ready.")

    def correlate(self, entity):

        events = []

        attributes = entity.get("attributes", {})

        state = entity.get("execution_status", "")

        # --------------------------------------------------
        # Execution Status
        # --------------------------------------------------

        if state == "FAILED":
            events.append("Execution Failure")

        elif state == "RUNNING":
            events.append("Pipeline Running")

        elif state == "QUEUED":
            events.append("Pipeline Waiting")

        elif state == "CANCELLED":
            events.append("Pipeline Cancelled")

        # --------------------------------------------------
        # Temperature
        # --------------------------------------------------

        temperature = attributes.get("temperature")

        if temperature is not None and temperature > 45:
            events.append("High Temperature")

        elif temperature is not None and temperature < 0:
            events.append("Low Temperature")

        # --------------------------------------------------
        # Humidity
        # --------------------------------------------------

        humidity = attributes.get("humidity")

        if humidity is not None and humidity > 90:
            events.append("High Humidity")

        # --------------------------------------------------
        # Battery
        # --------------------------------------------------

        battery = attributes.get("battery_level")

        if battery is not None and battery < 20:
            events.append("Low Battery")

        # --------------------------------------------------
        # Signal Strength
        # --------------------------------------------------

        signal = attributes.get("signal_strength")

        if signal is not None and signal < -85:
            events.append("Weak Signal")

        return events