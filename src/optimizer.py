import random

class TSPD_Solution:
    def __init__(self):
        self.truck_route = []
        self.drone_deliveries = []
        self.total_cost = float("inf")
        self.total_time = 0.0

    def copy(self):
        new_sol = TSPD_Solution()
        new_sol.truck_route = self.truck_route.copy()
        new_sol.drone_deliveries = self.drone_deliveries.copy()
        new_sol.total_cost = self.total_cost
        new_sol.total_time = self.total_time
        return new_sol

    def __repr__(self):
        return (
            f"Solution(Cost: {self.total_cost:.2f}, "
            f"Truck Stops: {len(self.truck_route)}, "
            f"Drone Deliveries: {len(self.drone_deliveries)})"
        )


class GRASPSolver:
    def __init__(self, environment, max_iterations=2000, k_max=5):
        self.env = environment
        self.max_iterations = max_iterations # IE Raporuna göre T_max = 2000
        self.k_max = k_max                   # IE Raporuna göre k_max = 5
        self.best_solution = TSPD_Solution()
        self.baseline_solution = None

        # chart data
        self.iteration_history = []
        self.best_cost_history = []

    def solve(self):
        print(f"Starting GRASP Algorithm... (Max Iterations: {self.max_iterations})")

        # Baseline olarak basit bir çözüm tutuyoruz
        baseline_tour = self._nearest_neighbor_tour(k=1)
        self.baseline_solution = self._truck_only_solution(baseline_tour)

        current_best = float("inf")

        for iteration in range(1, self.max_iterations + 1):
            # Adım 1: Adaptive K hesaplama
            k = self._adaptive_k(iteration)

            # Adım 2: Çoklu Başlangıç (Multi-start)
            tour_nn = self._nearest_neighbor_tour(k)
            tour_ins = self._insertion_heuristic_tour(k)

            cost_nn = self._calculate_truck_only_cost(tour_nn)
            cost_ins = self._calculate_truck_only_cost(tour_ins)

            # En iyi başlangıç rotasını seçme
            giant_tour = tour_nn if cost_nn <= cost_ins else tour_ins

            # Adım 3: Split Procedure
            current_solution = self._apply_split_procedure(giant_tour)
            
            # Adım 4: Guided Local Search
            improved_solution = self._local_search(current_solution)

            # Adım 5: En iyi çözümü güncelleme
            if improved_solution.total_cost < self.best_solution.total_cost:
                self.best_solution = improved_solution
                print(
                    f"New best solution found! "
                    f"Iteration: {iteration} | Cost: {self.best_solution.total_cost:.2f}"
                )

            current_best = min(current_best, self.best_solution.total_cost)
            self.iteration_history.append(iteration)
            self.best_cost_history.append(current_best)

        print("Optimization completed!")
        return self.best_solution

    def _adaptive_k(self, iteration):
        # k(t) = max(1, round(k_max * (1 - t / T_max)))
        if self.max_iterations <= 1:
            return 1
        ratio = 1 - (iteration / self.max_iterations)
        return max(1, round(self.k_max * ratio))

    def _truck_only_solution(self, route):
        sol = TSPD_Solution()
        sol.truck_route = route.copy()
        sol.drone_deliveries = []
        sol.total_cost = self._calculate_truck_only_cost(route)
        sol.total_time = self._calculate_truck_only_time(route)
        return sol

    def _nearest_neighbor_tour(self, k=1):
        customer_ids = [node.id for node in self.env.nodes if node.id != 0]
        if not customer_ids:
            return [0, 0]

        unvisited = set(customer_ids)
        route = [0]
        current = 0

        while unvisited:
            nearest_candidates = sorted(
                list(unvisited),
                key=lambda node_id: self.env.truck_dist_matrix[current][node_id]
            )

            candidate_count = min(max(1, k), len(nearest_candidates))
            candidate_subset = nearest_candidates[:candidate_count]

            # RCL Mantığı ile K içerisinden rastgele seçim
            costs = [self.env.truck_dist_matrix[current][n] for n in candidate_subset]
            min_cost = min(costs)
            max_cost = max(costs)

            alpha = 0.3
            threshold = min_cost + alpha * (max_cost - min_cost)

            rcl = [
                n for n in candidate_subset
                if self.env.truck_dist_matrix[current][n] <= threshold
            ]
            if not rcl:
                rcl = candidate_subset

            chosen = random.choice(rcl)
            route.append(chosen)
            unvisited.remove(chosen)
            current = chosen

        route.append(0)
        return route

    def _insertion_heuristic_tour(self, k=1):
        customer_ids = [node.id for node in self.env.nodes if node.id != 0]
        if not customer_ids:
            return [0, 0]

        unvisited = set(customer_ids)
        first = random.choice(list(unvisited))
        route = [0, first, 0]
        unvisited.remove(first)

        while unvisited:
            candidates = []
            for customer in unvisited:
                for pos in range(len(route) - 1):
                    a = route[pos]
                    b = route[pos + 1]

                    # IC = d_iv + d_vj - d_ij
                    insertion_cost = (
                        self.env.truck_dist_matrix[a][customer]
                        + self.env.truck_dist_matrix[customer][b]
                        - self.env.truck_dist_matrix[a][b]
                    )
                    candidates.append((insertion_cost, customer, pos + 1))

            candidates.sort(key=lambda x: x[0])
            candidate_count = min(max(1, k), len(candidates))
            candidate_subset = candidates[:candidate_count]

            costs = [c[0] for c in candidate_subset]
            min_cost = min(costs)
            max_cost = max(costs)

            alpha = 0.3
            threshold = min_cost + alpha * (max_cost - min_cost)

            rcl = [c for c in candidate_subset if c[0] <= threshold]
            if not rcl:
                rcl = candidate_subset

            _, chosen_customer, insert_pos = random.choice(rcl)

            route.insert(insert_pos, chosen_customer)
            unvisited.remove(chosen_customer)

        return route

    def _apply_split_procedure(self, tsp_tour):
        solution = self._truck_only_solution(tsp_tour)
        candidate_list = self._generate_ranked_candidates(solution.truck_route)

        for _, launch, drone_node, rendezvous in candidate_list:
            if drone_node not in solution.truck_route:
                continue

            temp_solution = solution.copy()
            temp_solution.drone_deliveries.append((launch, drone_node, rendezvous))
            temp_solution.truck_route.remove(drone_node)

            if not self._is_solution_feasible(temp_solution):
                continue

            temp_solution.total_cost = self._calculate_total_cost(temp_solution)
            temp_solution.total_time = self._calculate_truck_only_time(temp_solution.truck_route)

            if temp_solution.total_cost < solution.total_cost:
                solution = temp_solution

        return solution

    def _generate_ranked_candidates(self, route):
        candidates = []

        for idx in range(1, len(route) - 1):
            drone_node = route[idx]
            node_obj = self.env.nodes[drone_node]

            if getattr(node_obj, 'is_drone_eligible', True) == False:
                continue

            prev_node = route[idx - 1]
            next_node = route[idx + 1]

            truck_saving = (
                self.env.truck_dist_matrix[prev_node][drone_node]
                + self.env.truck_dist_matrix[drone_node][next_node]
                - self.env.truck_dist_matrix[prev_node][next_node]
            ) * self.env.C1

            for launch_pos in range(0, idx):
                for rendezvous_pos in range(idx + 1, len(route)):
                    launch = route[launch_pos]
                    rendezvous = route[rendezvous_pos]

                    d1 = self.env.drone_dist_matrix[launch][drone_node]
                    d2 = self.env.drone_dist_matrix[drone_node][rendezvous]
                    drone_distance = d1 + d2

                    drone_time = (drone_distance / self.env.drone_speed) * 60.0
                    if drone_time > self.env.drone_endurance:
                        continue

                    temp_route = route.copy()
                    temp_route.remove(drone_node)

                    if launch not in temp_route or rendezvous not in temp_route:
                        continue

                    truck_time = self._truck_path_time(temp_route, launch, rendezvous)
                    
                    # DÜZELTME 1: Matematiksel Modele Uygun Bekleme Maliyeti Hesabı
                    waiting_cost = 0.0
                    if truck_time < drone_time:
                        waiting_cost = (drone_time - truck_time) * self.env.alpha # Kamyon bekliyor
                    elif drone_time < truck_time:
                        waiting_cost = (truck_time - drone_time) * self.env.beta  # Dron bekliyor

                    drone_cost = drone_distance * self.env.C2
                    
                    # Delta Cost = Drone Cost + Waiting Cost - Truck Saving
                    delta = drone_cost + waiting_cost - truck_saving
                    candidates.append((delta, launch, drone_node, rendezvous))

        # En faydalı (negatif) atamalar ilk sırada
        candidates.sort(key=lambda x: x[0])
        return candidates

    def _truck_path_distance(self, route, start_node, end_node):
        positions = {node: idx for idx, node in enumerate(route)}

        if start_node not in positions or end_node not in positions:
            return float("inf")

        start_pos = positions[start_node]
        end_pos = positions[end_node]

        if start_pos >= end_pos:
            return float("inf")

        total = 0.0
        for i in range(start_pos, end_pos):
            a = route[i]
            b = route[i + 1]
            total += self.env.truck_dist_matrix[a][b]

        return total

    def _truck_path_time(self, route, start_node, end_node):
        distance = self._truck_path_distance(route, start_node, end_node)
        if distance == float("inf"):
            return float("inf")
        return (distance / self.env.truck_speed) * 60.0

    def _is_solution_feasible(self, solution):
        route = solution.truck_route
        positions = {node: idx for idx, node in enumerate(route)}

        used_drone_nodes = set()
        intervals = []

        for launch, drone_node, rendezvous in solution.drone_deliveries:
            if drone_node in used_drone_nodes:
                return False
            used_drone_nodes.add(drone_node)

            if drone_node in route:
                return False

            if launch not in positions or rendezvous not in positions:
                return False

            if positions[launch] >= positions[rendezvous]:
                return False

            d1 = self.env.drone_dist_matrix[launch][drone_node]
            d2 = self.env.drone_dist_matrix[drone_node][rendezvous]
            drone_time = ((d1 + d2) / self.env.drone_speed) * 60.0
            
            if drone_time > self.env.drone_endurance:
                return False

            intervals.append((positions[launch], positions[rendezvous]))

        # Non-overlapping drone deliveries kısıtı
        intervals.sort()
        for i in range(len(intervals) - 1):
            _, current_end = intervals[i]
            next_start, _ = intervals[i + 1]

            if next_start < current_end:
                return False

        return True

    def _calculate_truck_only_cost(self, route):
        total_cost = 0.0
        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]
            total_cost += self.env.truck_dist_matrix[a][b] * self.env.C1
        return total_cost

    def _calculate_truck_only_time(self, route):
        total_time = 0.0
        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]
            distance = self.env.truck_dist_matrix[a][b]
            total_time += (distance / self.env.truck_speed) * 60.0
        return total_time

    def _calculate_total_cost(self, solution):
        total_cost = self._calculate_truck_only_cost(solution.truck_route)

        for launch, drone_node, rendezvous in solution.drone_deliveries:
            d1 = self.env.drone_dist_matrix[launch][drone_node]
            d2 = self.env.drone_dist_matrix[drone_node][rendezvous]
            drone_distance = d1 + d2

            drone_time = (drone_distance / self.env.drone_speed) * 60.0
            truck_time = self._truck_path_time(solution.truck_route, launch, rendezvous)

            # DÜZELTME 2: Genel Maliyet Fonksiyonunda Bekleme Cezası Düzenlemesi
            waiting_cost = 0.0
            if truck_time < drone_time:
                waiting_cost = (drone_time - truck_time) * self.env.alpha
            elif drone_time < truck_time:
                waiting_cost = (truck_time - drone_time) * self.env.beta

            drone_cost = drone_distance * self.env.C2
            total_cost += drone_cost + waiting_cost

        return total_cost

    def _local_search(self, solution):
        # Akış şeması (Flowchart) hiyerarşisine tam uyumlu Guided Local Search
        current = solution.copy()
        improved = True

        while improved:
            improved = False

            # 1. Drone Relocation Operator
            better_drone_reloc = self._drone_relocation_operator(current)
            if better_drone_reloc.total_cost < current.total_cost:
                current = better_drone_reloc
                improved = True
                continue

            # 2. Relocation Operator (Kamyon düğümü yer değiştirme)
            better_reloc = self._relocation_operator(current)
            if better_reloc.total_cost < current.total_cost:
                current = better_reloc
                improved = True
                continue

            # 3. Two-Exchange Operator (Sadece 10 yakın komşu ile kısıtlı)
            better_swap = self._truck_swap_operator(current)
            if better_swap.total_cost < current.total_cost:
                current = better_swap
                improved = True
                continue

            # 4. Drone Removal Operator
            better_drone_remove = self._drone_removal_operator(current)
            if better_drone_remove.total_cost < current.total_cost:
                current = better_drone_remove
                improved = True
                # Akış şemasında son adım olduğu için continue yazmasak da olur ama tutarlılık için:
                continue

        return current

    # ---------------- OPERATÖRLER ---------------- #

    def _drone_relocation_operator(self, solution):
        best = solution.copy()
        route = solution.truck_route

        for delivery_index, (old_launch, drone_node, old_rendezvous) in enumerate(solution.drone_deliveries):
            for i in range(len(route) - 1):
                for j in range(i + 1, len(route)):
                    new_launch = route[i]
                    new_rendezvous = route[j]

                    if new_launch == old_launch and new_rendezvous == old_rendezvous:
                        continue

                    candidate = solution.copy()
                    candidate.drone_deliveries[delivery_index] = (new_launch, drone_node, new_rendezvous)

                    if not self._is_solution_feasible(candidate):
                        continue

                    candidate.total_cost = self._calculate_total_cost(candidate)
                    if candidate.total_cost < best.total_cost:
                        candidate.total_time = self._calculate_truck_only_time(candidate.truck_route)
                        return candidate # İlk bulduğu iyileştirmede döner (First-improvement)

        return best

    def _relocation_operator(self, solution):
        # Bir kamyon durağını rotadaki başka bir pozisyona taşır
        best = solution.copy()
        route = solution.truck_route

        for i in range(1, len(route) - 1): # Depo hariç hareket edecek düğüm
            for j in range(1, len(route)): # Yeni yerleşim noktası
                if i == j or i == j - 1:
                    continue

                node_to_move = route[i]
                new_route = route.copy()
                new_route.pop(i)
                
                insert_idx = j if j < i else j - 1
                new_route.insert(insert_idx, node_to_move)

                candidate = solution.copy()
                candidate.truck_route = new_route

                if not self._is_solution_feasible(candidate):
                    continue

                candidate.total_cost = self._calculate_total_cost(candidate)
                if candidate.total_cost < best.total_cost:
                    candidate.total_time = self._calculate_truck_only_time(candidate.truck_route)
                    return candidate

        return best

    def _truck_swap_operator(self, solution):
        # DÜZELTME 3: Karmaşıklığı önlemek için "Sadece 10 En Yakın Komşu" Kısıtı
        best = solution.copy()
        route = solution.truck_route

        for i in range(1, len(route) - 1):
            node_i = route[i]
            
            # i düğümünün, şu anki rotada olan düğümler arasından en yakın komşularını bul
            valid_targets = [n for n in route[1:-1] if n != node_i]
            valid_targets.sort(key=lambda n: self.env.truck_dist_matrix[node_i][n])
            nearest_10 = valid_targets[:10]

            for node_j in nearest_10:
                j = route.index(node_j)
                if i >= j: # Çift hesaplamayı önle
                    continue

                new_route = route.copy()
                new_route[i], new_route[j] = new_route[j], new_route[i]

                candidate = solution.copy()
                candidate.truck_route = new_route

                if not self._is_solution_feasible(candidate):
                    continue

                candidate.total_cost = self._calculate_total_cost(candidate)
                if candidate.total_cost < best.total_cost:
                    candidate.total_time = self._calculate_truck_only_time(candidate.truck_route)
                    return candidate

        return best

    def _drone_removal_operator(self, solution):
        # Dron ile atanan bir teslimatı iptal edip, kamyon rotasına tekrar dahil eder
        best = solution.copy()

        for delivery_index, (launch, drone_node, rendezvous) in enumerate(solution.drone_deliveries):
            for k_idx in range(1, len(solution.truck_route)):
                candidate = solution.copy()
                candidate.drone_deliveries.pop(delivery_index)

                new_route = candidate.truck_route.copy()
                new_route.insert(k_idx, drone_node)
                candidate.truck_route = new_route

                if not self._is_solution_feasible(candidate):
                    continue

                candidate.total_cost = self._calculate_total_cost(candidate)
                if candidate.total_cost < best.total_cost:
                    candidate.total_time = self._calculate_truck_only_time(candidate.truck_route)
                    return candidate

        return best