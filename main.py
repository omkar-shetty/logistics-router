import os
from src.spatial_data_mapper import SpatialDataMapper
from src.network_generator import LogisticsNetwork
from src.vehicle_router import Vehicle
from src.logger import get_logger
from sklearn.cluster import KMeans

logger = get_logger(__name__)

DATA_PATH = "data/brooklyn_net.json"
HUB_NODE = 42469596  # must be a valid node ID in the graph
RUN_TYPE = 'multi' #option to select between single ('single') and multiple ('multi') vehicle runs
VEHICLE_CAPACITY = 150
VEHICLE_COUNT = 3

def main():
    if os.path.exists(DATA_PATH):
        logger.info("Loading network from cache...")
        nyc_network = LogisticsNetwork.load_from_json(DATA_PATH)
    else:
        nyc_network = SpatialDataMapper.from_place("Brooklyn, NYC, NY, USA", center_point=(40.7033, -73.9894)) #Centre around DUMBO, NYC
        os.makedirs("data", exist_ok=True)
        nyc_network.save_to_json(DATA_PATH)
    logger.info(f"Network built with {nyc_network.get_stats()} elements.")

    start = list(nyc_network.NetGraph.nodes)[0]
    end = list(nyc_network.NetGraph.nodes)[-1]

    # A: Clear Roads
    nyc_network.simulate_traffic(intensity=1.0)
    time_clear = nyc_network.get_path_distance(start, end)

    # B: Rush Hour
    nyc_network.simulate_traffic(intensity=2.5)
    time_rush = nyc_network.get_path_distance(start, end)

    logger.info(f"Midnight Run: {time_clear:.1f} mins")
    logger.info(f"Rush Hour: {time_rush:.1f} mins")
    logger.info(f"Traffic Delay: {time_rush - time_clear:.1f} mins")

    #Convert to dataframes
    node_df, edge_df = nyc_network.convert_to_dataframes()

    urgent_cust_df = node_df.loc[node_df['urgency']>=1].copy()
    urgent_nodes = urgent_cust_df['node_id'].tolist()
    cust_coords = urgent_cust_df[['x','y']]
    logger.info(f'High Urgency Nodes: {urgent_nodes}')

    if RUN_TYPE == 'single':
        # Single Vehicle Path Calculation
        vehicle1 = Vehicle(vehicle_id=1, start_node=HUB_NODE, capacity=VEHICLE_CAPACITY)
        vehicle1.generate_greedy_path(urgent_nodes, nyc_network)
        logger.info('****** Greedy Path Computed ******')
        logger.info(f'Travel path: {vehicle1.route_history}')
        logger.info(f'Travel time: {vehicle1.travel_time}')
    elif RUN_TYPE == 'multi':
        # Multi Vehicle Path Calculation
        vehicle_count = VEHICLE_COUNT
        kmeans = KMeans(n_clusters=vehicle_count,
                        init='k-means++',
                        random_state=42).fit(cust_coords)
        urgent_cust_df['cluster'] = kmeans.labels_

        fleet = [Vehicle(vehicle_id=i, start_node=HUB_NODE, capacity=VEHICLE_CAPACITY) for i in range(vehicle_count)]

        for i, vehicle in enumerate(fleet):
            node_list = urgent_cust_df.loc[urgent_cust_df['cluster']==i, 'node_id']
            vehicle.generate_greedy_path(node_list, nyc_network)

            logger.info(f'Vehicle: {vehicle.vehicle_id}')
            logger.info(f'Travel path: {vehicle.route_history}')
            logger.info(f'Travel time: {vehicle.travel_time}')

        print_fleet_summary(fleet, urgent_nodes)

        os.makedirs("results", exist_ok=True)
        fleet_colors = ['#e74c3c', '#2ecc71', '#f1c40f']  # red, green, yellow per vehicle
        nyc_network.save_street_visualization(
            "results/brooklyn_street_network.png",
            route=[(v.route_history, fleet_colors[i % len(fleet_colors)]) for i, v in enumerate(fleet)]
        )
        nyc_network.visualize(save_path="results/fleet_dispatch_schematic.png")


def print_fleet_summary(fleet, urgent_nodes):
    """Prints a summary of the fleet performance to console."""
    total_travel_time = sum(v.travel_time for v in fleet)
    total_skipped = sum(len(v.skipped_nodes) for v in fleet)
    total_urgent = len(urgent_nodes)
    stops_served = total_urgent - total_skipped

    print("\n=== Fleet Summary ===")
    print(f"Vehicles deployed: {len(fleet)}")
    print(f"Total fleet travel time: {total_travel_time:.1f} mins")
    print(f"Stops served: {stops_served}/{total_urgent}")
    for vehicle in fleet:
        stops_visited = len(vehicle.route_history) - 1
        print(f"  V{vehicle.vehicle_id}: {stops_visited} stops, "
              f"{vehicle.travel_time:.1f} mins, load={vehicle.carried_load:.2f}")


if __name__ == "__main__":
    main()