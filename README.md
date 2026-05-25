🚁 A GRASP Heuristic for the Min-Cost Traveling Salesman Problem with Drone

Overview

This project presents a GRASP-based heuristic framework for solving the Min-Cost Traveling Salesman Problem with Drone (TSP-D).

The implementation is based on the research paper:

A GRASP Heuristic for the Min-Cost Traveling Salesman Problem with Drone

The objective is to minimize total transportation cost by coordinating a delivery truck and an unmanned aerial vehicle (drone) within a hybrid delivery system.

The project combines:

* heuristic optimization
* truck-drone synchronization
* local search improvement procedures
* benchmark experimentation
* parameter sensitivity analysis
* convergence and runtime evaluation

⸻

📌 Problem Definition

The Traveling Salesman Problem with Drone (TSP-D) extends the classical Traveling Salesman Problem by allowing drones to assist truck deliveries.

In this problem:

* the truck follows a primary delivery route
* drones may temporarily depart from the truck
* complete eligible deliveries independently
* rendezvous with the truck later

The optimization objective is:

* minimizing total operational cost
* maintaining feasible drone endurance constraints
* improving last-mile delivery efficiency

⸻

🧠 Implemented Methodology

The project follows the heuristic methodology proposed in the reference paper.

Main Heuristic

* GRASP (Greedy Randomized Adaptive Search Procedure)

Core Optimization Components

* Split Procedure
* Feasibility Checking
* Cost Evaluation
* Truck–Drone Synchronization

Local Search Operators

* Truck Relocation Operator
* Truck Swap Operator
* Drone Relocation Operator
* Drone Removal Operator

⸻

📊 Experimental Analysis

The project includes multiple experimental analysis modules for evaluating optimization performance and heuristic behavior.

Benchmark Evaluation

Comparison between:

* truck-only baseline
* GRASP-based TSP-D solution

Convergence Analysis

Tracks solution quality improvement across iterations.

Parameter Tuning

Evaluates:

* different iteration counts
* different k_max values

Runtime Scaling

Analyzes computational performance across:

* n10 datasets
* n50 datasets
* n100 datasets

Heatmap Analysis

Visualizes parameter sensitivity across optimization configurations.

Simulated Annealing Comparison

Additional heuristic comparison between:

* GRASP
* Simulated Annealing

Parallel Benchmark Execution

Uses multiprocessing to accelerate large-scale benchmark experiments.

⸻

🏗️ Project Architecture

TSP_DRONE_PROJECT/
│
├── data/
│   ├── singlecenter/
│   ├── doublecenter/
│   ├── restricted/
│   └── uniform/
│
├── experiments/
│   ├── advanced_analysis.py
│   ├── convergence_analysis.py
│   ├── heatmap_analysis.py
│   ├── parallel_benchmark.py
│   ├── parameter_tuning.py
│   ├── sa_comparison.py
│   └── singlecenter_benchmark.py
│
├── results/
│   ├── csv/
│   └── figures/
│
├── src/
│   ├── data_core.py
│   ├── optimizer.py
│   ├── demo_app.py
│   └── ui/
│
├── requirements.txt
└── README.md

⸻

⚙️ Core System Components

data_core.py

Responsible for:

* dataset parsing
* node management
* drone eligibility handling
* distance matrix calculation
* route visualization support

⸻

optimizer.py

Contains:

* GRASP heuristic implementation
* split procedure
* local search operators
* feasibility constraints
* cost calculations
* truck-drone coordination logic

⸻

experiments/

Contains experimental evaluation modules.

singlecenter_benchmark.py

Runs benchmark comparison between:

* truck-only baseline
* GRASP-based TSP-D solution

advanced_analysis.py

Performs:

* average improvement analysis
* runtime scaling analysis

convergence_analysis.py

Analyzes:

* convergence behavior of GRASP
* iteration-based cost improvement

parameter_tuning.py

Tests:

* multiple iteration counts
* multiple k_max configurations

heatmap_analysis.py

Visualizes:

* parameter sensitivity
* cost distribution across configurations

sa_comparison.py

Compares:

* GRASP
* Simulated Annealing

parallel_benchmark.py

Executes benchmark instances using multiprocessing.

⸻

📂 Dataset Structure

Benchmark datasets are located under:

data/
├── singlecenter/
├── doublecenter/
├── restricted/
└── uniform/

Main experiments were conducted using:

* 3 × n10 instances
* 3 × n50 instances
* 3 × n100 instances

from the singlecenter benchmark dataset.

⸻

🔄 Optimization Workflow

The framework follows the pipeline below:

Dataset Loading
        ↓
Initial GRASP Construction
        ↓
Split Procedure
        ↓
Truck–Drone Coordination
        ↓
Local Search Improvement
        ↓
Cost Optimization
        ↓
Benchmark Evaluation
        ↓
Experimental Analysis

⸻

🚀 Installation

Clone Repository

git clone https://github.com/BerrkeUnal/TSP_DRONE_PROJECT.git
cd TSP_DRONE_PROJECT

⸻

Create Virtual Environment

python3 -m venv .venv
source .venv/bin/activate

⸻

Install Dependencies

pip3 install -r requirements.txt

⸻

▶️ Running Experiments

Main Benchmark

python3 -m experiments.singlecenter_benchmark

⸻

Advanced Analysis

python3 -m experiments.advanced_analysis

⸻

Convergence Analysis

python3 -m experiments.convergence_analysis

⸻

Parameter Tuning

python3 -m experiments.parameter_tuning

⸻

Heatmap Analysis

python3 -m experiments.heatmap_analysis

⸻

Simulated Annealing Comparison

python3 -m experiments.sa_comparison

⸻

Parallel Benchmark Execution

python3 -m experiments.parallel_benchmark

⸻

📈 Experimental Findings

Experimental results demonstrate that the GRASP-based TSP-D framework consistently improves transportation cost compared to truck-only baseline solutions.

Observed findings include:

* strong improvements on n50 benchmark datasets
* scalable runtime behavior for n100 instances
* stable convergence performance
* effective parameter sensitivity behavior

⸻

📊 Generated Outputs

Generated CSV files are stored in:

results/csv/

Generated figures are stored in:

results/figures/

Outputs include:

* benchmark comparison tables
* convergence plots
* runtime scaling graphs
* parameter tuning results
* heatmaps
* heuristic comparison results

⸻

🛠️ Technologies Used

* Python 3
* Pandas
* Matplotlib
* Multiprocessing
* Streamlit
* Plotly
* Folium

⸻

🔮 Future Improvements

Possible future extensions include:

* Tabu Search
* Genetic Algorithms
* Multi-drone routing
* Dynamic delivery requests
* Real-time optimization environments

⸻

👥 Contributors

Industrial Engineering Team

* optimization modeling
* benchmark planning
* experimental evaluation

Software Engineering Team

* heuristic implementation
* benchmark automation
* visualization systems
* experimental analysis tools

⸻

📌 Conclusion

This project demonstrates that integrating drone-assisted delivery into routing optimization can significantly reduce transportation costs while maintaining feasible operational constraints.

The implemented GRASP-based framework successfully combines:

* heuristic optimization
* truck-drone coordination
* local search improvement
* benchmark experimentation
* parameter tuning
* convergence analysis

within a scalable and modular optimization environme