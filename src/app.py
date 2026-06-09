import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver
from src.ui.map_utils import create_plotly_map

def main():
    # --- UI Configuration ---
    st.set_page_config(page_title="TSP-D Optimizer", page_icon="🚁", layout="wide")
    st.title("🚁 TSP-D: Grid Logistics Dashboard")
    st.markdown("Optimization of Last-Mile Delivery using Truck & Drone Synchronization (Abstract Grid View)")

    # --- SESSION STATE ---
    if 'optimized' not in st.session_state:
        st.session_state.optimized = False
        st.session_state.results = []

    # --- Minimalist Sidebar ---
    st.sidebar.header("⚙️ Optimization Settings")
    
    # Allows uploading multiple benchmark files simultaneously (e.g., n10, n50, n100)
    uploaded_files = st.sidebar.file_uploader(
        "Upload Datasets (.txt)", 
        type=['txt'], 
        accept_multiple_files=True
    )
    
    run_button = st.sidebar.button("🚀 Run Optimization", use_container_width=True)

    # Perform calculation when the button is pressed
    if run_button:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one dataset (.txt) provided by your professor.")
            st.stop()
            
        results_list = []
        
        for file in uploaded_files:
            with st.spinner(f"Optimizing {file.name} ... Please wait."):
                env = TSPEnvironment()
                env.load_from_streamlit_file(file)
                
                # Paper Default Parameters
                env.alpha = 10.0  
                env.beta = 10.0   
                env.C1 = 25.0     
                env.C2 = 1.0      

                env.drone_speed = 2.0 
                env.drone_endurance = 10000.0

                
                solver = GRASPSolver(environment=env, max_iterations=50)
                best_sol = solver.solve()
                base_sol = solver.baseline_solution 
                
                # Performance metrics
                num_customers = len(env.nodes) - 1
                cost_savings = ((base_sol.total_cost - best_sol.total_cost) / base_sol.total_cost) * 100
                time_savings = ((base_sol.total_time - best_sol.total_time) / base_sol.total_time) * 100
                
                results_list.append({
                    "Dataset": file.name,
                    "Customers": num_customers,
                    "Base Cost ($)": round(base_sol.total_cost, 2),
                    "TSP-D Cost ($)": round(best_sol.total_cost, 2),
                    "Cost Savings": f"{cost_savings:.1f}%",
                    "Base Time (min)": round(base_sol.total_time, 2),
                    "TSP-D Time (min)": round(best_sol.total_time, 2),
                    "Time Savings": f"{time_savings:.1f}%",
                    "Drone Sorties": len(best_sol.drone_deliveries),
                    "env": env,
                    "best_sol": best_sol,
                    "base_sol": base_sol
                })
        
        st.session_state.results = results_list
        st.session_state.optimized = True

    # --- VISUALIZATION ---
    if st.session_state.optimized:
        results = st.session_state.results
        
        st.markdown("### 📊 Performance Benchmarks (Categorized by Scale)")
        st.caption("Results are grouped dynamically to match Table 3 (n=10), Table 4 (n=50), and Table 5 (n=100) of Ha et al. (2018).")
        
        # Convert all results to a master DataFrame for filtering
        df_master = pd.DataFrame(results)
        
        # 1. TABLE FOR 10 CUSTOMERS
        df_10 = df_master[df_master["Customers"] <= 15] # Safe boundary for 10-node instances
        if not df_10.empty:
            st.markdown("#### 📍 Small Scale Instances (Table 3 Standards - 10 Customers)")
            st.table(df_10.drop(columns=['env', 'best_sol', 'base_sol', 'Customers']).set_index("Dataset"))
            
        # 2. TABLE FOR 50 CUSTOMERS
        df_50 = df_master[(df_master["Customers"] > 15) & (df_master["Customers"] <= 60)]
        if not df_50.empty:
            st.markdown("#### 📍 Medium Scale Instances (Table 4 Standards - 50 Customers)")
            st.table(df_50.drop(columns=['env', 'best_sol', 'base_sol', 'Customers']).set_index("Dataset"))
            
        # 3. TABLE FOR 100 CUSTOMERS
        df_100 = df_master[df_master["Customers"] > 60]
        if not df_100.empty:
            st.markdown("#### 📍 Large Scale Instances (Table 5 Standards - 100 Customers)")
            st.table(df_100.drop(columns=['env', 'best_sol', 'base_sol', 'Customers']).set_index("Dataset"))

        st.divider()

        # --- ROUTE MAPS (Tabbed View for Clean Layout) ---
        st.markdown("### 🗺️ Route Maps by Dataset")
        tabs = st.tabs([res["Dataset"] for res in results])
        
        for i, tab in enumerate(tabs):
            with tab:
                res = results[i]
                map_col1, map_col2 = st.columns(2)

                with map_col1:
                    st.subheader(f"Standard Truck (TSP) - {res['Customers']} Customers")
                    st.plotly_chart(create_plotly_map(res['env'], res['base_sol']), use_container_width=True)

                with map_col2:
                    st.subheader(f"Optimized Truck-Drone (TSP-D) - {res['Customers']} Customers")
                    st.plotly_chart(create_plotly_map(res['env'], res['best_sol']), use_container_width=True)

                # --- YENİ EKLENEN KARŞILAŞTIRMA GRAFİĞİ BURADA ---
                st.divider()
                st.markdown("### 📈 Algorithm Comparison Chart")
                
                chart_df = pd.DataFrame({
                    "Total Cost ($)": [res['base_sol'].total_cost, res['best_sol'].total_cost],
                }, index=["Traditional TSP (Baseline)", "GRASP TSP-D (Your Algorithm)"])
                
                st.bar_chart(chart_df, color="#2ecc71")
                st.info(f"💡 For the {res['Dataset']} dataset, our GRASP algorithm successfully reduced the total cost by {res['Cost Savings']} compared to the traditional baseline.")

if __name__ == "__main__":
    main()