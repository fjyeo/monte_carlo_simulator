import { useState } from 'react'
import './App.css'

type MonteCarloResponse = {
  estimate: number
  std_error: number
  samples_used: number
}

function App() {
  const [samples, setSamples] = useState(1000)
  const [dimensions, setDimensions] = useState(2)
  const [seed, setSeed] = useState<number | ''>('')
  const [result, setResult] = useState<MonteCarloResponse | null>(null)
  const [history, setHistory] = useState<number[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const runSimulation = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/simulate/monte-carlo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          samples,
          dimensions,
          seed: seed === '' ? null : seed,
        }),
      })

      if (!response.ok) {
        throw new Error('Simulation failed')
      }

      const data = (await response.json()) as MonteCarloResponse
      setResult(data)
      setHistory((prev) => [...prev, data.estimate])
    } catch (caught) {
      const message =
        caught instanceof Error ? caught.message : 'Unexpected error'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Monte Carlo Playground</h1>
        <p>Estimate E[sum(x²)] for x ~ Uniform([0,1]^d)</p>
      </header>

      <section className="panel">
        <label>
          Samples
          <input
            type="number"
            min={1}
            max={1_000_000}
            value={samples}
            onChange={(event) => setSamples(Number(event.target.value))}
          />
        </label>
        <label>
          Dimensions
          <input
            type="number"
            min={1}
            max={20}
            value={dimensions}
            onChange={(event) => setDimensions(Number(event.target.value))}
          />
        </label>
        <label>
          Seed (optional)
          <input
            type="number"
            value={seed}
            onChange={(event) =>
              setSeed(event.target.value === '' ? '' : Number(event.target.value))
            }
          />
        </label>

        <button type="button" onClick={runSimulation} disabled={isLoading}>
          {isLoading ? 'Running...' : 'Run simulation'}
        </button>
      </section>

      <section className="panel">
        <h2>Result</h2>
        {error && <p className="error">{error}</p>}
        {result ? (
          <dl>
            <div>
              <dt>Estimate</dt>
              <dd>{result.estimate.toFixed(6)}</dd>
            </div>
            <div>
              <dt>Std. error</dt>
              <dd>{result.std_error.toFixed(6)}</dd>
            </div>
            <div>
              <dt>Samples used</dt>
              <dd>{result.samples_used}</dd>
            </div>
          </dl>
        ) : (
          <p className="muted">Run the simulation to see results.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Estimate history</h2>
          <button
            type="button"
            onClick={() => setHistory([])}
            disabled={history.length === 0}
          >
            Clear
          </button>
        </div>
        {history.length < 2 ? (
          <p className="muted">Run the simulation at least twice to plot.</p>
        ) : (
          <EstimatePlot values={history} />
        )}
      </section>
    </div>
  )
}

type EstimatePlotProps = {
  values: number[]
}

function EstimatePlot({ values }: EstimatePlotProps) {
  const width = 420
  const height = 160
  const padding = 16
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const range = maxValue - minValue || 1

  const points = values
    .map((value, index) => {
      const x =
        padding + (index / (values.length - 1)) * (width - padding * 2)
      const y =
        padding + ((maxValue - value) / range) * (height - padding * 2)
      return `${x},${y}`
    })
    .join(' ')

  return (
    <div className="plot">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Estimate history plot"
      >
        <rect x="0" y="0" width={width} height={height} rx="12" />
        <polyline points={points} />
      </svg>
      <div className="plot-meta">
        <span>Min: {minValue.toFixed(4)}</span>
        <span>Max: {maxValue.toFixed(4)}</span>
        <span>Runs: {values.length}</span>
      </div>
    </div>
  )
}

export default App
