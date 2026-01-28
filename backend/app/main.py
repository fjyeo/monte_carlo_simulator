import math
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Monte Carlo Visualization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


class MonteCarloRequest(BaseModel):
    samples: int = Field(default=1000, ge=1, le=1_000_000)
    dimensions: int = Field(default=2, ge=1, le=20)
    seed: int | None = None


class MonteCarloResponse(BaseModel):
    estimate: float
    std_error: float
    samples_used: int


@app.post("/simulate/monte-carlo", response_model=MonteCarloResponse)
def simulate_monte_carlo(payload: MonteCarloRequest) -> MonteCarloResponse:
    rng = random.Random(payload.seed)
    n = payload.samples
    d = payload.dimensions

    # Estimate E[sum(x_i^2)] for x ~ Uniform([0,1]^d)
    total = 0.0
    total_sq = 0.0
    for _ in range(n):
        value = 0.0
        for _ in range(d):
            x = rng.random()
            value += x * x
        total += value
        total_sq += value * value

    mean = total / n
    if n > 1:
        variance = (total_sq - n * mean * mean) / (n - 1)
        std_error = math.sqrt(variance / n)
    else:
        std_error = 0.0

    return MonteCarloResponse(
        estimate=mean,
        std_error=std_error,
        samples_used=n,
    )
