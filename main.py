from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver

def main():
    print("--- Drone Project is Being Launched ---")
    
    # 1. Create environment
    env = TSPEnvironment()
    
    # 2. Simulate one of instances of class "B" from article:
    # 50 Customers, 100 km2 area
    env.generate_random_instance(num_customers=50, area_size=100)
    
    # 3. Calculate distance matrices
    env.calculate_distance_matrices()
    
    print("Distance matrices were successfully generated.")
    print(f"Total Number of Nodes (including Warehouse): {len(env.nodes)}")
    
    # 4. Visualize Data (Preparation for Live Demo)
    print("Map is being drawn on the screen... (The program ends when you close graphics window)")
    env.plot_nodes()

    solver = GRASPSolver(environment=env, max_iterations=10)
    best_sol = solver.solve()
    print("Solution Found:", best_sol)

if __name__ == "__main__":
    main()