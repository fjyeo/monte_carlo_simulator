from fastapi import APIRouter

from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulation_runner import run_simulation

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest) -> SimulationResponse:
    return run_simulation(request)
