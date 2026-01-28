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

if __name__ == "__main__":
    main()