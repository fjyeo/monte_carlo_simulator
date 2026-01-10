from __future__ import annotations

import numpy as np

from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulations.common import autocorrelation_series, summarize_unweighted


def _log_target(samples: np.ndarray, distribution: str) -> np.ndarray:
    if distribution == "uniform":
        in_bounds = np.all((samples >= -1.0) & (samples <= 1.0), axis=1)
        logp = np.full(samples.shape[0], -np.inf)
        logp[in_bounds] = 0.0
        return logp
    squared_norm = np.sum(samples * samples, axis=1)
    dims = samples.shape[1]
    return -0.5 * (squared_norm + dims * np.log(2.0 * np.pi))


def _integrand(samples: np.ndarray) -> np.ndarray:
    squared_norm = np.sum(samples * samples, axis=1)
    return np.exp(-0.5 * squared_norm)


def run_metropolis_hastings(request: SimulationRequest) -> SimulationResponse:
    rng = np.random.default_rng(request.seed)
    step_size = 0.8
    current = rng.normal(size=(1, request.dimensions))
    current_logp = _log_target(current, request.distribution)[0]

    chain = np.zeros((request.samples, request.dimensions))
    accepts = 0

    for i in range(request.samples):
        proposal = current + rng.normal(scale=step_size, size=current.shape)
        proposal_logp = _log_target(proposal, request.distribution)[0]
        log_alpha = proposal_logp - current_logp
        if np.log(rng.random()) < log_alpha:
            current = proposal
            current_logp = proposal_logp
            accepts += 1
        chain[i] = current

    values = _integrand(chain)
    summary = summarize_unweighted(values)
    trace = chain[:, 0]

    return SimulationResponse(
        method="metropolis-hastings",
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
        trace=[float(x) for x in trace[-1000:]],
        autocorrelation=autocorrelation_series(trace[-1000:]),
    )
