import os
from src.spatial_data_mapper import SpatialDataMapper
from src.network_generator import LogisticsNetwork
from src.vehicle_router import Vehicle

DATA_PATH = "data/brooklyn_net.json"

def main():
    if os.path.exists(DATA_PATH):
        print("Loading network from cache...")
        nyc_network = LogisticsNetwork.load_from_json(DATA_PATH)
    else:
        nyc_network = SpatialDataMapper.from_place("Brooklyn, NYC, NY, USA")
        os.makedirs("data", exist_ok=True)
        nyc_network.save_to_json(DATA_PATH)
    print(f"Network built with {nyc_network.get_stats()} elements.")
    # nyc_network.visualize()
    
    start = list(nyc_network.NetGraph.nodes)[0]
    end = list(nyc_network.NetGraph.nodes)[-1]

    # A: Clear Roads
    nyc_network.simulate_traffic(intensity=1.0)
    time_clear = nyc_network.get_path_distance(start, end)

    # B: Rush Hour
    nyc_network.simulate_traffic(intensity=2.5)
    time_rush = nyc_network.get_path_distance(start, end)

    print(f"Midnight Run: {time_clear:.1f} mins")
    print(f"Rush Hour: {time_rush:.1f} mins")
    print(f"Traffic Delay: {time_rush - time_clear:.1f} mins")

    #Convert to dataframes
    node_df, edge_df = nyc_network.convert_to_dataframes()

    urgent_nodes = node_df.loc[node_df['urgency']>=1,'node_id']
    print(f'High Urgency Nodes:{urgent_nodes}')
    vehicle1 = Vehicle(vehicle_id=1, start_node=42490789)
    vehicle1.generate_greedy_path(urgent_nodes, nyc_network)
    print('****** Greedy Path Computed ******')
    print(f'Travel path: {vehicle1.route_history}')
    print(f'Travel time: {vehicle1.travel_time}')

if __name__ == "__main__":
    main()