from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulations.registry import get_simulation_handler


def run_simulation(request: SimulationRequest) -> SimulationResponse:
    handler = get_simulation_handler(request.method)
    return handler(request)
