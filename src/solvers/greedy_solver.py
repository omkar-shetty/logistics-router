from sklearn.cluster import KMeans

from src.network.network_generator import LogisticsNetwork
from src.solvers.routing_solver import RoutingSolver
from src.solvers.solution import FleetSolution
from src.vehicles.vehicle_router import Vehicle


class GreedySolver(RoutingSolver):
    """Nearest-neighbor greedy routing, one vehicle per KMeans cluster."""

    def solve(self, hub_node, customer_nodes, vehicle_count, capacity,
              net_graph: LogisticsNetwork, demands=None) -> FleetSolution:
        customer_nodes = list(customer_nodes)

        clusters = self._cluster_nodes(customer_nodes, net_graph, vehicle_count)

        fleet = [Vehicle(vehicle_id=i, start_node=hub_node, capacity=capacity)
                 for i in range(vehicle_count)]

        for i, vehicle in enumerate(fleet):
            self._generate_greedy_path(vehicle, clusters[i], net_graph, demands)

        routes = [vehicle.route_history for vehicle in fleet]
        travel_times = [vehicle.travel_time for vehicle in fleet]
        served = {node for vehicle in fleet for node in vehicle.route_history[1:] if node != hub_node}
        skipped = {node for vehicle in fleet for node in vehicle.skipped_nodes}

        return FleetSolution(
            routes=routes,
            travel_times=travel_times,
            served=served,
            skipped=skipped,
            solver_name="greedy",
        )

    def _cluster_nodes(self, customer_nodes, net_graph: LogisticsNetwork, vehicle_count):
        """Partition customer_nodes into vehicle_count clusters via KMeans on coordinates."""
        coords = [
            (net_graph.NetGraph.nodes[node]['x'], net_graph.NetGraph.nodes[node]['y'])
            for node in customer_nodes
        ]
        kmeans = KMeans(n_clusters=vehicle_count,
                         init='k-means++',
                         random_state=42).fit(coords)

        clusters = [[] for _ in range(vehicle_count)]
        for node, label in zip(customer_nodes, kmeans.labels_):
            clusters[label].append(node)
        return clusters

    def _generate_greedy_path(self, vehicle: Vehicle, nodes_to_visit, net_graph: LogisticsNetwork, demands):
        """Greedy nearest-neighbor traversal of nodes_to_visit for a single vehicle."""
        unvisited_nodes = set(nodes_to_visit)
        while unvisited_nodes:
            travel_dist = {}
            for node in unvisited_nodes:
                dist = net_graph.get_path_distance(vehicle.current_node, node)
                travel_dist[node] = dist
            next_node = min(travel_dist, key=travel_dist.get)
            if demands is None:
                demand = net_graph.NetGraph.nodes[next_node]['demand']
            else:
                demand = demands[next_node]
            if vehicle.carried_load + demand <= vehicle.capacity:
                travel_time = travel_dist[next_node]
                vehicle.move_to_target(next_node, travel_time, demand)
                vehicle.route_history.append(next_node)
                if next_node in unvisited_nodes:
                    unvisited_nodes.remove(next_node)
            else:
                # TODO: Implement a mechanism to handle skipped nodes due to capacity constraints
                vehicle.skipped_nodes.append(next_node)
                unvisited_nodes.remove(next_node)  # Node cannot be visited with the current load

        if vehicle.current_node != vehicle.hub:
            return_time = net_graph.get_path_distance(vehicle.current_node, vehicle.hub)
            vehicle.travel_time += return_time
            vehicle.route_history.append(vehicle.hub)
            vehicle.current_node = vehicle.hub