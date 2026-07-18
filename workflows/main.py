import logging
import json
import os
import time

from adapters.connectors.csv_connector import CSVConnector
from adapters.parsers.tabular_parser import TabularParser
from adapters.mapping.mapping_engine import MappingEngine
from adapters.normalizer.normalizer import Normalizer
from adapters.enricher.context_enricher import ContextEnricher
from adapters.validation.validation_engine import ValidationEngine
from adapters.entity_builder.operational_entity_builder import OperationalEntityBuilder
from agents.observer.observer_agent import ObserverAgent
from agents.behavior.behavior_agent import BehaviorAgent

# ==========================================================
# Logging Configuration
# ==========================================================

LOG_LEVEL = os.getenv("AIF_LOG_LEVEL", "WARNING").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),
    format="%(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# MAIN
# ==========================================================

def main():

    start_time = time.perf_counter()

    print_workflow_banner()

    # ======================================================
    # STEP 1 : CSV CONNECTOR
    # ======================================================

    logger.debug("Starting capability adapter execution.")

    connector = CSVConnector("config/sources.yaml")

    connector.connect()

    datasets = connector.read_all()

    connector.disconnect()

    # ======================================================
    # Separate Raw Sources & Lookup Tables
    # ======================================================

    raw_dataset_names = [

        "airflow",
        "kafka",
        "kubernetes",
        "azure_data_factory",
        "sap",
        "manufacturing",
        "iot"

    ]

    lookup_dataset_names = [

        "business_context",
        "historical_baselines",
        "incident_history",
        "pipeline_lineage",
        "recommendation_history"

    ]

    raw_datasets = {

        name: datasets[name]

        for name in raw_dataset_names

    }

    lookup_datasets = {

        name: datasets[name]

        for name in lookup_dataset_names

    }

    logger.debug(f"Raw Datasets Loaded    : {len(raw_datasets)}")
    logger.debug(f"Lookup Datasets Loaded : {len(lookup_datasets)}")

    # ======================================================
    # STEP 2 : TABULAR PARSER
    # ======================================================

    parser = TabularParser()

    parsed_raw = parser.parse_all(raw_datasets)

    parsed_lookup = parser.parse_all(lookup_datasets)

    logger.debug("Parsing completed successfully.")

    # ======================================================
    # STEP 3 : MAPPING ENGINE
    # ======================================================

    mapper = MappingEngine("config/mapping.yaml")

    mapped_data = mapper.map_all(parsed_raw)

    logger.debug("Mapping completed successfully.")

    # ======================================================
    # STEP 4 : NORMALIZER
    # ======================================================

    normalizer = Normalizer()

    normalized_data = normalizer.normalize_all(mapped_data)

    logger.debug("Normalization completed successfully.")

    # ======================================================
    # STEP 5 : CONTEXT ENRICHER
    # ======================================================

    enricher = ContextEnricher(parsed_lookup)

    if hasattr(enricher, "health_check"):
        enricher.health_check()

    enriched_data = enricher.enrich_all(normalized_data)

    logger.debug("Context enrichment completed successfully.")

    # ======================================================
    # STEP 6 : VALIDATION ENGINE
    # ======================================================

    validator = ValidationEngine()

    validator.health_check()

    validation_results = validator.validate_all(enriched_data)

    logger.debug("Validation completed successfully.")

    # ======================================================
    # STEP 7 : OPERATIONAL ENTITY BUILDER
    # ======================================================

    entity_builder = OperationalEntityBuilder()

    operational_entities = entity_builder.build_all(
        validation_results
    )

    total_entities = sum(len(v) for v in operational_entities.values())
    logger.debug(f"Operational Entities Generated : {total_entities}")

    observer = ObserverAgent()

    observer.health_check()

    observation_objects = observer.observe_all(
        operational_entities
    )

    behavior_agent = BehaviorAgent("config/behavior_rules.yaml")
    behavior_agent.health_check()

    behavior_objects = behavior_agent.analyze_all(observation_objects)

    adapter_summary = {
        "data_sources_loaded": len(datasets),
        "raw_datasets": len(raw_datasets),
        "lookup_datasets": len(lookup_datasets),
        "parsed_raw_records": sum(len(records) for records in parsed_raw.values()),
        "parsed_lookup_records": sum(len(records) for records in parsed_lookup.values()),
        "mapped_records": sum(len(records) for records in mapped_data.values()),
        "normalized_records": sum(len(records) for records in normalized_data.values()),
        "validated_records": sum(len(records) for records in validation_results.values()),
        "operational_entities": total_entities
    }

    observer_summary = observer.summary()

    behavior_summary = behavior_agent.summary()

    representative_flow = build_representative_flow(
        operational_entities,
        observation_objects,
        behavior_objects
    )

    # ======================================================
    # EXECUTION OUTPUT
    # ======================================================

    execution_output = {
        "adapter_output": {
            "parsed_raw": parsed_raw,
            "parsed_lookup": parsed_lookup,
            "mapped_data": mapped_data,
            "normalized_data": normalized_data,
            "enriched_data": enriched_data,
            "validation_results": validation_results
        },
        "operational_entity": operational_entities,
        "observer_output": observation_objects,
        "behavior_output": behavior_objects
    }

    output_dir = "output"
    output_path = os.path.join(output_dir, "execution_output.json")

    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(execution_output, file, indent=2, default=str)

    execution_time = round(time.perf_counter() - start_time, 2)

    print_execution_summary(
        adapter_summary,
        observer_summary,
        behavior_summary,
        representative_flow,
        execution_time,
        output_path
    )

    logger.debug("Output saved")


def build_representative_flow(operational_entities, observation_objects, behavior_objects):

    dataset_name = "kafka" if "kafka" in operational_entities else next(iter(operational_entities))

    representative_entity = operational_entities[dataset_name][0]
    representative_entity_id = representative_entity.get("entity_id")

    representative_observation = next(
        observation
        for observation in observation_objects[dataset_name]
        if observation.get("entity_id") == representative_entity_id
    )

    representative_behavior = next(
        behavior
        for behavior in behavior_objects[dataset_name]
        if behavior.get("entity_id") == representative_entity_id
    )

    observation_state = representative_observation.get("observations", {}).get("state", {})
    observation_metrics = representative_observation.get("observations", {}).get("metrics", {})
    observation_baseline = representative_observation.get("observations", {}).get("baseline", {})
    observation_trend = representative_observation.get("observations", {}).get("trend", {})
    observation_events = representative_observation.get("observations", {}).get("events", [])

    behavior_analysis = representative_behavior.get("behavior", {})

    return {
        "dataset_name": dataset_name,
        "entity": representative_entity,
        "observation": representative_observation,
        "behavior": representative_behavior,
        "observation_state": observation_state,
        "observation_metrics": observation_metrics,
        "observation_baseline": observation_baseline,
        "observation_trend": observation_trend,
        "observation_events": observation_events,
        "behavior_analysis": behavior_analysis,
    }


def print_execution_summary(
    adapter_summary,
    observer_summary,
    behavior_summary,
    representative_flow,
    execution_time,
    output_path
):

    print_capability_adapter_summary(adapter_summary, representative_flow)
    print_observer_summary(observer_summary, representative_flow)
    print_behavior_summary(behavior_summary, representative_flow)
    print_footer_summary(
        adapter_summary,
        observer_summary,
        behavior_summary,
        execution_time,
        output_path
    )


def print_workflow_banner():

    print("=" * 80)
    print("                ADAPTIVE INTELLIGENCE FABRIC (AIF)")
    print("=" * 80)
    print("Capability Adapter")
    print("        ↓")
    print("Operational Entity")
    print("        ↓")
    print("Observer Agent")
    print("        ↓")
    print("Observation Object")
    print("        ↓")
    print("Behavior Agent")
    print("        ↓")
    print("Behavior Object")
    print("=" * 80)


def print_pipeline_footer():

    print()
    print("=" * 80)
    print("AIF PIPELINE EXECUTED SUCCESSFULLY")
    print("=" * 80)


def print_section_header(step_number, title):

    print()
    print(f"STEP {step_number} : {title}")
    print("-" * 80)


def print_label(label, value, width=22):

    print(f"{label:<{width}} : {value}")


def format_inline_pairs(data, preferred_keys=None):

    if not data:

        return "None"

    items = []

    if preferred_keys:

        for key in preferred_keys:

            if key in data and data[key] is not None:

                items.append(f"{key}={data[key]}")

    else:

        for key, value in data.items():

            if value is not None:

                items.append(f"{key}={value}")

    return ", ".join(items) if items else "None"


def format_list_values(values):

    if not values:

        return "None"

    return ", ".join(str(value) for value in values)


def format_status_count(value):

    return value if value is not None else "None"


def print_footer_summary(
    adapter_summary,
    observer_summary,
    behavior_summary,
    execution_time,
    output_path
):

    print()
    print("=" * 80)
    print("Execution Output Saved")
    print("=" * 80)
    print()
    print("Capability Adapter")
    print_label("Operational Entities Created", adapter_summary["operational_entities"], 30)
    print()
    print("Observer Agent")
    print_label("Observation Objects Created", observer_summary["observation_objects"], 30)
    print()
    print("Behavior Agent")
    print_label("Behavior Objects Created", behavior_summary["behavior_objects"], 30)
    print()
    print_label("Execution Status", "SUCCESS", 30)
    print_label("Execution Time", f"{execution_time:.2f} seconds", 30)
    print()
    print("Output File")
    print_label("Path", output_path, 30)
    print()
    print("=" * 80)


def print_reasons(reasons):

    for reason in reasons:

        print(f"• {reason}")


def print_capability_adapter_summary(adapter_summary, representative_flow):

    print_section_header(1, "CAPABILITY ADAPTER")
    print("Input")
    print("------")
    print_label("Data Sources Loaded", adapter_summary["data_sources_loaded"])
    print_label("Raw Datasets", adapter_summary["raw_datasets"])
    print_label("Lookup Datasets", adapter_summary["lookup_datasets"])

    print()
    print("Processing Summary")
    print("------------------")
    print_label("Records Parsed", adapter_summary["parsed_raw_records"])
    print_label("Lookup Records Parsed", adapter_summary["parsed_lookup_records"])
    print_label("Records Validated", adapter_summary["validated_records"])
    print_label("Operational Entities Created", adapter_summary["operational_entities"])

    print()
    print("Representative Operational Entity")
    print("----------------------------------")
    entity = representative_flow["entity"]
    print_label("Entity ID", entity.get("entity_id"), 18)
    print_label("Platform", entity.get("source_system"), 18)
    print_label("Pipeline", entity.get("entity_name"), 18)
    print_label("Status", entity.get("execution_status"), 18)
    print_label("Timestamp", entity.get("event_timestamp"), 18)

    print()
    print("Passing Operational Entity to Observer Agent...")

    print()
    print("Completion Status")
    print("------------------")
    print_label("Capability Adapter", "Completed Successfully")


def print_observer_summary(observer_summary, representative_flow):

    print_section_header(2, "OBSERVER AGENT")
    print("Observer Agent Received Operational Entity")
    print("------------------------------------------")
    print_label("Entity ID", representative_flow["entity"].get("entity_id"), 18)
    print_label("Platform", representative_flow["entity"].get("source_system"), 18)

    print()
    print("Observing Metrics...")
    print()
    print_label("Throughput", f"{representative_flow['observation_metrics'].get('throughput')} msg/sec", 18)
    print_label("Consumer Lag", representative_flow['observation_metrics'].get('consumer_lag'), 18)

    print()
    print("Comparing with Historical Baseline...")
    print()
    print_label("Expected Throughput", representative_flow['observation_baseline'].get('throughput', {}).get('baseline'), 24)
    throughput_deviation = representative_flow['observation_baseline'].get('throughput', {}).get('deviation_percent')
    print_label("Deviation", f"+{throughput_deviation}%" if throughput_deviation is not None else "None", 24)

    print()
    print("Detecting Trend...")
    print()
    print_label("Trend", representative_flow['observation_trend'].get('throughput', 'Stable'), 18)

    print()
    print("Detecting Events...")
    print()
    observation_events = representative_flow["observation_events"]
    if observation_events:
        for event in observation_events:
            print(f"✓ {event}")
    else:
        print("✓ None")

    print()
    print("Observation Created")
    print("-------------------")
    print_label(
        "State",
        derive_observation_status(
            representative_flow["observation_events"],
            representative_flow["observation_baseline"]
        ),
        18
    )
    print("Reason")
    print_reasons(
        summarize_observer_reason(
            representative_flow["observation_events"],
            representative_flow["observation_baseline"],
            representative_flow["observation_trend"]
        )
    )

    print()
    print("Passing Observation Object to Behavior Agent...")

    print()
    print("Completion Status")
    print("------------------")
    print_label("Observation Object", "Generated", 18)


def print_behavior_summary(behavior_summary, representative_flow):

    print_section_header(3, "BEHAVIOR AGENT")
    print("Behavior Agent Received Observation Object")
    print("------------------------------------------")
    print_label("Entity ID", representative_flow["entity"].get("entity_id"), 18)

    print()
    print("Analyzing Behavior...")
    print()
    print_label("Behavior Score", f"{representative_flow['behavior_analysis'].get('behavior_score')} /100", 18)
    print_label("Severity", representative_flow['behavior_analysis'].get('severity'), 18)
    confidence_percent = round((representative_flow['behavior_analysis'].get('confidence') or 0) * 100)
    print_label("Confidence", f"{confidence_percent}%", 18)

    print_label(
        "Deviation Score",
        format_deviation_score(representative_flow),
        18
    )

    print_label(
        "Drift Status",
        format_drift_status(representative_flow),
        18
    )

    print()
    print("Detecting Behavior Pattern...")
    print()
    patterns = representative_flow['behavior_analysis'].get('patterns', [])
    if patterns:
        for pattern in patterns:
            print(f"✓ {pattern}")
    else:
        print("✓ No abnormal pattern detected")

    print()
    print("Final Behavior Status")
    print("---------------------")
    print_label(
        "Behavior Status",
        derive_behavior_status(
            representative_flow["behavior_analysis"],
            representative_flow["observation_events"],
            representative_flow["observation_baseline"],
            representative_flow["observation_trend"]
        ),
        18
    )

    print()
    print("Behavior Object Generated Successfully.")

    print("Completion Status")
    print("------------------")
    print_label("Behavior Object", "Generated Successfully", 18)


def derive_observation_status(events, baseline):

    if events or any(
        result.get("status") in {"WARNING", "CRITICAL"}
        for result in baseline.values()
    ):

        return "ATTENTION REQUIRED"

    return "NORMAL"


def summarize_baseline_comparison(baseline):

    if not baseline:

        return "No baseline comparison available"

    parts = []

    for metric_name, result in baseline.items():

        status = result.get("status", "UNKNOWN")
        deviation = result.get("deviation_percent")

        if deviation is None:

            parts.append(f"{metric_name.title()}={status}")

        else:

            parts.append(f"{metric_name.title()}={status} ({deviation}%)")

    return "; ".join(parts)


def derive_behavior_status(behavior_analysis, events, baseline, trend):

    if behavior_analysis.get("severity") in {"WARNING", "CRITICAL"}:

        return "ATTENTION REQUIRED"

    if behavior_analysis.get("patterns"):

        return "ATTENTION REQUIRED"

    if events or any(result.get("status") in {"WARNING", "CRITICAL"} for result in baseline.values()):

        return "ATTENTION REQUIRED"

    if any(value == "Increasing" for value in trend.values()):

        return "ATTENTION REQUIRED"

    return "NORMAL"


def summarize_observer_reason(events, baseline, trend):

    reasons = []

    for metric_name, result in baseline.items():

        deviation = result.get("deviation_percent")
        status = result.get("status")

        if status in {"WARNING", "CRITICAL"} and deviation is not None:

            reasons.append(f"{metric_name.title()} is {deviation}% above baseline")

    for metric_name, trend_value in trend.items():

        if trend_value == "Increasing":

            reasons.append(f"{metric_name.title()} is increasing")

    for event in events:

        reasons.append(f"{event} detected")

    if not reasons:

        reasons.append("No abnormal baseline deviation or events detected")

    return reasons


def summarize_behavior_reason(behavior_analysis, events, baseline, trend):

    reasons = []

    for metric_name, result in baseline.items():

        deviation = result.get("deviation_percent")
        status = result.get("status")

        if status in {"WARNING", "CRITICAL"} and deviation is not None:

            reasons.append(
                f"{metric_name.title()} exceeds historical baseline by {deviation}%"
            )

    for metric_name, trend_value in trend.items():

        if trend_value == "Increasing":

            reasons.append(f"{metric_name.title()} trend is increasing")

    for event in events:

        reasons.append(f"{event} detected")

    for pattern in behavior_analysis.get("patterns", []):

        reasons.append(pattern)

    if not reasons:

        reasons.append("Behavior remains within expected thresholds")

    return reasons


def format_deviation_score(representative_flow):

    baseline = representative_flow.get("observation_baseline", {})

    if not baseline:

        return "None"

    deviations = []

    for result in baseline.values():

        deviation = result.get("deviation_percent")

        if deviation is not None:

            deviations.append(abs(deviation))

    if not deviations:

        return "None"

    return f"{max(deviations)}%"


def format_drift_status(representative_flow):

    drift = representative_flow.get("behavior_analysis", {}).get("drift", {})

    if not drift:

        return "None"

    if any(result.get("is_drifting") for result in drift.values()):

        return "DETECTED"

    return "CLEAR"


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()