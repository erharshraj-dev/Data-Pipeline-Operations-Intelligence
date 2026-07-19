from fastapi import APIRouter
from api.services.pipeline_service import PipelineService

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"]
)


@router.post("/execute")
def execute_pipeline():
    """
    Execute the complete AIF pipeline.
    """
    return PipelineService.execute()