# Backend (FastAPI)

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```powershell
uvicorn app.main:app --reload --port 8000
```

## Check
```powershell
Invoke-RestMethod http://localhost:8000/health
```

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
