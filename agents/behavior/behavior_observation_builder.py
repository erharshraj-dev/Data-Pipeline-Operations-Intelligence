import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BehaviorObservationBuilder:
    """
    -------------------------------------------------------
    Behavior Observation Builder

    Responsibility:
    Build the final Behavior Object from
    Observation Object + Behavior Analysis.

    Input:
        Observation Object
        Behavior Analysis Dictionary

    Output:
        Behavior Object
    -------------------------------------------------------
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Behavior Observation Builder Ready.")

    # =====================================================
    # BUILD BEHAVIOR OBJECT
    # =====================================================

    def build(self, observation_object, behavior_analysis):

        behavior_object = {

            "entity_id": observation_object.get("entity_id"),

            "entity_name": observation_object.get("entity_name"),

            "entity_type": observation_object.get("entity_type"),

            "source_system": observation_object.get("source_system"),

            "event_timestamp": observation_object.get("event_timestamp"),

            # Original Observation Object
            "observation": observation_object,

            # All Behavior Agent Outputs
            "behavior": behavior_analysis,

            # Metadata
            "metadata": {

                "agent": "Behavior Agent",

                "version": "1.0",

                "generated_at": datetime.now().isoformat()

            }

        }

        return behavior_object
