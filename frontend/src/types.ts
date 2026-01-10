export type SimulationMethod = "standard" | "importance" | "metropolis-hastings";
export type DistributionType = "normal" | "uniform" | "custom";

export interface SimulationRequest {
  method: SimulationMethod;
  distribution: DistributionType;
  dimensions: number;
  samples: number;
  seed: number | null;
}

export interface SimulationResponse {
  method: SimulationMethod;
  estimate: number;
  variance: number;
  ci_low: number;
  ci_high: number;
  samples_used: number;
  sample_sizes: number[];
  estimate_series: number[];
  variance_series: number[];
  ci_low_series: number[];
  ci_high_series: number[];
  trace: number[];
  autocorrelation: number[];
}
