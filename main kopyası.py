from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver
import matplotlib.pyplot as plt


def run_single_scenario(num_customers, area_size, max_iterations=10, k_max=4, draw_solution=False):
    print("\n" + "=" * 60)
    print(f"SCENARIO: {num_customers} customers | area = {area_size} km2")
    print("=" * 60)

    env = TSPEnvironment()
    env.generate_random_instance(num_customers=num_customers, area_size=area_size)
    env.calculate_distance_matrices()

    solver = GRASPSolver(environment=env, max_iterations=max_iterations, k_max=k_max)
    best_sol = solver.solve()

    print("Solution Found:", best_sol)
    print("Truck Route:", best_sol.truck_route)
    print("Drone Deliveries:", best_sol.drone_deliveries)

    baseline_cost = None
    improvement = None

    if solver.baseline_solution is not None:
        baseline_cost = solver.baseline_solution.total_cost
        best_cost = best_sol.total_cost
        improvement = ((baseline_cost - best_cost) / baseline_cost) * 100.0

        print("\n--- Benchmark Comparison ---")
        print(f"Truck-only baseline cost: {baseline_cost:.2f}")
        print(f"TSP-D best cost: {best_cost:.2f}")
        print(f"Improvement: {improvement:.2f}%")

    if draw_solution:
        print("\nFinal solution map is being drawn...")
        env.plot_solution(best_sol)

    return {
        "customers": num_customers,
        "baseline_cost": baseline_cost,
        "best_cost": best_sol.total_cost,
        "improvement": improvement,
        "truck_stops": len(best_sol.truck_route),
        "drone_deliveries": len(best_sol.drone_deliveries),
        "iteration_history": solver.iteration_history,
        "best_cost_history": solver.best_cost_history,
    }


def plot_iteration_graph(iterations, costs):
    plt.figure(figsize=(8, 5))
    plt.plot(iterations, costs, marker="o")
    plt.title("GRASP Progress: Iteration vs Best Cost")
    plt.xlabel("Iteration")
    plt.ylabel("Best Cost")
    plt.grid(True)
    plt.show()


def plot_truck_vs_drone(results):
    labels = [str(r["customers"]) for r in results]
    truck_counts = [r["truck_stops"] for r in results]
    drone_counts = [r["drone_deliveries"] for r in results]

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar([i - width / 2 for i in x], truck_counts, width=width, label="Truck Stops")
    plt.bar([i + width / 2 for i in x], drone_counts, width=width, label="Drone Deliveries")
    plt.xticks(list(x), labels)
    plt.xlabel("Number of Customers")
    plt.ylabel("Count")
    plt.title("Truck Stops vs Drone Deliveries")
    plt.legend()
    plt.grid(True, axis="y")
    plt.show()


def plot_benchmark_improvement(results):
    labels = [str(r["customers"]) for r in results]
    improvements = [r["improvement"] if r["improvement"] is not None else 0 for r in results]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, improvements)
    plt.xlabel("Number of Customers")
    plt.ylabel("Improvement (%)")
    plt.title("Benchmark Improvement over Truck-Only Baseline")
    plt.grid(True, axis="y")
    plt.show()


def main():
    # Demo scenario
    main_result = run_single_scenario(
        num_customers=50,
        area_size=100,
        max_iterations=10,
        k_max=4,
        draw_solution=True
    )

    plot_iteration_graph(main_result["iteration_history"], main_result["best_cost_history"])

    # Lighter benchmark scenarios
    scenario_results = []
    for n in [50, 100]:
        result = run_single_scenario(
            num_customers=n,
            area_size=100,
            max_iterations=5,
            k_max=3,
            draw_solution=False
        )
        scenario_results.append(result)

    print("\nALL SCENARIOS COMPLETED. DRAWING GRAPHS...")
    plot_truck_vs_drone(scenario_results)
    plot_benchmark_improvement(scenario_results)


if __name__ == "__main__":
    main()