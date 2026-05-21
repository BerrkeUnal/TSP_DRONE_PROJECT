import math
import random
import numpy as np
import matplotlib.pyplot as plt

class Node:
    def __init__(self, node_id, x, y, name="loc", is_drone_eligible=True):
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name
        self.is_drone_eligible = is_drone_eligible

    def __repr__(self):
        return f"Node({self.id}, {self.x}, {self.y})"


class TSPEnvironment:
    def __init__(self, C1=25.0, C2=1.0, alpha=10.0, beta=10.0, drone_endurance=20.0):
        self.nodes = []
        self.truck_dist_matrix = []
        self.drone_dist_matrix = []
        
        # Speeds will be read from the dataset file
        self.truck_speed = 0.0
        self.drone_speed = 0.0
        
        # Paper parameters (can be overridden)
        self.C1 = C1                  # Unit cost of the truck
        self.C2 = C2                  # Unit cost of the drone
        self.alpha = alpha            # Waiting penalty coefficient for the truck
        self.beta = beta              # Waiting penalty coefficient for the drone
        self.drone_endurance = drone_endurance # Drone maximum flight endurance (minutes)
    
    def _parse_dataset_lines(self, lines):
        """
        Internal method to parse the lines extracted from either a local file or a Streamlit uploaded file.
        Formats the environment according to the Ha et al. (2018) min-cost TSP-D paper.
        """
        self.nodes = []
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Boş satırları ve /* ile başlayan yorumları atla
            if not line or line.startswith('/*'):
                continue
            
            # #MAXFLY varsa drone dayanıklılığını güncelle
            if line.startswith('#MAXFLY'):
                self.drone_endurance = float(line.split()[1])
                continue
                
            # YENİ EKLENEN KISIM: #NOVISIT gibi # ile başlayan diğer tüm etiketleri atla
            if line.startswith('#'):
                continue
                
            clean_lines.append(line)
            
        # Makaleye göre ilk satır kamyon, ikinci satır dron hızıdır
        self.truck_speed = float(clean_lines[0])
        self.drone_speed = float(clean_lines[1])
        num_nodes = int(clean_lines[2])
        
        # Depo verisi (Node 0)
        depot_data = clean_lines[3].split()
        self.add_node(Node(node_id=0, x=float(depot_data[0]), y=float(depot_data[1]), name=depot_data[2], is_drone_eligible=False))
        
        # Müşteriler
        for i in range(1, num_nodes):
            data = clean_lines[3 + i].split()
            # Müşterilerin %80'i drone ile teslimata uygundur
            is_eligible = True if random.random() <= 0.80 else False
            self.add_node(Node(node_id=i, x=float(data[0]), y=float(data[1]), name=data[2], is_drone_eligible=is_eligible))
            
        self.calculate_distance_matrices()

    def load_from_txt(self, file_path):
        """Reads the Zenodo format txt files locally."""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self._parse_dataset_lines(lines)
        
    def load_from_streamlit_file(self, uploaded_file):
        """Reads the Zenodo format txt file from a Streamlit UploadedFile object."""
        content = uploaded_file.getvalue().decode("utf-8")
        lines = content.split('\n')
        self._parse_dataset_lines(lines)

    def add_node(self, node):
        self.nodes.append(node)

    def calculate_distance_matrices(self):
        """
        Calculates distance matrices.
        According to Ha et al. (2018) Section 6:
        - Truck distance (d_ij) uses Manhattan distance.
        - Drone distance (d'_ij) uses Euclidean distance.
        """
        n = len(self.nodes)
        self.truck_dist_matrix = np.zeros((n, n))
        self.drone_dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    node_a = self.nodes[i]
                    node_b = self.nodes[j]

                    # Euclidean distance for the drone
                    euclidean_dist = math.sqrt(
                        (node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2
                    )
                    
                    # Manhattan distance for the truck
                    manhattan_dist = abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)
                    
                    self.truck_dist_matrix[i][j] = manhattan_dist
                    self.drone_dist_matrix[i][j] = euclidean_dist


def plot_solution(env, solution):
    """
    Visualizes the final TSP-D routes.
    """
    if not env.nodes or solution is None:
        print("No nodes or solution available to plot.")
        return

    plt.figure(figsize=(12, 8))
    
    # 1. Plot all nodes
    xs = [node.x for node in env.nodes]
    ys = [node.y for node in env.nodes]
    
    # Customers and Depot
    plt.scatter(xs[1:], ys[1:], c="royalblue", marker="o", s=100, label="Customers", zorder=5)
    plt.scatter(xs[0], ys[0], c="red", marker="s", s=200, label="Depot (Start/End)", zorder=6)

    # Annotate Node IDs
    for node in env.nodes:
        plt.annotate(f" {node.id}", (node.x, node.y), fontsize=9, fontweight='bold')

    # 2. Truck Route (Solid Black Line)
    truck_route = solution.truck_route
    for i in range(len(truck_route) - 1):
        start_node = env.nodes[truck_route[i]]
        end_node = env.nodes[truck_route[i+1]]
        
        plt.plot(
            [start_node.x, end_node.x], 
            [start_node.y, end_node.y], 
            color="black", 
            linestyle="-", 
            linewidth=2.5, 
            alpha=0.8,
            label="Truck Route" if i == 0 else ""
        )

    # 3. Drone Flights (Dashed Orange Line)
    for idx, (launch, target, rendezvous) in enumerate(solution.drone_deliveries):
        l_node = env.nodes[launch]
        t_node = env.nodes[target]
        r_node = env.nodes[rendezvous]

        # Launch -> Target -> Rendezvous
        plt.plot(
            [l_node.x, t_node.x, r_node.x], 
            [l_node.y, t_node.y, r_node.y], 
            color="orange", 
            linestyle="--", 
            linewidth=1.8,
            label="Drone Flight" if idx == 0 else ""
        )
        # Mark drone target with a triangle
        plt.scatter(t_node.x, t_node.y, c="orange", marker="^", s=120, zorder=7)

    plt.title(f"TSP-D Final Solution\nTotal Cost: ${solution.total_cost:.2f} | Total Time: {solution.total_time:.1f} min", fontsize=14)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.axis("equal") 
    
    return plt.gcf()