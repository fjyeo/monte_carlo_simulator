from collections.abc import Callable

from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.simulations.standard import run_standard_mc
from app.services.simulations.importance import run_importance_sampling
from app.services.simulations.metropolis import run_metropolis_hastings


Handler = Callable[[SimulationRequest], SimulationResponse]


HANDLERS: dict[str, Handler] = {
    "standard": run_standard_mc,
    "importance": run_importance_sampling,
    "metropolis-hastings": run_metropolis_hastings,
}


def get_simulation_handler(method: str) -> Handler:
    return HANDLERS.get(method, run_standard_mc)
