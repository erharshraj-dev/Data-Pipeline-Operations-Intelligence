import logging

logger = logging.getLogger(__name__)


class FeatureNormalizer:
    """
    ==========================================================
    Feature Normalizer

    Responsibility:
        Normalize every raw feature value onto a common 0-1
        scale, using the min/max bounds and invert flag
        configured per feature in risk_rules.yaml.

    Input:
        Raw Feature Dictionary

    Output:
        Normalized Feature Dictionary

    DOES NOT
    --------
    - Extract features
    - Calculate weighted risk score
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Feature Normalizer Ready.")

    # =====================================================
    # NORMALIZE ONE VALUE
    # =====================================================

    def normalize_value(self, value, feature_config):

        min_value = feature_config.get("min", 0)

        max_value = feature_config.get("max", 1)

        invert = feature_config.get("invert", False)

        if max_value == min_value:

            return 0.0

        clipped = max(min_value, min(value, max_value))

        normalized = (clipped - min_value) / (max_value - min_value)

        if invert:

            normalized = 1.0 - normalized

        return round(normalized, 4)

    # =====================================================
    # NORMALIZE ALL
    # =====================================================

    def normalize(self, raw_features, source_system=None):

        # Issue 3: passing source_system selects the matching
        # normalization_profiles entry (falling back to
        # "default", then to the base bounds) so a single
        # feature like execution_runtime can use domain-
        # appropriate min/max instead of one hardcoded bound
        # shared across every platform. Omitting source_system
        # keeps the original, profile-less behavior.

        feature_definitions = self.rule_engine.get_feature_definitions(
            source_system
        )

        normalized_features = {}

        for feature_name, value in raw_features.items():

            feature_config = feature_definitions.get(feature_name)

            if feature_config is None:

                continue

            normalized_features[feature_name] = self.normalize_value(

                value,

                feature_config

            )

        return normalized_features
