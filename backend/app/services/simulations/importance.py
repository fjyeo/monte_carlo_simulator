from __future__ import annotations

import numpy as np

from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulations.common import summarize_weighted


def _log_normal_pdf(x: np.ndarray, variance: float) -> np.ndarray:
    dims = x.shape[1]
    return -0.5 * (np.sum(x * x, axis=1) / variance + dims * np.log(2.0 * np.pi * variance))


def _integrand(samples: np.ndarray) -> np.ndarray:
    squared_norm = np.sum(samples * samples, axis=1)
    return np.exp(-0.5 * squared_norm)


def run_importance_sampling(request: SimulationRequest) -> SimulationResponse:
    if request.distribution != "normal":
        request = request.model_copy(update={"distribution": "normal"})

    rng = np.random.default_rng(request.seed)
    proposal_variance = 4.0
    samples = rng.normal(scale=np.sqrt(proposal_variance), size=(request.samples, request.dimensions))

    log_target = _log_normal_pdf(samples, variance=1.0)
    log_proposal = _log_normal_pdf(samples, variance=proposal_variance)
    weights = np.exp(log_target - log_proposal)

    values = _integrand(samples)
    summary = summarize_weighted(values, weights)

    return SimulationResponse(
        method="importance",
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
