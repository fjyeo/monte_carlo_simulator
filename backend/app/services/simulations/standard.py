from __future__ import annotations

import numpy as np

from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulations.common import summarize_unweighted


def _draw_samples(request: SimulationRequest, rng: np.random.Generator) -> np.ndarray:
    if request.distribution == "normal":
        return rng.normal(size=(request.samples, request.dimensions))
    if request.distribution == "uniform":
        return rng.uniform(-1.0, 1.0, size=(request.samples, request.dimensions))
    centers = np.array([[-1.0, -1.0], [1.0, 1.0]], dtype=float)
    if request.dimensions > 2:
        centers = np.pad(centers, ((0, 0), (0, request.dimensions - 2)), mode="constant")
    choices = rng.integers(0, 2, size=request.samples)
    locs = centers[choices]
    return rng.normal(loc=locs, scale=0.6, size=(request.samples, request.dimensions))


def _integrand(samples: np.ndarray) -> np.ndarray:
    squared_norm = np.sum(samples * samples, axis=1)
    return np.exp(-0.5 * squared_norm)


def run_standard_mc(request: SimulationRequest) -> SimulationResponse:
    rng = np.random.default_rng(request.seed)
    samples = _draw_samples(request, rng)
    values = _integrand(samples)
    summary = summarize_unweighted(values)

    return SimulationResponse(
        method="standard",
        estimate=summary.final_mean,
        variance=summary.final_variance,
        ci_low=summary.final_ci_low,
        ci_high=summary.final_ci_high,
        samples_used=request.samples,
        sample_sizes=summary.sample_sizes,
        estimate_series=summary.mean_series,
        variance_series=summary.variance_series,
        ci_low_series=summary.ci_low_series,
        ci_high_series=summary.ci_high_series,
    )
