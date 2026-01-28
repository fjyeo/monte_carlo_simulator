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
