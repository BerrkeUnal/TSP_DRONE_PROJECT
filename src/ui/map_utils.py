import math
import folium
import plotly.graph_objects as go

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

def create_folium_map(env, solution):
    """Generates the Real World map using Folium."""
    max_x = max([n.x for n in env.nodes]) if env.nodes else 10
    max_y = max([n.y for n in env.nodes]) if env.nodes else 10
    mid_lat, mid_lon = km_to_latlon(max_x / 2, max_y / 2)
    
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=13, tiles="CartoDB positron")
    node_coords = {}
    
    for node in env.nodes[1:]:
        lat, lon = km_to_latlon(node.x, node.y)
        node_coords[node.id] = (lat, lon)
        color = 'blue' if node.is_drone_eligible else 'purple'
        folium.CircleMarker(
            location=[lat, lon], radius=5,
            popup=f"Customer {node.id}<br>Drone Eligible: {node.is_drone_eligible}",
            color=color, fill=True, fill_opacity=0.7
        ).add_to(m)
        
    if env.nodes:
        depot = env.nodes[0]
        lat, lon = km_to_latlon(depot.x, depot.y)
        node_coords[depot.id] = (lat, lon)
        folium.Marker(
            location=[lat, lon], popup="Depot",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

    # TODO: Gerçek rota formülleri geldiğinde çalışacak
    if solution and solution.truck_route:
        truck_path = [node_coords[n_id] for n_id in solution.truck_route if n_id in node_coords]
        folium.PolyLine(truck_path, color="black", weight=3, opacity=0.8, tooltip="Truck Route").add_to(m)

    # TODO: Gerçek drone uçuş formülleri geldiğinde çalışacak
    if solution and solution.drone_deliveries:
        for launch, target, rendezvous in solution.drone_deliveries:
            drone_path = [node_coords[launch], node_coords[target], node_coords[rendezvous]]
            folium.PolyLine(drone_path, color="red", weight=2, opacity=0.8, dash_array="5, 5", tooltip="Drone Flight").add_to(m)
            
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

    # TODO: Backend'den gerçek rota geldiğinde siyah çizgi düzgün oluşacak.
    if solution and solution.truck_route:
        node_dict = {n.id: n for n in env.nodes}
        truck_x = [node_dict[node_id].x for node_id in solution.truck_route if node_id in node_dict]
        truck_y = [node_dict[node_id].y for node_id in solution.truck_route if node_id in node_dict]
        fig.add_trace(go.Scatter(x=truck_x, y=truck_y, mode='lines', line=dict(color='black', width=2), name='Truck Route', opacity=0.7))

    # TODO: Drone atamaları yapıldığında kırmızı kesik çizgiler eklenecek.
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