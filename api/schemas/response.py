from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class PipelineDetailsResponse(BaseModel):
    operational_entity: Optional[Dict[str, Any]] = None
    observation_object: Optional[Dict[str, Any]] = None
    behavior_object: Optional[Dict[str, Any]] = None
    risk_object: Optional[Dict[str, Any]] = None
    integrity_object: Optional[Dict[str, Any]] = None
    recommendation_object: Optional[Dict[str, Any]] = None

class TimelineEvent(BaseModel):
    timestamp: str
    status: str
    metrics: Dict[str, Any]

class TimelineResponse(BaseModel):
    pipeline_id: str
    timeline: List[TimelineEvent]

class LineageRelation(BaseModel):
    entity_id: str
    source_system: str
    depends_on: str
    downstream: str
    dependency_type: str

class DependencyResponse(BaseModel):
    pipeline_id: str
    upstream_pipelines: List[str]
    downstream_pipelines: List[str]
    pipeline_lineage: List[LineageRelation]
    dependency_count: int

class RecommendationResponse(BaseModel):
    pipeline_id: str
    priority: Optional[str] = None
    recommendation: Optional[str] = None
    expected_impact: Optional[str] = None
    recovery_time: Optional[str] = None
    automation_possible: Optional[bool] = None
    human_approval_required: Optional[bool] = None
    confidence: Optional[float] = None
    generated_by: Optional[str] = None
    model: Optional[str] = None
    recommendation_source: Optional[str] = None

class CopilotChatResponse(BaseModel):
    answer: str

class AgentHealthDetail(BaseModel):
    status: str
    version: str
    health: str

class AgentsResponse(BaseModel):
    agents: Dict[str, AgentHealthDetail]

class DashboardSummaryResponse(BaseModel):
    execution_summary: Dict[str, Any]
    capability_adapter_summary: Dict[str, Any]
    observer_summary: Dict[str, Any]
    behavior_summary: Dict[str, Any]
    risk_summary: Dict[str, Any]
    integrity_summary: Dict[str, Any]
    recommendation_summary: Dict[str, Any]
    top_critical_pipelines: List[Dict[str, Any]]
    agent_health: Dict[str, AgentHealthDetail]
    representative_pipeline: PipelineDetailsResponse
    latest_recommendation: Optional[Dict[str, Any]] = None
    execution_time: float
    status: str
