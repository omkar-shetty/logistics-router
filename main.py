import os
from src.network.spatial_data_mapper import SpatialDataMapper
from src.network.network_generator import LogisticsNetwork
from src.solvers.greedy_solver import GreedySolver
from src.solvers.or_solver import ORSolver
from src.logger import get_logger

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

    # Clear Roads
    nyc_network.simulate_traffic(intensity=1.0)
    time_clear = nyc_network.get_path_distance(start, end)

    # Rush Hour
    nyc_network.simulate_traffic(intensity=2.5)
    time_rush = nyc_network.get_path_distance(start, end)

    logger.info(f"Midnight Run: {time_clear:.1f} mins")
    logger.info(f"Rush Hour: {time_rush:.1f} mins")
    logger.info(f"Traffic Delay: {time_rush - time_clear:.1f} mins")

    #Convert to dataframes
    node_df, _ = nyc_network.convert_to_dataframes()

    urgent_cust_df = node_df.loc[node_df['urgency']>=1].copy()
    urgent_nodes = urgent_cust_df['node_id'].tolist()
    logger.info(f'High Urgency Nodes: {urgent_nodes}')

    demands = resolve_demands(urgent_nodes, nyc_network)

    solvers = {
        'greedy': GreedySolver(),
        'or_tools': ORSolver(),
    }

    vehicle_count = 1 if RUN_TYPE == 'single' else VEHICLE_COUNT

    for solver_name, solver in solvers.items():
        try:
            solution = solver.solve(HUB_NODE, urgent_nodes, vehicle_count=vehicle_count,
                                        capacity=VEHICLE_CAPACITY, net_graph=nyc_network,
                                        demands=demands)

            for i, route in enumerate(solution.routes):
                logger.info(f'[{solver_name}] Vehicle: {i}')
                logger.info(f'[{solver_name}] Travel path: {route}')
                logger.info(f'[{solver_name}] Travel time: {solution.travel_times[i]}')

            print_fleet_summary(solution, urgent_nodes, demands)
            save_solution_plots(nyc_network, solution, solver_name)
        
        except Exception as ex:
            logger.error(f"Error occurred while solving with {solver_name}: {ex}")
            continue

    os.makedirs("results", exist_ok=True)
    nyc_network.visualize(save_path="results/fleet_dispatch_schematic.png")


def resolve_demands(customer_nodes, net_graph, demands=None):
    """Resolves a demands dict for customer_nodes."""

    if demands is None:
        return {node: net_graph.NetGraph.nodes[node]['demand'] for node in customer_nodes}

    missing = [node for node in customer_nodes if node not in demands]
    if missing:
        raise ValueError(f"demands is missing entries for customer_nodes: {missing}")
    return demands


def print_fleet_summary(solution, urgent_nodes, demands):
    """Prints a summary of the fleet performance to console."""
    total_travel_time = sum(solution.travel_times)
    total_urgent = len(urgent_nodes)
    stops_served = len(solution.served)

    print(f"\n=== Fleet Summary ({solution.solver_name}) ===")
    print(f"Vehicles deployed: {len(solution.routes)}")
    print(f"Total fleet travel time: {total_travel_time:.1f} mins")
    print(f"Stops served: {stops_served}/{total_urgent}")
    for i, route in enumerate(solution.routes):
        customer_stops = [node for node in route[1:] if node in demands]
        stops_visited = len(customer_stops)
        load = sum(demands[node] for node in customer_stops)
        print(f"  V{i}: {stops_visited} stops, "
              f"{solution.travel_times[i]:.1f} mins, load={load:.2f}")


def save_solution_plots(net_graph, solution, solver_name):
    """Saves the street-network visualization for a solution's routes."""
    os.makedirs("results", exist_ok=True)
    fleet_colors = ['#e74c3c', '#2ecc71', '#f1c40f'] 

    net_graph.save_street_visualization(
        f"results/{solver_name}_street_network.png",
        route=[(route, fleet_colors[i % len(fleet_colors)]) for i, route in enumerate(solution.routes)]
    )


if __name__ == "__main__":
    main()