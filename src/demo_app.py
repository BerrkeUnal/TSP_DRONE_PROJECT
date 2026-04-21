import streamlit as st
import pandas as pd
import sys
import os
from streamlit_folium import st_folium

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_core import TSPEnvironment
from src.optimizer import GRASPSolver
from src.ui.sidebar_utils import render_sidebar
from src.ui.map_utils import create_plotly_map, create_folium_map
from src.ui.analytics import render_benchmark, render_export, render_timeline, get_vehicle_locations_at_time

def main():
    # --- UI Configuration ---
    st.set_page_config(page_title="TSP-D Pro Optimizer", page_icon="🚁", layout="wide")
    st.title("🚁 TSP-D: Integrated Logistics Dashboard")
    st.markdown("Optimization of Last-Mile Delivery using Truck & Drone Synchronization")

    # ---  (SESSION STATE)  ---
    if 'optimized' not in st.session_state:
        st.session_state.optimized = False
        st.session_state.env = None
        st.session_state.best_solution = None
        st.session_state.baseline_solution = None
        st.session_state.solver_stats = None

    # --- Sidebar Parameters ---
    params = render_sidebar()
    run_button = st.sidebar.button("🚀 Run Optimization", use_container_width=True)

    # Perform the calculation and save it to memory when the button is pressed.
    if run_button:
        with st.spinner("Initializing Environment & Computing Routes..."):
            env = TSPEnvironment()
            
            if params.get("uploaded_file") is not None:
                env.load_from_csv(params["uploaded_file"])
            else:
                env.generate_random_instance(params["num_customers"], params["area_size"])
            
            env.truck_speed = params["truck_speed"]
            env.drone_speed = params["drone_speed"]
            env.drone_endurance = params["drone_endurance"]
            env.alpha = params["alpha"]
            env.beta = params["beta"]
            env.calculate_distance_matrices()

            solver = GRASPSolver(environment=env, max_iterations=params["max_iter"])
            best_sol = solver.solve()
            base_sol = solver.baseline_solution 

            # Let's write the data to memory.
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
        col_m3.metric("Truck Stops", len(best_solution.truck_route))
        col_m4.metric("Drone Sorties", len(best_solution.drone_deliveries))

        st.divider()

        # --- COMPARATIVE MAP VIEW ---
        st.markdown("### 🗺️ Route Comparison")
        map_col1, map_col2 = st.columns(2)

        with map_col1:
            st.subheader("🚛 Standard Truck (TSP)")
            if params["map_view"] == "Real World (Folium)":
                m_base = create_folium_map(env, baseline_sol, show_radius=False)
                st_folium(m_base, height=450, width=None, key="map_base", returned_objects=[])
            else:
                st.plotly_chart(create_plotly_map(env, baseline_sol), use_container_width=True)

        with map_col2:
            st.subheader("🚁 Optimized Truck-Drone (TSP-D)")
            if params["map_view"] == "Real World (Folium)":
                m_opt = create_folium_map(env, best_solution, show_radius=params.get("show_radius", False))
                # returned_objects=[] ve unique key sayesinde beyaz ekran hatası çözüldü
                st_folium(m_opt, height=450, width=None, key="map_opt", returned_objects=[])
            else:
                st.plotly_chart(create_plotly_map(env, best_solution), use_container_width=True)

        st.divider()

        # --- SUB-ANALYTICAL PANEL ---
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📉 Convergence Chart", 
                                                        "⏱️ Time Analysis",
                                                        "📥 Data Export",
                                                        "📉 Sensitivity Analysis: Battery vs. Cost",
                                                        "🎬 Mission Playback Simulator",
                                                        "🌿 Carbon Savings"])
        
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
            st.caption("This graphic shows the simultaneous movements of the truck and the drone..")
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
                st.info("As battery life increases, the drone can fly to more distant customers, which reduces the overall cost..")    

        with tab5: # Simulation Tab
                    st.subheader("🎬 Mission Playback Simulator")
                    
                    # Setup the slider
                    max_t = int(best_solution.total_time) + 1
                    sim_time = st.slider("Select Operation Minute", 0, max_t, 0, key="sim_slider")
                    
                    # Get positions from our new logic
                    from src.ui.map_utils import km_to_latlon # Ensure this is imported
                    
                    t_pos, d_pos, t_stat, d_stat = get_vehicle_locations_at_time(env, best_solution, sim_time)
                    t_lat, t_lon = km_to_latlon(t_pos[0], t_pos[1])
                    d_lat, d_lon = km_to_latlon(d_pos[0], d_pos[1])

                    # Status Cards
                    col_s1, col_s2 = st.columns(2)
                    col_s1.info(f"🚛 **Truck Status:** {t_stat}")
                    col_s2.error(f"🚁 **Drone Status:** {d_stat}")

                    # Create a dynamic simulation map
                    import folium
                    sim_map = folium.Map(location=[t_lat, t_lon], zoom_start=14)
                    
                    # Draw original route for reference (faded)
                    # (Optional: Add static routes here with lower opacity)

                    # Add Truck Marker
                    folium.Marker(
                        [t_lat, t_lon], 
                        tooltip="Truck Current Position",
                        icon=folium.Icon(color="black", icon="truck", prefix="fa")
                    ).add_to(sim_map)

                    # Add Drone Marker
                    folium.Marker(
                        [d_lat, d_lon], 
                        tooltip="Drone Current Position",
                        icon=folium.Icon(color="red", icon="plane", prefix="fa")
                    ).add_to(sim_map)

                    st_folium(sim_map, height=500, width=None, key="sim_map_display", returned_objects=[])

        with tab6: # Sustainability (Carbon Savings)
                    st.subheader("🌿 Environmental Impact Report")
                    from src.ui.analytics import render_sustainability_report
                    # Passing current env, the TSP-D solution, and the Truck-only baseline
                    render_sustainability_report(env, best_solution, baseline_sol)

    else:
        st.info("👈 Configure parameters and click 'Run Optimization' to start.")

if __name__ == "__main__":
    main()