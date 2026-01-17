from src.spatial_data_mapper import SpatialDataMapper

def main():
    # Build a real-world network for London
    london_network = SpatialDataMapper.from_place("Camden, London, UK")
    print(f"Network built with {london_network.get_stats()} elements.")
    london_network.visualize()

if __name__ == "__main__":
    main()