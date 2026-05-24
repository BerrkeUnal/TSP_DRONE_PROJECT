import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver
from src.ui.map_utils import create_plotly_map
from src.ui.analytics import render_benchmark, render_export, render_timeline

def main():
    # --- UI Configuration ---
    st.set_page_config(page_title="TSP-D Optimizer", page_icon="🚁", layout="wide")
    st.title("🚁 TSP-D: Grid Logistics Dashboard")
    st.markdown("Optimization of Last-Mile Delivery using Truck & Drone Synchronization (Abstract Grid View)")

    # --- SESSION STATE ---
    if 'optimized' not in st.session_state:
        st.session_state.optimized = False
        st.session_state.env = None
        st.session_state.best_solution = None
        st.session_state.baseline_solution = None
        st.session_state.solver_stats = None

    # --- Minimalist Sidebar (Sadece gerekli olanlar) ---
    st.sidebar.header("⚙️ Optimization Settings")
    
    # Sadece hocanın veri setini yüklemek için alan ve iterasyon sayısı bıraktık
    uploaded_file = st.sidebar.file_uploader("Upload Dataset (.txt)", type=['txt'])
    
    run_button = st.sidebar.button("🚀 Run Optimization", use_container_width=True)

    # Perform calculation when the button is pressed
    if run_button:
        if uploaded_file is None:
            st.error("⚠️ Please upload the dataset (.txt) provided by your professor to run the simulation.")
            st.stop()
            
        with st.spinner("Initializing Environment & Computing Routes..."):
            env = TSPEnvironment()
            
            # Veriyi dosyadan oku
            env.load_from_streamlit_file(uploaded_file)
            
            # Makalenin varsayılan sabit parametrelerini doğrudan arka planda tanımlıyoruz
            env.alpha = 10.0  # Truck waiting penalty (Paper default)
            env.beta = 10.0   # Drone waiting penalty (Paper default)
            env.C1 = 25.0     # Truck unit cost
            env.C2 = 1.0      # Drone unit cost

            solver = GRASPSolver(environment=env, max_iterations=2000)
            best_sol = solver.solve()
            base_sol = solver.baseline_solution 

            # Memory allocation
            st.session_state.env = env
            st.session_state.best_solution = best_sol
            st.session_state.baseline_solution = base_sol
            st.session_state.solver_stats = {
                "iter_hist": solver.iteration_history,
                "cost_hist": solver.best_cost_history
            }
            st.session_state.optimized = True

    # --- VISUALIZATION ---
    if st.session_state.optimized:
        env = st.session_state.env
        best_solution = st.session_state.best_solution
        baseline_sol = st.session_state.baseline_solution

        # --- PERFORMANCE SUMMARY ---
        st.markdown("### 📊 Performance Analysis")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        cost_savings = ((baseline_sol.total_cost - best_solution.total_cost) / baseline_sol.total_cost) * 100
        
        col_m1.metric("Baseline Cost", f"${baseline_sol.total_cost:.2f}")
        col_m2.metric("Optimized Cost", f"${best_solution.total_cost:.2f}", f"-{cost_savings:.1f}%")
        col_m3.metric("Truck Stops", len(best_solution.truck_route) - 2)
        col_m4.metric("Drone Sorties", len(best_solution.drone_deliveries))

        st.divider()

        # --- COMPARATIVE GRID MAP VIEW ---
        st.markdown("### 🗺️ Abstract Grid Route Comparison")
        map_col1, map_col2 = st.columns(2)

        with map_col1:
            st.subheader("制造业 / Standard Truck (TSP)")
            # Sadece Plotly grid haritasını çizdiriyoruz
            st.plotly_chart(create_plotly_map(env, baseline_sol), use_container_width=True)

        with map_col2:
            st.subheader("🚁 Optimized Truck-Drone (TSP-D)")
            # Sadece Plotly grid haritasını çizdiriyoruz
            st.plotly_chart(create_plotly_map(env, best_solution), use_container_width=True)

        # --- TABLE: COMPARISON SUITABLE FOR THE ARTICLE ---
        st.markdown("### 📊 Performance Comparison in Article Standards")

        cost_savings = ((baseline_sol.total_cost - best_solution.total_cost) / baseline_sol.total_cost) * 100
        time_savings = ((baseline_sol.total_time - best_solution.total_time) / baseline_sol.total_time) * 100

        comparison_data = {
            "Metric": [
                "Total Operational Cost ($)", 
                "Total Time (min)", 
                "Number of Customers Visited by Truck", 
                "Number of Customers Visited by Drone"
            ],
            "Truck Only (Traditional TSP)": [
                f"{baseline_sol.total_cost:.2f}", 
                f"{baseline_sol.total_time:.2f}", 
                f"{len(baseline_sol.truck_route) - 2}", 
                "0"
            ],
            "Truck + Drone (TSP-D)": [
                f"{best_solution.total_cost:.2f}", 
                f"{best_solution.total_time:.2f}", 
                f"{len(best_solution.truck_route) - 2}", 
                f"{len(best_solution.drone_deliveries)}"
            ], 
            "Improvement / Difference": [
                f"{cost_savings:.1f}% Savings",
                f"{time_savings:.1f}% Faster",
                "-",
                "-"
            ]
        }

        df_comparison = pd.DataFrame(comparison_data).set_index("Metric")
        st.table(df_comparison)

        st.divider()

        # --- SUB-ANALYTICAL PANEL (Sadece Akademik Sekmeler Kaldı) ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📉 Convergence Chart", 
            "⏱️ Time Analysis",
            "📥 Data Export",
            "📉 Sensitivity Analysis: Battery vs. Cost"
        ])
        
        with tab1:
            stats = st.session_state.solver_stats
            if stats["iter_hist"]:
                chart_data = pd.DataFrame({
                    "Iteration": stats["iter_hist"],
                    "Best Cost": stats["cost_hist"]
                })
                st.line_chart(chart_data, x="Iteration", y="Best Cost")
        
        with tab2:
            st.markdown("### ⏱️ Logistics Synchronization Timeline")
            render_timeline(env, best_solution)
            render_benchmark(best_solution, baseline_sol)
        
        with tab3:
            render_export(best_solution)

        with tab4:
            st.subheader("📉 Sensitivity Analysis: Battery vs. Cost")
            if st.button("Analyze Impact of Battery Life"):
                results = []
                for test_endurance in [10, 20, 30, 40, 50, 60]:
                    env.drone_endurance = test_endurance
                    temp_solver = GRASPSolver(env, max_iterations=20) 
                    sol = temp_solver.solve()
                    results.append({"Battery": test_endurance, "Cost": sol.total_cost})
                
                sensitivity_df = pd.DataFrame(results)
                st.line_chart(sensitivity_df, x="Battery", y="Cost")
                st.info("As battery life increases, the drone can fly to more distant customers, which reduces the overall cost.")    

    else:
        st.info("👈 Please upload the professor's dataset and click 'Run Optimization' to start.")

if __name__ == "__main__":
    main()