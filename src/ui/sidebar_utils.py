import streamlit as st

def render_sidebar():
    """
    Renders all sidebar controls and returns a dictionary of parameters.
    """
    st.sidebar.header("⚙️ Network Setup")
    num_customers = st.sidebar.slider("Number of Customers", 10, 100, 50, 10)
    area_size = st.sidebar.selectbox("Area Size (km²)", [100, 500, 1000], index=0)
    
    st.sidebar.header("🗺️ Display Options")
    map_view = st.sidebar.radio("Map Style", ["Abstract Grid (Plotly)", "Real World (Folium)"])
    
    st.sidebar.header("🚁 Vehicle Parameters")
    truck_speed = st.sidebar.slider("Truck Speed (km/h)", 20.0, 80.0, 40.0, 5.0)
    drone_speed = st.sidebar.slider("Drone Speed (km/h)", 20.0, 80.0, 40.0, 5.0)
    drone_endurance = st.sidebar.slider("Drone Battery (mins)", 10.0, 60.0, 20.0, 5.0)
    
    st.sidebar.header("⏳ Cost & Penalties")
    alpha = st.sidebar.number_input("Truck Wait Penalty (α)", value=10.0, step=1.0)
    beta = st.sidebar.number_input("Drone Wait Penalty (β)", value=10.0, step=1.0)

    st.sidebar.header("🔄 Algorithm Rules")
    max_iter = st.sidebar.number_input("Max Iterations", 1, 5000, 100)
    
    # Return all parameters as a dictionary
    return {
        "num_customers": num_customers,
        "area_size": area_size,
        "map_view": map_view,
        "truck_speed": truck_speed,
        "drone_speed": drone_speed,
        "drone_endurance": drone_endurance,
        "alpha": alpha,
        "beta": beta,
        "max_iter": max_iter
    }