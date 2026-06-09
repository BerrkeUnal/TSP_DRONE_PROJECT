import time
from pathlib import Path

import matplotlib.pyplot as plt

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver


SELECTED_INSTANCE = "singlecenter-72-n50.txt"


def run_convergence_analysis():
    instance_path = Path("data") / "singlecenter" / SELECTED_INSTANCE

    env = TSPEnvironment(
    C1=25.0,
    C2=1.0,
    alpha=10.0,
    beta=10.0,
    drone_endurance=120.0,
    )
    env.load_from_txt(instance_path)

    max_iterations = 100
    solver = GRASPSolver(environment=env, max_iterations=max_iterations, k_max=5)

    best_costs = []
    best_cost = float("inf")

    start_time = time.perf_counter()

    for iteration in range(1, max_iterations + 1):
        solver.max_iterations = 1
        solution = solver.solve()

        if solution.total_cost < best_cost:
            best_cost = solution.total_cost

        best_costs.append(best_cost)

        print(f"Iteration {iteration}: Best Cost = {best_cost:.2f}")

    runtime = time.perf_counter() - start_time

    output_dir = Path("results") / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, max_iterations + 1), best_costs, marker="o", markersize=3)
    plt.xlabel("Iteration")
    plt.ylabel("Best Cost")
    plt.title(f"Convergence Plot - {SELECTED_INSTANCE}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_dir / "convergence_plot.png", dpi=200)
    plt.close()

    print(f"Convergence analysis completed in {runtime:.2f} seconds.")
    print("Saved: results/figures/convergence_plot.png")


if __name__ == "__main__":
    run_convergence_analysis()