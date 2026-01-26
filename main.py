import os
from src.spatial_data_mapper import SpatialDataMapper
from src.network_generator import LogisticsNetwork

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
    nyc_network.visualize()
    # breakpoint()
    path_distance = nyc_network.get_path_distance(source_node=list(nyc_network.NetGraph.nodes)[0],
                                                    target_node=list(nyc_network.NetGraph.nodes)[-1])
    print(f"Sample path distance: {path_distance} metres.")

if __name__ == "__main__":
    main()