from src.spatial_data_mapper import SpatialDataMapper

def main():
    # Build a real-world network for London
    london_network = SpatialDataMapper.from_place("Camden, London, UK")
    print(f"Network built with {london_network.get_stats()} elements.")
    london_network.visualize()
    # breakpoint()
    path_distance = london_network.get_path_distance(source_node=list(london_network.NetGraph.nodes)[0],
                                                    target_node=list(london_network.NetGraph.nodes)[-1])
    print(f"Sample path distance: {path_distance} metres.")

if __name__ == "__main__":
    main()