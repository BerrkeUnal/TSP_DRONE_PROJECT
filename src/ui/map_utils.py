import math
import folium
import requests
import plotly.graph_objects as go
import streamlit as st

# --- COORDINATE CONVERSION FOR REAL WORLD MAP ---
CENTER_LAT = 40.990  # Kadikoy, Istanbul (Latitude)
CENTER_LON = 29.020  # Kadikoy, Istanbul (Longitude)

def km_to_latlon(x_km, y_km, center_lat=CENTER_LAT, center_lon=CENTER_LON):
    """
    Converts internal abstract Grid (X, Y in km) to Real World GPS Coordinates (Lat, Lon).
    """
    lat = center_lat + (y_km / 111.0)
    lon = center_lon + (x_km / (111.0 * math.cos(math.radians(center_lat))))
    return lat, lon

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

def create_folium_map(env, solution, show_radius=False):
    """Generates the Real World map using Folium and OSRM for Truck routes."""
    max_x = max([n.x for n in env.nodes]) if env.nodes else 10
    max_y = max([n.y for n in env.nodes]) if env.nodes else 10
    mid_lat, mid_lon = km_to_latlon(max_x / 2, max_y / 2)
    
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=13, tiles="OpenStreetMap")
    node_coords = {}
    
    # 1. Plot Customers
    for node in env.nodes[1:]:
        lat, lon = km_to_latlon(node.x, node.y)
        node_coords[node.id] = (lat, lon)
        color = 'blue' if node.is_drone_eligible else 'purple'
        folium.CircleMarker(
            location=[lat, lon], radius=6,
            popup=f"Customer {node.id}<br>Drone Eligible: {node.is_drone_eligible}",
            color=color, fill=True, fill_opacity=0.9
        ).add_to(m)
        
    # 2. Plot Depot
    if env.nodes:
        depot = env.nodes[0]
        lat, lon = km_to_latlon(depot.x, depot.y)
        node_coords[depot.id] = (lat, lon)
        folium.Marker(
            location=[lat, lon], popup="Depot",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

    # DİKKAT: ESKİ DEPO ÇEMBERİNİ BURADAN SİLDİK!

    # 3. Plot Truck Route (REAL STREETS using OSRM)
    if solution and solution.truck_route:
        truck_waypoints = [node_coords[n_id] for n_id in solution.truck_route if n_id in node_coords]
        
        if len(truck_waypoints) > 1:
            real_street_path = get_osrm_route(truck_waypoints)
            folium.PolyLine(
                real_street_path, 
                color="#2c3e50", 
                weight=5, 
                opacity=0.9, 
                tooltip="Truck Route (Real Streets)"
            ).add_to(m)

    # 4. Plot Drone Deliveries & YENİ ÇEMBERLER
    if solution and solution.drone_deliveries:
        # Menzili (yarıçapı) metre cinsinden 1 kere hesaplıyoruz
        max_flight_radius_meters = ((env.drone_speed / 60.0) * env.drone_endurance / 2.0) * 1000
        
        for launch, target, rendezvous in solution.drone_deliveries:
            drone_path = [node_coords[launch], node_coords[target], node_coords[rendezvous]]
            
            # Uçuş çizgisi
            folium.PolyLine(
                drone_path, 
                color="#e74c3c", 
                weight=3, 
                opacity=0.9, 
                dash_array="8, 8", 
                tooltip="Drone Flight (Air Path)"
            ).add_to(m)
            
            # YENİ VE DOĞRU: Çemberi uçağın kalktığı (Launch) noktaya çiz!
            if show_radius:
                launch_lat, launch_lon = node_coords[launch]
                folium.Circle(
                    location=[launch_lat, launch_lon],
                    radius=max_flight_radius_meters,
                    color="#e74c3c",
                    fill=True,
                    fill_color="#e74c3c",
                    fill_opacity=0.08,  # Üst üste binince çok koyu olmasın diye şeffaf tuttuk
                    tooltip=f"Kalkış {launch} için Operasyon Menzili",
                    weight=1
                ).add_to(m)
            
    return m

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
            marker=dict(size=16, color='#e74c3c', symbol='square'),
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