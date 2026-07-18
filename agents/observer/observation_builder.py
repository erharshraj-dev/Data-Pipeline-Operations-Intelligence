import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ObservationBuilder:
    """
    -------------------------------------------------------
    Observation Builder

    Responsibility:
    Build the final Observation Object from
    Operational Entity + Observations.

    Input:
        Operational Entity
        Observation Dictionary

    Output:
        Observation Object
    -------------------------------------------------------
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Observation Builder Ready.")

    # =====================================================
    # BUILD OBSERVATION OBJECT
    # =====================================================

    def build(self, entity, observations):

        observation_object = {

            "entity_id": entity.get("entity_id"),

            "entity_name": entity.get("entity_name"),

            "entity_type": entity.get("entity_type"),

            "source_system": entity.get("source_system"),

            "event_timestamp": entity.get("event_timestamp"),

            # Original Operational Entity
            "entity": entity,

            # All Observer Outputs
            "observations": observations,

            # Metadata
            "metadata": {

                "agent": "Observer Agent",

                "version": "1.0",

                "generated_at": datetime.now().isoformat()

            }

        }

        return observation_object