import math
import numpy as np
import matplotlib.pyplot as plt
import random

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
        
        # Paper parameters (Default values based on the article)
        self.C1 = 25.0              # Truck cost per unit distance
        self.C2 = 1.0               # Drone cost per unit distance
        self.alpha = 10.0           # Truck waiting penalty per unit time
        self.beta = 10.0            # Drone waiting penalty per unit time
        self.drone_endurance = 20.0 # Maximum drone flight time (minutes)
        self.truck_speed = 40.0     # km/h
        self.drone_speed = 40.0     # km/h

    def add_node(self, node):
        """Adds a single customer or depot to the environment."""
        self.nodes.append(node)

    def calculate_distance_matrices(self):
        """
        Calculates the distance matrices for both the truck and the drone.
        Truck uses Manhattan distance.
        Drone uses Euclidean distance.
        """
        n = len(self.nodes)
        self.truck_dist_matrix = np.zeros((n, n))
        self.drone_dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    node_a, node_b = self.nodes[i], self.nodes[j]
                    
                    # Drone: Euclidean Distance
                    euclidean_dist = math.sqrt((node_a.x - node_b.x)**2 + (node_a.y - node_b.y)**2)
                    self.drone_dist_matrix[i][j] = euclidean_dist
                    
                    # Truck: Manhattan Distance
                    manhattan_dist = abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)
                    self.truck_dist_matrix[i][j] = manhattan_dist

    def plot_nodes(self):
        """Plots the depot and customers for visual verification."""
        if not self.nodes:
            print("No nodes to plot.")
            return

        xs = [node.x for node in self.nodes]
        ys = [node.y for node in self.nodes]
        
        plt.figure(figsize=(8, 6))
        # Plot Depot (First node)
        plt.scatter(xs[0], ys[0], c='red', marker='s', s=100, label='Depot')
        # Plot Customers
        plt.scatter(xs[1:], ys[1:], c='blue', marker='o', label='Customers')
        
        for node in self.nodes:
            plt.annotate(node.id, (node.x + 0.5, node.y + 0.5))

        plt.title("TSP-D Customer Distribution")
        plt.legend()
        plt.grid(True)
        plt.show()


    def generate_random_instance(self, num_customers, area_size):
            """
            Generates a random benchmark instance based on the paper's rules.
            - Depot is at (0,0)
            - 80% of customers are drone-eligible
            """
            self.nodes = [] # Clear existing nodes
            
            # Add Depot
            depot = Node(node_id=0, x=0.0, y=0.0, is_drone_eligible=False)
            self.add_node(depot)
            
            # Calculate grid boundaries based on area_size (e.g., 100 km2 -> 10x10 grid)
            max_coord = math.sqrt(area_size)
            
            for i in range(1, num_customers + 1):
                x = random.uniform(0, max_coord)
                y = random.uniform(0, max_coord)
                
                # 80% chance to be drone eligible
                is_eligible = random.random() < 0.80 
                
                self.add_node(Node(node_id=i, x=x, y=y, is_drone_eligible=is_eligible))
                
            print(f"Generated {num_customers} customers in a {area_size} km2 area.")