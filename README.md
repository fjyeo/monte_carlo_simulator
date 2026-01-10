# Monte Carlo Visualization Lab

Interactive web app for exploring Monte Carlo methods with a focus on simulation, visualization, and clear explanations.

## Goals
- Visualize convergence, variance, and confidence intervals for Monte Carlo estimators.
- Compare standard Monte Carlo, importance sampling, and Metropolis-Hastings.
- Provide an interactive UI for changing parameters and seeing results live.

## Stack
- Frontend: React + Vite + TypeScript
- Backend: FastAPI (Python)

## Repo layout
- `backend/` FastAPI app and simulation services
- `frontend/` React app and visualization UI
- `venv/` Local virtualenv (ignored)

## Quickstart
Backend (Windows PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Environment
- Frontend reads `VITE_API_BASE_URL` (default `http://localhost:8000`).
- Backend allows CORS from `http://localhost:5173` by default.

## What the simulation is doing
Each run estimates the expectation of a simple integrand:

- Integrand: `f(x) = exp(-0.5 * ||x||^2)`.
- Standard MC draws samples from the chosen distribution and averages `f(x)`.
- Importance sampling draws from a wider normal proposal and reweights samples.
- Metropolis-Hastings uses a random-walk proposal to sample from the target distribution.

These are intentionally small but real implementations so the UI has working data for convergence and trace plots.

## API shape
`POST /api/simulate` returns:

- `estimate`, `variance`, `ci_low`, `ci_high`: final summary values.
- `sample_sizes`, `estimate_series`, `variance_series`, `ci_low_series`, `ci_high_series`: data for plots.
- `trace`, `autocorrelation`: chain diagnostics (mostly for Metropolis-Hastings).

## Next implementation steps
- Implement richer distributions and integrands in `backend/app/services/simulations/`.
- Replace the placeholder integrand with a configurable function from the UI.
- Add richer charts (histograms, pair plots) when you pick a charting library.
