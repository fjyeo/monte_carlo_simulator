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


class ImportanceSamplingRequest(BaseModel):
    samples: int = Field(default=1000, ge=1, le=1_000_000)
    dimensions: int = Field(default=2, ge=1, le=20)
    alpha: float = Field(default=2.0, gt=0.0, le=10.0)
    beta: float = Field(default=2.0, gt=0.0, le=10.0)
    seed: int | None = None


class ImportanceSamplingResponse(BaseModel):
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


def _beta_sample(rng: random.Random, alpha: float, beta: float) -> float:
    x = rng.gammavariate(alpha, 1.0)
    y = rng.gammavariate(beta, 1.0)
    total = x + y
    if total == 0.0:
        return 0.5
    return x / total


def _beta_log_pdf(x: float, alpha: float, beta: float) -> float:
    epsilon = 1e-12
    x = min(max(x, epsilon), 1.0 - epsilon)
    log_norm = math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
    return (alpha - 1.0) * math.log(x) + (beta - 1.0) * math.log(1.0 - x) - log_norm


@app.post("/simulate/importance-sampling", response_model=ImportanceSamplingResponse)
def simulate_importance_sampling(
    payload: ImportanceSamplingRequest,
) -> ImportanceSamplingResponse:
    rng = random.Random(payload.seed)
    n = payload.samples
    d = payload.dimensions
    alpha = payload.alpha
    beta = payload.beta

    sum_w = 0.0
    sum_wf = 0.0
    sum_wf2 = 0.0

    for _ in range(n):
        value = 0.0
        log_q = 0.0
        for _ in range(d):
            x = _beta_sample(rng, alpha, beta)
            value += x * x
            log_q += _beta_log_pdf(x, alpha, beta)
        weight = math.exp(-log_q)
        sum_w += weight
        sum_wf += weight * value
        sum_wf2 += weight * value * value

    estimate = sum_wf / sum_w
    variance = max(0.0, (sum_wf2 / sum_w) - estimate * estimate)
    std_error = math.sqrt(variance / n) if n > 1 else 0.0

    return ImportanceSamplingResponse(
        estimate=estimate,
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
