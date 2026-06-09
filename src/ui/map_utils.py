import math
import requests
import plotly.graph_objects as go
import streamlit as st

# --- COORDINATE CONVERSION FOR REAL WORLD MAP ---
CENTER_LAT = 40.990  # Kadikoy, Istanbul (Latitude)
CENTER_LON = 29.020  # Kadikoy, Istanbul (Longitude)


def get_osrm_route(coords):
    """
    Fetches the real street-routing path from OSRM API.
    coords: List of (lat, lon) tuples.
    """
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    
    headers = {
        "User-Agent": "TSPD-Optimization-App/1.0 (Student Project)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("code") == "Ok":
            route_geometry = data["routes"][0]["geometry"]["coordinates"]
            return [(lat, lon) for lon, lat in route_geometry]
        else:
            st.warning("OSRM API isteği reddetti. Yollar yerine düz çizgi çiziliyor.")
            return coords
    except Exception as e:
        st.warning(f"OSRM Bağlantı Hatası: {e}. Düz çizgi çiziliyor.")
        return coords

def create_plotly_map(env, solution):
    """Generates the Abstract Grid map using Plotly."""
    fig = go.Figure()

    if env.nodes:
        xs = [n.x for n in env.nodes[1:]]
        ys = [n.y for n in env.nodes[1:]]
        texts = [f"Customer ID: {n.id}<br>Drone Eligible: {n.is_drone_eligible}" for n in env.nodes[1:]]
        
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode='markers',
            marker=dict(size=10, color='#3498db', line=dict(width=1, color='DarkSlateGrey')),
            text=texts, hoverinfo='text', name='Customers'
        ))

        depot = env.nodes[0]
        fig.add_trace(go.Scatter(
            x=[depot.x], y=[depot.y], mode='markers',
            marker=dict(size=16, color='orange', symbol='square'),
            text=["Depot (0,0)"], hoverinfo='text', name='Depot'
        ))

    if solution and solution.truck_route:
        node_dict = {n.id: n for n in env.nodes}
        truck_x = [node_dict[node_id].x for node_id in solution.truck_route if node_id in node_dict]
        truck_y = [node_dict[node_id].y for node_id in solution.truck_route if node_id in node_dict]
        fig.add_trace(go.Scatter(x=truck_x, y=truck_y, mode='lines', line=dict(color='black', width=2), name='Truck Route', opacity=0.7))

    if solution and solution.drone_deliveries:
        for i, (launch, target, rendezvous) in enumerate(solution.drone_deliveries):
            show_legend = True if i == 0 else False
            node_dict = {n.id: n for n in env.nodes}
            dx = [node_dict[launch].x, node_dict[target].x, node_dict[rendezvous].x]
            dy = [node_dict[launch].y, node_dict[target].y, node_dict[rendezvous].y]
            fig.add_trace(go.Scatter(x=dx, y=dy, mode='lines', line=dict(color='#e74c3c', width=2, dash='dash'), name='Drone Flight', showlegend=show_legend))

    fig.update_layout(
        title="TSP-D Delivery Network", xaxis_title="X Coordinate (km)", yaxis_title="Y Coordinate (km)",
        template="plotly_white", height=600, margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig