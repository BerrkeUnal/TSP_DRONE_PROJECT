import streamlit as st
import time
import sys
import os

from streamlit_folium import st_folium

# Ensure the app can find the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver

# Import our custom UI modules
from src.ui.sidebar_utils import render_sidebar
from src.ui.map_utils import create_plotly_map, create_folium_map
from src.ui.analytics import render_benchmark, render_export

def main():
    # --- UI Configuration ---
    st.set_page_config(page_title="TSP-D Optimizer", page_icon="🚁", layout="wide")
    st.title("🚁 Traveling Salesman Problem with Drone")
    st.markdown("Interactive Dashboard for Min-Cost TSP-D Operations")

    # --- Sidebar Parameters ---
    params = render_sidebar()
    run_button = st.sidebar.button("🚀 Run Optimization", use_container_width=True)

    # --- Main Logic ---
    if run_button:
        with st.spinner("Applying parameters and building environment..."):
            env = TSPEnvironment()
            
            # Apply dynamic parameters
            env.truck_speed = params["truck_speed"]
            env.drone_speed = params["drone_speed"]
            env.drone_endurance = params["drone_endurance"]
            env.alpha = params["alpha"]
            env.beta = params["beta"]
            
            env.generate_random_instance(params["num_customers"], params["area_size"])
            env.calculate_distance_matrices()
        
        # --- UI Animation ---
        st.markdown("### ⚙️ Optimization Progress")
        progress_bar = st.progress(0)
        log_box = st.empty() 
        
        for i in range(1, 11):
            progress_bar.progress(i * 10)
            log_box.info(f"Running GRASP Iterations... {i * 10}% completed.")
            time.sleep(0.1) 
        log_box.success("Optimization finished! Rendering results...")
        time.sleep(0.5)
        log_box.empty()
        progress_bar.empty()

        # --- Run Backend Solver ---
        solver = GRASPSolver(environment=env, max_iterations=params["max_iter"])
        best_solution = solver.solve()
        
        # --- UI Modules Execution ---
        
        # 1. Benchmark Analytics
        render_benchmark(best_solution)

        # 2. Map Visualization
        st.markdown("### 🗺️ Delivery Routes Visualization")
        if params["map_view"] == "Real World (Folium)":
            st.info("📍 Displaying operations over Kadıköy, Istanbul based on exact km distances.")
            m = create_folium_map(env, best_solution)
            st_folium(m, height=500, use_container_width=True, returned_objects=[])
        else:
            map_fig = create_plotly_map(env, best_solution)
            st.plotly_chart(map_fig, use_container_width=True)
        
        # 3. Export Analytics
        render_export(best_solution)

    else:
        st.info("👈 Please configure the parameters on the sidebar and click 'Run Optimization' to start.")

if __name__ == "__main__":
    main()