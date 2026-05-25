import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver


INSTANCE = "singlecenter-72-n50.txt"
ITERATION_VALUES = [20, 50, 100, 200]
K_VALUES = [3, 5, 10]


def run_solver(iterations, k_max):
    env = TSPEnvironment(C1=25.0, C2=1.0, alpha=10.0, beta=10.0)
    env.load_from_txt(Path("data") / "singlecenter" / INSTANCE)

    solver = GRASPSolver(environment=env, max_iterations=iterations, k_max=k_max)

    start = time.perf_counter()
    solution = solver.solve()
    runtime = time.perf_counter() - start

    return {
        "instance": INSTANCE,
        "iterations": iterations,
        "k_max": k_max,
        "cost": round(solution.total_cost, 4),
        "runtime_seconds": round(runtime, 4),
        "drone_deliveries": len(solution.drone_deliveries),
    }


def write_csv(rows):
    output = Path("results/csv/parameter_tuning_results.csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {output}")


def plot_cost(rows):
    output = Path("results/figures/parameter_tuning_cost.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))

    for k in K_VALUES:
        subset = [row for row in rows if row["k_max"] == k]
        x = [row["iterations"] for row in subset]
        y = [row["cost"] for row in subset]
        plt.plot(x, y, marker="o", label=f"k={k}")

    plt.xlabel("Iterations")
    plt.ylabel("Best Cost")
    plt.title("Parameter Tuning: Iterations vs Cost")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()

    print(f"Saved: {output}")


def plot_runtime(rows):
    output = Path("results/figures/parameter_tuning_runtime.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))

    for k in K_VALUES:
        subset = [row for row in rows if row["k_max"] == k]
        x = [row["iterations"] for row in subset]
        y = [row["runtime_seconds"] for row in subset]
        plt.plot(x, y, marker="o", label=f"k={k}")

    plt.xlabel("Iterations")
    plt.ylabel("Runtime (seconds)")
    plt.title("Parameter Tuning: Iterations vs Runtime")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()

    print(f"Saved: {output}")


def main():
    rows = []

    for iterations in ITERATION_VALUES:
        for k in K_VALUES:
            print(f"Running iterations={iterations}, k_max={k}...")
            row = run_solver(iterations, k)
            rows.append(row)
            print(
                f"Done | iterations={iterations}, k={k}, "
                f"cost={row['cost']}, runtime={row['runtime_seconds']}s"
            )

    write_csv(rows)
    plot_cost(rows)
    plot_runtime(rows)

    print("Parameter tuning completed.")


if __name__ == "__main__":
    main()