🚁 TSP-D Pro: Integrated Truck-Drone Logistics Optimizer
TSP-D Pro is a high-performance Decision Support System (DSS) designed to solve the Traveling Salesman Problem with Drone (TSP-D). It optimizes last-mile delivery operations by synchronizing a conventional delivery truck with an unmanned aerial vehicle (drone) to minimize total operational costs and time.

📌 Key Features
Advanced Optimization Engine: Utilizes the GRASP (Greedy Randomized Adaptive Search Procedure) algorithm to find high-quality solutions for complex routing scenarios.

Interactive Dashboard: A modern UI built with Streamlit for real-time parameter tuning and result visualization.

Geospatial Visualization: Integration with Folium and Plotly for real-world map rendering and abstract grid analysis.

Mission Playback Simulator: Interactive "Play" feature to visualize the step-by-step delivery process over time.

Sustainability Analytics: Automated calculation of CO 
2
​	
  savings and environmental impact (Tree-equivalent) compared to traditional logistics.

Sensitivity Analysis: Built-in "What-If" tools to analyze the impact of drone battery life on total costs.

Data Management: Support for custom CSV data imports and detailed mission report exports.

🏗️ Technical Architecture
The project is built on a modular Python architecture:

data_core.py: Manages spatial data, distance matrices (Manhattan for trucks, Euclidean for drones), and Node structures.

optimizer.py: Contains the GRASP metaheuristic logic, local search improvements, and cost calculation engines.

analytics.py: Handles synchronization logic for Gantt charts, carbon footprint modeling, and simulation time-stepping.

map_utils.py: Manages Folium map generation, custom markers, and route drawing.

🚀 Getting Started
Prerequisites

Python 3.9+

Virtual Environment (Recommended)

Installation

Clone the repository:

Bash
git clone https://github.com/yourusername/tsp-drone-optimizer.git
cd tsp-drone-optimizer
Install dependencies:

Bash
pip install -r requirements.txt
Running the Application

Launch the interactive dashboard:

Bash
streamlit run src/demo_app.py
📊 Analytics & Insights
⏱️ Time Synchronization

The system generates a Gantt Chart to visualize the parallel operations of the truck and drone. This highlights the "waiting times" and "simultaneous delivery" windows that lead to efficiency gains.

🌿 Green Logistics

By utilizing electric drones for short-distance "eligible" deliveries, the system calculates the reduction in diesel emissions.

Truck Emission: ~160g CO 
2
​	
  / km

Drone Emission: ~10g CO 
2
​	
  / km

📉 Sensitivity Study

Users can test various drone hardware specifications (e.g., flight endurance) to determine the Return on Investment (ROI) for upgrading drone fleets.

📂 File Structure
Plaintext
├── src/
│   ├── demo_app.py          # Main Streamlit Application
│   ├── optimizer.py         # GRASP Solver Logic
│   ├── data_core.py         # Data Structures & Environment
│   └── ui/                  # UI Components (Maps, Analytics, Sidebar)
├── requirements.txt         # Project Dependencies
├── .gitignore               # Version Control Exclusions
└── README.md                # Project Documentation