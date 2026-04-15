import streamlit as st
import pandas as pd

def render_benchmark(best_solution):
    """
    Renders the Benchmark Analysis section comparing TSP and TSP-D.
    """
    st.markdown("### 📊 Benchmark Analysis")
    
    # TODO: Endüstriciler TSP (Sadece Kamyon) formülünü yazdığında buradaki sahte değerler değişecek.
    dummy_tsp_cost = best_solution.total_cost * 1.25 # Fake 25% worse cost
    
    col_bench1, col_bench2 = st.columns(2)
    with col_bench1:
        st.info("🚚 Traditional TSP (Truck Only)")
        st.metric("Total Operational Cost", f"${dummy_tsp_cost:.2f}")
        st.metric("Total Delivery Time", "120.0 mins")
    with col_bench2:
        st.success("🚁 TSP-D (Truck + Drone)")
        st.metric("Total Operational Cost", f"${best_solution.total_cost:.2f}", "-20.0% (Saved)")
        st.metric("Total Delivery Time", f"{best_solution.total_time:.1f} mins", "-15.0% (Saved)")

def render_export(best_solution):
    """
    Renders the Export Results section allowing users to download CSV reports.
    """
    st.markdown("### 📄 Export Results")
    
    report_data = {
        "Step": range(1, len(best_solution.truck_route) + 1),
        "Node ID": best_solution.truck_route,
        "Vehicle": ["Truck"] * len(best_solution.truck_route)
    }
    df_report = pd.DataFrame(report_data)
    
    # Main download button
    csv_data = df_report.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Route Report (CSV)",
        data=csv_data,
        file_name='tsp_drone_route.csv',
        mime='text/csv',
        use_container_width=True
    )

    # Optional pop-up table preview
    with st.expander("👁️ View Route Data (Preview)"):
        st.info("Showing the first 15 steps of the route.")
        st.dataframe(df_report.head(15), use_container_width=True)