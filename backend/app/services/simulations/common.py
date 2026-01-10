from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable

import numpy as np


@dataclass
class SeriesSummary:
    sample_sizes: list[int]
    mean_series: list[float]
    variance_series: list[float]
    ci_low_series: list[float]
    ci_high_series: list[float]
    final_mean: float
    final_variance: float
    final_ci_low: float
    final_ci_high: float


def _select_indices(total: int, max_points: int) -> list[int]:
    if total <= max_points:
        return list(range(1, total + 1))
    stride = ceil(total / max_points)
    indices = list(range(stride, total + 1, stride))
    if indices[-1] != total:
        indices.append(total)
    return indices


def summarize_unweighted(values: Iterable[float], max_points: int = 200) -> SeriesSummary:
    values_array = np.asarray(list(values), dtype=float)
    total = values_array.size
    indices = _select_indices(total, max_points)

    cumsum = np.cumsum(values_array)
    cumsum_sq = np.cumsum(values_array * values_array)

    mean_all = cumsum / np.arange(1, total + 1)
    variance_all = np.zeros_like(mean_all)
    if total > 1:
        numerator = cumsum_sq - (cumsum * cumsum) / np.arange(1, total + 1)
        variance_all[1:] = numerator[1:] / (np.arange(2, total + 1) - 1)

    stderr = np.sqrt(variance_all / np.arange(1, total + 1))
    ci_low = mean_all - 1.96 * stderr
    ci_high = mean_all + 1.96 * stderr

    idx = np.array(indices) - 1

    return SeriesSummary(
        sample_sizes=[int(n) for n in indices],
        mean_series=[float(x) for x in mean_all[idx]],
        variance_series=[float(x) for x in variance_all[idx]],
        ci_low_series=[float(x) for x in ci_low[idx]],
        ci_high_series=[float(x) for x in ci_high[idx]],
        final_mean=float(mean_all[-1]),
        final_variance=float(variance_all[-1]),
        final_ci_low=float(ci_low[-1]),
        final_ci_high=float(ci_high[-1]),
    )


def summarize_weighted(values: np.ndarray, weights: np.ndarray, max_points: int = 200) -> SeriesSummary:
    values = values.astype(float)
    weights = weights.astype(float)
    total = values.size
    indices = _select_indices(total, max_points)

    w = weights
    wf = weights * values
    wf2 = weights * values * values
    w2 = weights * weights

    cum_w = np.cumsum(w)
    cum_wf = np.cumsum(wf)
    cum_wf2 = np.cumsum(wf2)
    cum_w2 = np.cumsum(w2)

    mean_all = cum_wf / cum_w
    variance_all = np.maximum(cum_wf2 / cum_w - mean_all * mean_all, 0.0)
    n_eff = np.maximum(cum_w * cum_w / cum_w2, 1.0)
    stderr = np.sqrt(variance_all / n_eff)
    ci_low = mean_all - 1.96 * stderr
    ci_high = mean_all + 1.96 * stderr

    idx = np.array(indices) - 1

    return SeriesSummary(
        sample_sizes=[int(n) for n in indices],
        mean_series=[float(x) for x in mean_all[idx]],
        variance_series=[float(x) for x in variance_all[idx]],
        ci_low_series=[float(x) for x in ci_low[idx]],
        ci_high_series=[float(x) for x in ci_high[idx]],
        final_mean=float(mean_all[-1]),
        final_variance=float(variance_all[-1]),
        final_ci_low=float(ci_low[-1]),
        final_ci_high=float(ci_high[-1]),
    )


def autocorrelation_series(values: np.ndarray, max_lag: int = 40) -> list[float]:
    series = values - np.mean(values)
    denom = np.dot(series, series)
    if denom == 0:
        return [1.0] + [0.0 for _ in range(max_lag)]
    acf = [1.0]
    for lag in range(1, max_lag + 1):
        numer = np.dot(series[:-lag], series[lag:])
        acf.append(float(numer / denom))
    return acf
