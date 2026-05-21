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
        
        # Hızlar txt dosyasından okunacak (Başlangıçta 0)
        self.truck_speed = 0.0
        self.drone_speed = 0.0
        
        # Makalenin sabit parametreleri (Dışarıdan değiştirilebilir)
        self.C1 = C1                  # Kamyon birim maliyeti
        self.C2 = C2                  # Dron birim maliyeti
        self.alpha = alpha            # Kamyon bekleme cezası
        self.beta = beta              # Dron bekleme cezası
        self.drone_endurance = drone_endurance # Dron max uçuş süresi (dk)
    
    def load_from_txt(self, file_path):
        """
        Zenodo txt dosyalarını okur ve makalenin istediği formata çevirir.
        """
        self.nodes = []
        with open(file_path, 'r') as f:
            # Yorum satırlarını (/* ... */) atla
            lines = [line.strip() for line in f if line.strip() and not line.startswith('/*')]
        
        # Dosyanın ilk 2 satırından hızları al (Makale kuralı)
        self.truck_speed = float(lines[0])
        self.drone_speed = float(lines[1])
        num_nodes = int(lines[2])
        
        # Depo verisi (Node 0)
        depot_data = lines[3].split()
        self.add_node(Node(node_id=0, x=float(depot_data[0]), y=float(depot_data[1]), name="depot", is_drone_eligible=False))
        
        # Müşteriler
        for i in range(1, num_nodes):
            data = lines[3 + i].split()
            # Makaledeki %80 drona uygunluk kuralı
            is_eligible = True if random.random() < 0.80 else False
            self.add_node(Node(node_id=i, x=float(data[0]), y=float(data[1]), name=data[2], is_drone_eligible=is_eligible))
            
        self.calculate_distance_matrices()

    def add_node(self, node):
        self.nodes.append(node)

    def calculate_distance_matrices(self):
        n = len(self.nodes)
        self.truck_dist_matrix = np.zeros((n, n))
        self.drone_dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    node_a = self.nodes[i]
                    node_b = self.nodes[j]

                    # Makalede hem kamyon hem dron için Öklid (Kuş uçuşu) mesafesi kullanılır
                    euclidean_dist = math.sqrt(
                        (node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2
                    )
                    
                    self.truck_dist_matrix[i][j] = euclidean_dist
                    self.drone_dist_matrix[i][j] = euclidean_dist


def load_dataset(file_path):
    """
    Zenodo TXT dosyalarını okuyup Environment objesi döndürür.
    Hocanın dediği gibi veriler (hızlar, koordinatlar) direkt dosyadan alınır.
    """
    # Parametreler dışarıdan veriliyor, kodun içine gömülü değil!
    env = TSPEnvironment(C1=25.0, C2=1.0, alpha=10.0, beta=10.0, drone_endurance=20.0)
    
    with open(file_path, 'r') as f:
        # Yorum satırlarını (/*...*/) ve boş satırları atla
        lines = [line.strip() for line in f if line.strip() and not line.startswith('/*')]
    
    # 1. Hızları DOSYADAN oku (Hocanın kuralı)
    env.truck_speed = float(lines[0])
    env.drone_speed = float(lines[1])
    num_nodes = int(lines[2])
    
    # 2. Depoyu Oku (ID = 0)
    depot_data = lines[3].split()
    depot = Node(0, float(depot_data[0]), float(depot_data[1]), depot_data[2], is_drone_eligible=False)
    env.add_node(depot)
    
    # 3. Müşterileri Oku
    for i in range(1, num_nodes):
        data = lines[3 + i].split()
        
        # Eğer dosyada dron uygunluğu yoksa, makaledeki %80 kuralını uygularız
        is_eligible = True if random.random() <= 0.8 else False
        
        node = Node(i, float(data[0]), float(data[1]), data[2], is_drone_eligible=is_eligible)
        env.add_node(node)
        
    # Uzaklık matrislerini hesapla
    env.calculate_distance_matrices()
    
    print(f"Dataset loaded: {num_nodes} nodes.")
    print(f"Truck Speed: {env.truck_speed}, Drone Speed: {env.drone_speed}")
    return env


def plot_solution(env, solution):
    """
    Sizin yazdığınız harika görselleştirme kodunun güncellenmiş hali.
    """
    if not env.nodes or solution is None:
        print("No nodes or solution available to plot.")
        return

    plt.figure(figsize=(12, 8))
    
    # 1. Tüm Düğümleri Çiz
    xs = [node.x for node in env.nodes]
    ys = [node.y for node in env.nodes]
    
    # Müşteriler ve Depo
    plt.scatter(xs[1:], ys[1:], c="royalblue", marker="o", s=100, label="Customers", zorder=5)
    plt.scatter(xs[0], ys[0], c="red", marker="s", s=200, label="Depot (Start/End)", zorder=6)

    # Düğüm ID'lerini yaz
    for node in env.nodes:
        plt.annotate(f" {node.id}", (node.x, node.y), fontsize=9, fontweight='bold')

    # 2. Kamyon Rotası (Siyah Düz Çizgi)
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

    # 3. Dron Uçuşları (Turuncu Kesik Çizgi)
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
        # Dron hedefini üçgen ile işaretle
        plt.scatter(t_node.x, t_node.y, c="orange", marker="^", s=120, zorder=7)

    plt.title(f"TSP-D Final Solution\nTotal Cost: ${solution.total_cost:.2f} | Total Time: {solution.total_time:.1f} min", fontsize=14)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.axis("equal") 
    
    return plt.gcf()

# ÖRNEK KULLANIM:
# my_env = load_dataset("uniform_n10.txt") 
# solver = GRASPSolver(my_env, max_iterations=100) # Algoritmayı çağır
# best_sol = solver.solve()
# plot_solution(my_env, best_sol) # Çizdir