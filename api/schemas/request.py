from pydantic import BaseModel

class CopilotQuery(BaseModel):
    query: str
