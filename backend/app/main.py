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


class ConvergenceRequest(BaseModel):
    max_samples: int = Field(default=1000, ge=1, le=1_000_000)
    step: int = Field(default=100, ge=1, le=100_000)
    dimensions: int = Field(default=2, ge=1, le=20)
    seed: int | None = None


class ConvergencePoint(BaseModel):
    samples_used: int
    estimate: float


class ConvergenceResponse(BaseModel):
    points: list[ConvergencePoint]


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


@app.post("/simulate/monte-carlo/convergence", response_model=ConvergenceResponse)
def simulate_monte_carlo_convergence(
    payload: ConvergenceRequest,
) -> ConvergenceResponse:
    rng = random.Random(payload.seed)
    total = 0.0
    count = 0
    points: list[ConvergencePoint] = []

    max_samples = payload.max_samples
    step = min(payload.step, max_samples)
    d = payload.dimensions

    for target in range(step, max_samples + 1, step):
        while count < target:
            value = 0.0
            for _ in range(d):
                x = rng.random()
                value += x * x
            total += value
            count += 1
        points.append(ConvergencePoint(samples_used=count, estimate=total / count))

    if points and points[-1].samples_used != max_samples:
        while count < max_samples:
            value = 0.0
            for _ in range(d):
                x = rng.random()
                value += x * x
            total += value
            count += 1
        points.append(ConvergencePoint(samples_used=count, estimate=total / count))

    return ConvergenceResponse(points=points)
