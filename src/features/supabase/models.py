from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    # Required field (indicated by ...), with an example list
    status: str = Field(..., examples=["healthy"])
    
    # Required field, with a default examples list
    database_connected: bool = Field(..., examples=[True])
    
    # Optional field with an explicit default of None
    latency_ms: float | None = Field(default=None, examples=[42.5])