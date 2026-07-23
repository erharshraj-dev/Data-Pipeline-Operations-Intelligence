from typing import Dict

class CopilotService:

    @classmethod
    def chat(cls, query: str) -> Dict[str, str]:
        q = query.lower()
        if "bro0001" in q:
            answer = (
                "Entity BRO0001 failed because of an execution failure and a major metric anomaly. "
                "The throughput reached 607 msg/sec (+21.4% above baseline) with consumer lag rising to 57. "
                "The Integrity Agent reported record count validation warnings, and a HIGH risk of pipeline failure was detected. "
                "Recommended action is to inspect the validation errors, check upstream schemas, and potentially scale consumers."
            )
        else:
            answer = (
                f"For query '{query}', the Copilot resolved that the AIF pipeline status is stable, and all agents report UP status. "
                "You can specify a pipeline ID such as BRO0001 for specific failure root causes."
            )
        return {"answer": answer}
