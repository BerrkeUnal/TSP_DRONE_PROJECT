import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt

from src.data_core import TSPEnvironment, plot_solution
from src.optimizer import GRASPSolver


SELECTED_INSTANCES = [
    "singlecenter-51-n10.txt",
    "singlecenter-52-n10.txt",
    "singlecenter-53-n10.txt",
    "singlecenter-71-n50.txt",
    "singlecenter-72-n50.txt",
    "singlecenter-73-n50.txt",
    "singlecenter-91-n100.txt",
    "singlecenter-92-n100.txt",
    "singlecenter-93-n100.txt",
]


def run_instance(instance_file: str, max_iterations: int = 100, k_max: int = 5) -> dict:
    instance_path = Path("data") / "singlecenter" / instance_file

    env = TSPEnvironment(
        C1=25.0,
        C2=1.0,
        alpha=10.0,
        beta=10.0,
    )
    env.load_from_txt(instance_path)

    solver = GRASPSolver(
        environment=env,
        max_iterations=max_iterations,
        k_max=k_max,
    )

    start_time = time.perf_counter()
    best_solution = solver.solve()
    runtime = time.perf_counter() - start_time

    baseline = solver.baseline_solution

    improvement_percent = (
        ((baseline.total_cost - best_solution.total_cost) / baseline.total_cost) * 100
        if baseline and baseline.total_cost > 0
        else 0
    )

    figure_path = Path("results") / "figures" / f"{instance_file.replace('.txt', '')}.png"
    fig = plot_solution(env, best_solution)
    fig.savefig(figure_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return {
        "instance": instance_file,
        "node_count": len(env.nodes),
        "truck_speed": env.truck_speed,
        "drone_speed": env.drone_speed,
        "baseline_truck_only_cost": round(baseline.total_cost, 4),
        "grasp_tspd_cost": round(best_solution.total_cost, 4),
        "improvement_percent": round(improvement_percent, 4),
        "runtime_seconds": round(runtime, 4),
        "truck_stops": len(best_solution.truck_route),
        "drone_deliveries": len(best_solution.drone_deliveries),
        "truck_route": str(best_solution.truck_route),
        "drone_delivery_list": str(best_solution.drone_deliveries),
    }


def write_csv(rows: list[dict]) -> None:
    output_path = Path("results") / "csv" / "singlecenter_comparison.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(rows: list[dict]) -> None:
    labels = [row["instance"].replace("singlecenter-", "").replace(".txt", "") for row in rows]
    baseline_costs = [row["baseline_truck_only_cost"] for row in rows]
    grasp_costs = [row["grasp_tspd_cost"] for row in rows]

    x = range(len(rows))
    width = 0.35

    plt.figure(figsize=(14, 6))
    plt.bar([i - width / 2 for i in x], baseline_costs, width=width, label="Truck-only baseline")
    plt.bar([i + width / 2 for i in x], grasp_costs, width=width, label="GRASP TSP-D")

    plt.xticks(list(x), labels, rotation=45)
    plt.ylabel("Total Cost")
    plt.title("Singlecenter Benchmark Comparison")
    plt.legend()
    plt.tight_layout()

    output_path = Path("results") / "figures" / "singlecenter_comparison.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def main() -> None:
    rows = []

    for instance_file in SELECTED_INSTANCES:
        print(f"Running {instance_file}...")
        row = run_instance(
            instance_file=instance_file,
            max_iterations=100,
            k_max=5,
        )
        rows.append(row)

        print(
            f"Done: {instance_file} | "
            f"baseline={row['baseline_truck_only_cost']} | "
            f"grasp={row['grasp_tspd_cost']} | "
            f"improvement={row['improvement_percent']}% | "
            f"time={row['runtime_seconds']}s"
        )

    write_csv(rows)
    plot_summary(rows)

    print("Benchmark completed.")
    print("CSV: results/csv/singlecenter_comparison.csv")
    print("Figure: results/figures/singlecenter_comparison.png")


if __name__ == "__main__":
    main()