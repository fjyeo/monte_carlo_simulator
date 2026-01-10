import type { SimulationRequest, SimulationResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function runSimulation(payload: SimulationRequest): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Simulation request failed");
  }

  return response.json() as Promise<SimulationResponse>;
}
