import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StateDetector:
    """
    -------------------------------------------------------
    State Detector

    Responsibility:
    Observe the current execution state of an
    Operational Entity.

    Input:
        Operational Entity

    Output:
        Current State Observation
    -------------------------------------------------------
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.state_mapping = {

            "SUCCESS": "Healthy",
            "RUNNING": "Active",
            "FAILED": "Failure",
            "QUEUED": "Waiting",
            "CANCELLED": "Stopped"

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("State Detector Ready.")

    # =====================================================
    # DETECT CURRENT STATE
    # =====================================================

    def detect(self, entity):

        execution_status = entity.get(
            "execution_status",
            "UNKNOWN"
        )

        business_state = self.state_mapping.get(
            execution_status,
            "Unknown"
        )

        observation = {

            "current_state": execution_status,

            "business_state": business_state,

            "observed": True,

            "observation_type": "STATE",

            "observed_at": datetime.now().isoformat()

        }

        return observation