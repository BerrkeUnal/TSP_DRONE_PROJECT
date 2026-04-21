import streamlit as st

def render_sidebar():
    st.sidebar.header("🛠️ Optimization Settings")
    
    # 1. GROUP: SCRIPT SETTINGS
    with st.sidebar.expander("🌐 Scenario Parameters", expanded=True):
        num_customers = st.slider("Number of Customers", 5, 50, 20)
        area_size = st.slider("Area Size (km²)", 100, 2500, 400)
        max_iter = st.number_input("Max Iterations", 10, 1000, 100)

    # 2. GROUP: VEHICLE AND COST SPECIFICATIONS
    with st.sidebar.expander("🚛 Vehicle & Costs", expanded=False):
        truck_speed = st.slider("Truck Speed (km/h)", 20, 80, 40)
        drone_speed = st.slider("Drone Speed (km/h)", 30, 100, 60)
        drone_endurance = st.slider("Drone Battery (mins)", 10, 60, 20)
        st.markdown("---")
        alpha = st.slider("Truck Wait Penalty (α)", 0.0, 20.0, 0.0)
        beta = st.slider("Drone Wait Penalty (β)", 0.0, 20.0, 0.0)

    # 3. GROUP: VISUALIZATION AND FILE PROCESSING
    with st.sidebar.expander("📊 UI & Data Settings", expanded=True):
        map_view = st.selectbox("Map Type", ["Real World (Folium)", "Abstract Grid (Plotly)"])
        show_radius = st.checkbox("⭕ Show Drone Range Circles", value=False)
        
        st.markdown("---")
        # CSV Import
        uploaded_file = st.file_uploader("Upload Customer CSV", type=["csv", "xlsx"])

    return {
        "num_customers": num_customers,
        "area_size": area_size,
        "truck_speed": truck_speed,
        "drone_speed": drone_speed,
        "drone_endurance": drone_endurance,
        "alpha": alpha,
        "beta": beta,
        "max_iter": max_iter,
        "map_view": map_view,
        "show_radius": show_radius,
        "uploaded_file": uploaded_file
    }