from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    method: str = Field("standard", description="standard | importance | metropolis-hastings")
    distribution: str = Field("normal", description="normal | uniform | custom")
    dimensions: int = Field(2, ge=1, le=20)
    samples: int = Field(1000, ge=100, le=200000)
    seed: int | None = None


class SimulationResponse(BaseModel):
    method: str
    estimate: float
    variance: float
    ci_low: float
    ci_high: float
    samples_used: int
    sample_sizes: list[int]
    estimate_series: list[float]
    variance_series: list[float]
    ci_low_series: list[float]
    ci_high_series: list[float]
    trace: list[float] = []
    autocorrelation: list[float] = []
