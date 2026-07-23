from typing import Dict, Any

class AgentService:

    @classmethod
    def get_agents(cls) -> Dict[str, Any]:
        return {
            "agents": {
                "Capability Adapter": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Observer": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Behavior": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Risk Prediction": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Integrity": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Recommendation": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                },
                "Multi LLM": {
                    "status": "UP",
                    "version": "1.0.0",
                    "health": "OK"
                }
            }
        }
