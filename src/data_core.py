import math
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
class Node:
    def __init__(self, node_id, x, y, is_drone_eligible=True):
        self.id = node_id
        self.x = x
        self.y = y
        self.is_drone_eligible = is_drone_eligible

    def __repr__(self):
        return f"Node({self.id}, {self.x}, {self.y})"


class TSPEnvironment:
    def __init__(self):
        self.nodes = []
        self.truck_dist_matrix = []
        self.drone_dist_matrix = []

        # Default parameters
        self.C1 = 1.0               # Truck cost per unit distance
        self.C2 = 0.2               # Drone cost per unit distance
        self.alpha = 0.0            # Truck waiting penalty
        self.beta = 0.0             # Drone waiting penalty
        self.drone_endurance = 20.0 # Maximum drone flight time (minutes)
        self.truck_speed = 40.0     # km/h
        self.drone_speed = 60.0     # km/h

    def add_node(self, node):
        self.nodes.append(node)

    # --- Method for loading data from a CSV file. ---
    def load_from_csv(self, uploaded_file):
        """
        CSV formatı: id, lat, lon, drone_eligible
        id=0 olan satırı merkez (0,0) kabul eder.
        """
        df = pd.read_csv(uploaded_file)
        
        # First, let's find the repository (id=0).
        depot_row = df[df['id'] == 0].iloc[0]
        depot_lat = depot_row['lat']
        depot_lon = depot_row['lon']

        self.nodes = []
        
        for _, row in df.iterrows():
            # Converting latitude/longitude difference to approximate kilometers.
            # 1 degree latitude ~ 111km
            # 1degrees longitude ~ 111km * cos(latitude)
            y_km = (row['lat'] - depot_lat) * 111.0
            x_km = (row['lon'] - depot_lon) * (111.0 * math.cos(math.radians(depot_lat)))
            
            new_node = Node(
                node_id=int(row['id']),
                x=x_km,
                y=y_km,
                is_drone_eligible=bool(row['drone_eligible'])
            )
            self.add_node(new_node)
        
        print(f"Successfully loaded {len(self.nodes)} nodes from CSV.")

    def calculate_distance_matrices(self):
        n = len(self.nodes)
        self.truck_dist_matrix = np.zeros((n, n))
        self.drone_dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    node_a = self.nodes[i]
                    node_b = self.nodes[j]

                    euclidean_dist = math.sqrt(
                        (node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2
                    )
                    self.drone_dist_matrix[i][j] = euclidean_dist

                    # Distance to Manhattan (Street type) for truck.
                    manhattan_dist = abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)
                    self.truck_dist_matrix[i][j] = manhattan_dist

    def generate_random_instance(self, num_customers, area_size):
        self.nodes = []
        depot = Node(node_id=0, x=0.0, y=0.0, is_drone_eligible=False)
        self.add_node(depot)
        max_coord = math.sqrt(area_size)

        for i in range(1, num_customers + 1):
            x = random.uniform(0, max_coord)
            y = random.uniform(0, max_coord)
            is_eligible = random.random() < 0.80
            self.add_node(Node(node_id=i, x=x, y=y, is_drone_eligible=is_eligible))

    # --- MATPLOTLIB PLOTS (Available for debugging) ---
    def plot_nodes(self):
        if not self.nodes: return
        xs = [node.x for node in self.nodes]
        ys = [node.y for node in self.nodes]
        plt.figure(figsize=(8, 6))
        plt.scatter(xs[0], ys[0], c="red", marker="s", s=100, label="Depot")
        plt.scatter(xs[1:], ys[1:], c="blue", marker="o", label="Customers")
        plt.grid(True)
        plt.show()

def plot_solution(self, solution):
        """
        Visualizes the final truck route and drone deliveries using Matplotlib.
        Truck route: solid black line
        Drone deliveries: dashed orange lines
        """
        if not self.nodes or solution is None:
            print("No nodes or solution available to plot.")
            return

        plt.figure(figsize=(12, 8))
        
        # 1. Plot all nodes
        xs = [node.x for node in self.nodes]
        ys = [node.y for node in self.nodes]
        
        # Plot Customers
        plt.scatter(xs[1:], ys[1:], c="royalblue", marker="o", s=100, label="Customers", zorder=5)
        # Plot Depot (Node 0)
        plt.scatter(xs[0], ys[0], c="red", marker="s", s=200, label="Depot (Start/End)", zorder=6)

        # Add ID labels to nodes
        for node in self.nodes:
            plt.annotate(f" {node.id}", (node.x, node.y), fontsize=9, fontweight='bold')

        # 2. Plot Truck Route (Solid Black Line)
        truck_route = solution.truck_route
        for i in range(len(truck_route) - 1):
            start_node = self.nodes[truck_route[i]]
            end_node = self.nodes[truck_route[i+1]]
            
            plt.plot(
                [start_node.x, end_node.x], 
                [start_node.y, end_node.y], 
                color="black", 
                linestyle="-", 
                linewidth=2.5, 
                alpha=0.8,
                label="Truck Route" if i == 0 else ""
            )

        # 3. Plot Drone Deliveries (Dashed Orange Line)
        for idx, (launch, target, rendezvous) in enumerate(solution.drone_deliveries):
            l_node = self.nodes[launch]
            t_node = self.nodes[target]
            r_node = self.nodes[rendezvous]

            # Path: Launch -> Target -> Rendezvous
            plt.plot(
                [l_node.x, t_node.x, r_node.x], 
                [l_node.y, t_node.y, r_node.y], 
                color="orange", 
                linestyle="--", 
                linewidth=1.8,
                label="Drone Flight" if idx == 0 else ""
            )
            # Mark the drone target specifically
            plt.scatter(t_node.x, t_node.y, c="orange", marker="^", s=120, zorder=7)

        # Final touches
        plt.title(f"TSP-D Final Solution\nTotal Cost: ${solution.total_cost:.2f} | Total Time: {solution.total_time:.1f} min", fontsize=14)
        plt.xlabel("Distance X (km)")
        plt.ylabel("Distance Y (km)")
        plt.legend(loc="upper right")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.axis("equal") # Keep the aspect ratio square
        
        plt.show()