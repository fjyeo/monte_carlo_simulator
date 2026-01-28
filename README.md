# Monte Carlo Visualization

Interactive web app for exploring Monte Carlo simulation methods with a React
frontend and a FastAPI backend.

## Project goals
- Show how Monte Carlo estimates converge as sample size increases.
- Compare standard Monte Carlo, importance sampling, and MCMC (later phases).
- Visualize diagnostics: convergence, variance, trace plots, autocorrelation.

## Tech stack
- Frontend: React + TypeScript (Vite)
- Backend: FastAPI (Python)

## Quick start

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
npm install
npm run dev
```

Open `http://localhost:5173`.

## API

### POST /simulate/monte-carlo
Estimate the expected value of the sum of squares for a uniform random vector
in `d` dimensions.

Request body:
```json
{
  "samples": 1000,
  "dimensions": 2,
  "seed": 123
}
```

Response:
```json
{
  "estimate": 0.666666,
  "std_error": 0.012345,
  "samples_used": 1000
}
```

## Current status
- Backend scaffold is in place.
- Basic Monte Carlo endpoint implemented.
- Minimal frontend call available (see the UI for inputs/results).
