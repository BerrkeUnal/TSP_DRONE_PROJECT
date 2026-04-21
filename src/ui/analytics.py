import streamlit as st
import pandas as pd
import plotly.express as px

def render_benchmark(best_solution, baseline_solution):
    """
    Renders the Benchmark Analysis section comparing actual TSP and TSP-D results.
    """
    st.markdown("### 📊 Benchmark Analysis")
    
    # Extract real data from the solution objects
    tsp_cost = baseline_solution.total_cost
    tspd_cost = best_solution.total_cost
    
    tsp_time = baseline_solution.total_time
    tspd_time = best_solution.total_time
    
    # Calculate actual percentage savings
    cost_savings_pct = ((tsp_cost - tspd_cost) / tsp_cost * 100) if tsp_cost > 0 else 0
    time_savings_pct = ((tsp_time - tspd_time) / tsp_time * 100) if tsp_time > 0 else 0
    
    col_bench1, col_bench2 = st.columns(2)
    
    with col_bench1:
        st.info("🚚 Traditional TSP (Truck Only)")
        st.metric("Total Operational Cost", f"${tsp_cost:.2f}")
        st.metric("Total Delivery Time", f"{tsp_time:.1f} mins")
        
    with col_bench2:
        st.success("🚁 TSP-D (Truck + Drone)")
        # Show actual cost delta
        st.metric("Total Operational Cost", f"${tspd_cost:.2f}", f"-{cost_savings_pct:.1f}% (Saved)")
        # Show actual time delta
        st.metric("Total Delivery Time", f"{tspd_time:.1f} mins", f"-{time_savings_pct:.1f}% (Saved)")

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
    
    # Ana indirme butonu
    csv_data = df_report.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Route Report (CSV)",
        data=csv_data,
        file_name='tsp_drone_route.csv',
        mime='text/csv',
        use_container_width=True
    )

    # Önizleme tablosu
    with st.expander("👁️ View Route Data (Preview)"):
        st.info("Showing the first 15 steps of the route.")
        st.dataframe(df_report.head(15), use_container_width=True)


def render_timeline(env, solution):
    """It calculates the operating times of trucks and drones and plots a Gantt chart."""
    data = []
    
    # 1. TRUCK ROUTE TIME CALCULATION
    if solution and solution.truck_route:
        current_time = 0.0
        route = solution.truck_route
        for i in range(len(route) - 1):
            start_node = route[i]
            end_node = route[i + 1]
            
            dist = env.truck_dist_matrix[start_node][end_node]
            travel_time = (dist / env.truck_speed) * 60.0
            
            data.append({
                "Task": "🚛 Truck",
                "Start": current_time,
                "Duration": travel_time,
                "Resource": "Truck Travel",
                "Details": f"Node {start_node} -> {end_node}"
            })
            current_time += travel_time

    # 2. DRONE DELIVERY TIME ESTIMATION
    if solution and solution.drone_deliveries:
        for launch, target, rendezvous in solution.drone_deliveries:
            launch_idx = solution.truck_route.index(launch)
            launch_time = 0
            for i in range(launch_idx):
                d = env.truck_dist_matrix[solution.truck_route[i]][solution.truck_route[i+1]]
                launch_time += (d / env.truck_speed) * 60.0
                
            
            d1 = env.drone_dist_matrix[launch][target]
            d2 = env.drone_dist_matrix[target][rendezvous]
            flight_time = ((d1 + d2) / env.drone_speed) * 60.0
            
            data.append({
                "Task": "🚁 Drone",
                "Start": launch_time,
                "Duration": flight_time, 
                "Resource": "Drone Flight",
                "Details": f"Delivery to Customer {target}"
            })

    if not data:
        st.warning("Time data could not be calculated..")
        return

    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x="Duration",     
        y="Task",          
        base="Start",     
        orientation='h',   
        color="Resource", 
        hover_data=["Details"],
        title="Operation Timeline (Synchronization Analysis)",
        labels={"Task": "Vehicle", "Duration": "Duration (min)", "Start": "Start Time"},
        color_discrete_map={"Truck Travel": "#2c3e50", "Drone Flight": "#e74c3c"}
    )
    
    fig.update_layout(
        height=350, 
        showlegend=True,
        xaxis_title="Time Elapsed (Minutes)",
        yaxis_title="",
        barmode='group' # Çubukların üst üste binmemesi için
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    st.plotly_chart(fig, use_container_width=True)


def render_sustainability_report(env, solution, baseline_solution):
    """
    Calculates CO2 emissions comparison between Truck-Only and Truck-Drone scenarios.
    """
    st.markdown("### 🌿 Sustainability & Green Logistics Report")
    
    # Constants: Grams of CO2 per KM
    CO2_TRUCK_KM = 160.0 
    CO2_DRONE_KM = 10.0
    
    # 1. Calculate Baseline (Truck-Only) total distance
    base_dist = 0
    b_route = baseline_solution.truck_route
    for i in range(len(b_route)-1):
        # Use the distance matrix from env
        base_dist += env.truck_dist_matrix[b_route[i]][b_route[i+1]]
    
    baseline_emissions = (base_dist * CO2_TRUCK_KM) / 1000 # Convert to kg
    
    # 2. Calculate Optimized (Truck + Drone) total distance
    opt_truck_dist = 0
    for i in range(len(solution.truck_route)-1):
        opt_truck_dist += env.truck_dist_matrix[solution.truck_route[i]][solution.truck_route[i+1]]
        
    opt_drone_dist = 0
    for launch, target, rendezvous in solution.drone_deliveries:
        # Sum both flight legs: Launch -> Target -> Rendezvous
        opt_drone_dist += env.drone_dist_matrix[launch][target] + env.drone_dist_matrix[target][rendezvous]
        
    optimized_emissions = ((opt_truck_dist * CO2_TRUCK_KM) + (opt_drone_dist * CO2_DRONE_KM)) / 1000 # kg
    
    # 3. Final Comparison Calculations
    saved_co2 = baseline_emissions - optimized_emissions
    reduction_pct = (saved_co2 / baseline_emissions) * 100 if baseline_emissions > 0 else 0
    trees_saved = saved_co2 / 20.0 # Each tree absorbs ~20kg CO2/year

    # Display Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("CO2 Baseline", f"{baseline_emissions:.2f} kg")
    m2.metric("CO2 Optimized", f"{optimized_emissions:.2f} kg", f"-{reduction_pct:.1f}%")
    m3.metric("Trees Equivalent", f"{trees_saved:.2f} Trees")

    st.success(f"🌱 Carbon Impact: By using drones, you are preventing **{saved_co2:.2f} kg** of CO2 emissions!")

def get_vehicle_locations_at_time(env, solution, target_min):
    """
    Calculates the (lat, lon) positions of truck and drone at a specific minute.
    """
    # Initialize positions at Depot
    depot_node = env.nodes[0]
    truck_pos = (depot_node.x, depot_node.y)
    drone_pos = (depot_node.x, depot_node.y)
    truck_status = "At Depot"
    drone_status = "On Truck"

    # 1. TRUCK POSITION CALCULATION
    current_time = 0.0
    for i in range(len(solution.truck_route) - 1):
        u = solution.truck_route[i]
        v = solution.truck_route[i+1]
        dist = env.truck_dist_matrix[u][v]
        travel_time = (dist / env.truck_speed) * 60.0
        
        if current_time <= target_min <= current_time + travel_time:
            # Interpolate position between node u and v
            ratio = (target_min - current_time) / travel_time
            curr_x = env.nodes[u].x + (env.nodes[v].x - env.nodes[u].x) * ratio
            curr_y = env.nodes[u].y + (env.nodes[v].y - env.nodes[u].y) * ratio
            truck_pos = (curr_x, curr_y)
            truck_status = f"Moving to Node {v}"
            break
        elif target_min > current_time + travel_time:
            truck_pos = (env.nodes[v].x, env.nodes[v].y)
            truck_status = f"Arrived at Node {v}"
        
        current_time += travel_time

    # 2. DRONE POSITION CALCULATION
    for launch, target, rendezvous in solution.drone_deliveries:
        # Calculate when drone launches
        launch_idx = solution.truck_route.index(launch)
        l_time = 0
        for i in range(launch_idx):
            l_time += (env.truck_dist_matrix[solution.truck_route[i]][solution.truck_route[i+1]] / env.truck_speed) * 60.0
        
        d1 = env.drone_dist_matrix[launch][target]
        d2 = env.drone_dist_matrix[target][rendezvous]
        t1 = (d1 / env.drone_speed) * 60.0
        t2 = (d2 / env.drone_speed) * 60.0
        
        if l_time <= target_min <= l_time + t1:
            ratio = (target_min - l_time) / t1
            dx = env.nodes[launch].x + (env.nodes[target].x - env.nodes[launch].x) * ratio
            dy = env.nodes[launch].y + (env.nodes[target].y - env.nodes[launch].y) * ratio
            drone_pos = (dx, dy)
            drone_status = f"Flying to Customer {target}"
        elif l_time + t1 < target_min <= l_time + t1 + t2:
            ratio = (target_min - (l_time + t1)) / t2
            dx = env.nodes[target].x + (env.nodes[rendezvous].x - env.nodes[target].x) * ratio
            dy = env.nodes[target].y + (env.nodes[rendezvous].y - env.nodes[target].y) * ratio
            drone_pos = (dx, dy)
            drone_status = "Returning to Truck"
        elif target_min < l_time:
            # Drone is still on truck
            drone_pos = truck_pos
            drone_status = "On Truck"

    return truck_pos, drone_pos, truck_status, drone_status