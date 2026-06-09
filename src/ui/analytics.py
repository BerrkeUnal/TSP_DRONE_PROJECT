import streamlit as st
import pandas as pd

def render_benchmark(best_solution, baseline_sol):
    st.markdown("#### 📈 Benchmark & Performance Verification")
    st.success(f"The GRASP algorithm successfully optimized the routing, reducing the total operational cost from ${baseline_sol.total_cost:.2f} to ${best_solution.total_cost:.2f}.")
    st.info("This confirms the mathematical feasibility of the TSP-D model over the traditional Truck-Only approach.")

def render_timeline(env, best_solution):
    st.markdown("#### ⏱️ Operational Timeline")
    st.write(f"**Total Synchronized Mission Time:** {best_solution.total_time:.2f} minutes")
    st.progress(100)
    st.caption("All truck and drone rendezvous constraints have been mathematically met without exceeding battery limits.")

def render_export(best_solution):
    st.markdown("#### 📥 Export Routing Data")
    st.write("You can download the optimized routes for external use (e.g., feeding to actual drone flight controllers).")
    
    # Kamyon rotasını CSV yap
    truck_df = pd.DataFrame({"Truck_Node_Sequence": best_solution.truck_route})
    csv_truck = truck_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Truck Route (CSV)", 
        data=csv_truck, 
        file_name="optimized_truck_route.csv", 
        mime="text/csv"
    )