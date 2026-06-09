import math
import random
import time
from copy import deepcopy
from pathlib import Path

import csv
import matplotlib.pyplot as plt

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver


INSTANCE = "singlecenter-72-n50.txt"


def simulated_annealing(
    solver,
    initial_solution,
    max_iterations=500,
    initial_temp=1000,
    cooling_rate=0.995,
):
    current = deepcopy(initial_solution)
    best = deepcopy(initial_solution)

    current_cost = current.total_cost
    best_cost = best.total_cost

    temperature = initial_temp

    history = []

    for iteration in range(max_iterations):
        candidate = solver._relocation_operator(deepcopy(current))

        candidate_cost = candidate.total_cost

        delta = candidate_cost - current_cost

        accept = False

        if delta < 0:
            accept = True
        else:
            probability = math.exp(-delta / temperature)
            if random.random() < probability:
                accept = True

        if accept:
            current = deepcopy(candidate)
            current_cost = candidate_cost

        if current_cost < best_cost:
            best = deepcopy(current)
            best_cost = current_cost

        history.append(best_cost)

        temperature *= cooling_rate

    return best, history


def main():
    env = TSPEnvironment(
    C1=25.0,
    C2=1.0,
    alpha=10.0,
    beta=10.0,
    drone_endurance=120.0,
    )

    env.load_from_txt(Path("data") / "singlecenter" / INSTANCE)

    # GRASP
    grasp_solver = GRASPSolver(
        environment=env,
        max_iterations=100,
        k_max=5,
    )

    print("Running GRASP...")
    grasp_start = time.perf_counter()
    grasp_solution = grasp_solver.solve()
    grasp_runtime = time.perf_counter() - grasp_start

    # SA
    print("Running Simulated Annealing...")
    initial_solution = grasp_solver._truck_only_solution(
        grasp_solver._nearest_neighbor_tour()
    )

    sa_start = time.perf_counter()

    sa_solution, sa_history = simulated_annealing(
        grasp_solver,
        initial_solution,
        max_iterations=500,
    )

    sa_runtime = time.perf_counter() - sa_start

    # CSV
    rows = [
        {
            "algorithm": "GRASP",
            "cost": round(grasp_solution.total_cost, 4),
            "runtime_seconds": round(grasp_runtime, 4),
        },
        {
            "algorithm": "SimulatedAnnealing",
            "cost": round(sa_solution.total_cost, 4),
            "runtime_seconds": round(sa_runtime, 4),
        },
    ]

    output_csv = Path("results/csv/sa_comparison.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(sa_history)

    plt.xlabel("Iteration")
    plt.ylabel("Best Cost")
    plt.title("Simulated Annealing Convergence")

    output_plot = Path("results/figures/sa_convergence.png")
    output_plot.parent.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_plot, dpi=200)
    plt.close()

    print("\n=== Comparison Results ===")
    print(f"GRASP Cost: {grasp_solution.total_cost:.2f}")
    print(f"GRASP Runtime: {grasp_runtime:.2f}s")

    print(f"SA Cost: {sa_solution.total_cost:.2f}")
    print(f"SA Runtime: {sa_runtime:.2f}s")

    print(f"\nSaved: {output_csv}")
    print(f"Saved: {output_plot}")


if __name__ == "__main__":
    main()