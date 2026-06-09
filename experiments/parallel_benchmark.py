import csv
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

from src.data_core import TSPEnvironment
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


def run_instance(instance_file):
    env = TSPEnvironment(
    C1=25.0,
    C2=1.0,
    alpha=10.0,
    beta=10.0,
    drone_endurance=120.0,
    )

    env.load_from_txt(Path("data") / "singlecenter" / instance_file)

    solver = GRASPSolver(
        environment=env,
        max_iterations=100,
        k_max=5,
    )

    start = time.perf_counter()

    solution = solver.solve()

    runtime = time.perf_counter() - start

    return {
        "instance": instance_file,
        "cost": round(solution.total_cost, 4),
        "runtime_seconds": round(runtime, 4),
        "drone_deliveries": len(solution.drone_deliveries),
    }


def main():
    print(f"Using {cpu_count()} CPU cores")

    start_total = time.perf_counter()

    with Pool(processes=min(4, cpu_count())) as pool:
        results = pool.map(run_instance, SELECTED_INSTANCES)

    total_runtime = time.perf_counter() - start_total

    output_path = Path("results/csv/parallel_benchmark.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\n=== Parallel Benchmark Results ===")

    for row in results:
        print(
            f"{row['instance']} | "
            f"Cost={row['cost']} | "
            f"Runtime={row['runtime_seconds']}s"
        )

    print(f"\nTotal Parallel Runtime: {total_runtime:.2f}s")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()