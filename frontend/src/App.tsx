import { useMemo, useState } from "react";
import "./styles/app.css";
import { runSimulation } from "./api/client";
import type { SimulationRequest, SimulationResponse } from "./types";
import LineChart from "./components/LineChart";
import BandChart from "./components/BandChart";

const DEFAULT_REQUEST: SimulationRequest = {
  method: "standard",
  distribution: "normal",
  dimensions: 2,
  samples: 5000,
  seed: null,
};

function buildSeries(result: SimulationResponse | null) {
  if (!result) {
    return { convergence: [], variance: [], trace: [], autocorrelation: [] };
  }

  const convergence = result.sample_sizes.map((size, index) => ({
    x: size,
    y: result.estimate_series[index],
    low: result.ci_low_series[index],
    high: result.ci_high_series[index],
  }));

  const variance = result.sample_sizes.map((size, index) => ({
    x: size,
    y: result.variance_series[index],
  }));

  const trace = result.trace.map((value, index) => ({
    x: index + 1,
    y: value,
  }));

  const autocorrelation = result.autocorrelation.map((value, index) => ({
    x: index,
    y: value,
  }));

  return { convergence, variance, trace, autocorrelation };
}

export default function App() {
  const [request, setRequest] = useState<SimulationRequest>(DEFAULT_REQUEST);
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "error">("idle");

  const series = useMemo(() => buildSeries(result), [result]);
  const summary = useMemo(() => {
    if (!result) return "Run a simulation to see estimates.";
    return `Estimate: ${result.estimate.toFixed(4)} | Variance: ${result.variance.toFixed(4)}`;
  }, [result]);

  async function handleRun() {
    try {
      setStatus("running");
      const response = await runSimulation(request);
      setResult(response);
      setStatus("idle");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Monte Carlo Visualization Lab</p>
          <h1>Explore convergence, variance, and sampling behavior.</h1>
          <p className="subtitle">
            Compare Monte Carlo estimators with interactive controls and live plots.
          </p>
          <div className="hero-actions">
            <button className="primary" onClick={handleRun} disabled={status === "running"}>
              {status === "running" ? "Simulating..." : "Run simulation"}
            </button>
            <span className="status">{status === "error" ? "Simulation failed." : summary}</span>
          </div>
        </div>
        <div className="hero-panel">
          <div className="stat">
            <span>Method</span>
            <strong>{request.method}</strong>
          </div>
          <div className="stat">
            <span>Dimensions</span>
            <strong>{request.dimensions}</strong>
          </div>
          <div className="stat">
            <span>Samples</span>
            <strong>{request.samples.toLocaleString()}</strong>
          </div>
        </div>
      </header>

      <main className="grid">
        <section className="panel controls">
          <h2>Controls</h2>
          <div className="field">
            <label htmlFor="method">Method</label>
            <select
              id="method"
              value={request.method}
              onChange={(event) => setRequest({ ...request, method: event.target.value as SimulationRequest["method"] })}
            >
              <option value="standard">Standard MC</option>
              <option value="importance">Importance Sampling</option>
              <option value="metropolis-hastings">Metropolis-Hastings</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="distribution">Distribution</label>
            <select
              id="distribution"
              value={request.distribution}
              onChange={(event) => setRequest({ ...request, distribution: event.target.value as SimulationRequest["distribution"] })}
            >
              <option value="normal">Normal</option>
              <option value="uniform">Uniform</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="dimensions">Dimensions</label>
            <input
              id="dimensions"
              type="number"
              min={1}
              max={20}
              value={request.dimensions}
              onChange={(event) => setRequest({ ...request, dimensions: Number(event.target.value) })}
            />
          </div>
          <div className="field">
            <label htmlFor="samples">Samples</label>
            <input
              id="samples"
              type="number"
              min={100}
              max={200000}
              value={request.samples}
              onChange={(event) => setRequest({ ...request, samples: Number(event.target.value) })}
            />
          </div>
          <div className="field">
            <label htmlFor="seed">Seed (optional)</label>
            <input
              id="seed"
              type="number"
              placeholder="auto"
              value={request.seed ?? ""}
              onChange={(event) =>
                setRequest({
                  ...request,
                  seed: event.target.value === "" ? null : Number(event.target.value),
                })
              }
            />
          </div>
          <button className="secondary" onClick={() => setRequest(DEFAULT_REQUEST)}>
            Reset
          </button>
        </section>

        <section className="panel plot">
          <h2>Convergence</h2>
          <div className="plot-surface chart-surface">
            <BandChart data={series.convergence} />
          </div>
        </section>

        <section className="panel plot">
          <h2>Variance</h2>
          <div className="plot-surface chart-surface">
            <LineChart data={series.variance} color="#b07131" />
          </div>
        </section>

        <section className="panel plot">
          <h2>Trace</h2>
          <div className="plot-surface chart-surface">
            <LineChart data={series.trace} color="#3b3f45" />
          </div>
        </section>

        <section className="panel plot">
          <h2>Autocorrelation</h2>
          <div className="plot-surface chart-surface">
            <LineChart data={series.autocorrelation} color="#8a5d2a" />
          </div>
        </section>
      </main>
    </div>
  );
}
