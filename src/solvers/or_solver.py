from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from src.solvers.solution import FleetSolution
from src.solvers.routing_solver import RoutingSolver

class ORSolver(RoutingSolver):
    """OR based routing optimizer."""

    def solve(self, hub_node, customer_nodes, vehicle_count, capacity,
              net_graph: LogisticsNetwork, demands=None)-> FleetSolution:
        """Compute routes for a fleet of vehicles serving customer_nodes."""
        customer_nodes = list(customer_nodes)
        data = self._build_data_model(hub_node, 
                                      customer_nodes, 
                                      vehicle_count, 
                                      capacity, 
                                      net_graph, 
                                      demands)
        manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            """Tracks capacity requirements per node step."""
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # Null capacity slack
        data["vehicle_capacities"],  # Max load structural arrays
        True,  # Restrict variables to start empty at base depot
        "Capacity"
        )

        max_distance = max(max(row) for row in data["distance_matrix"])
        drop_penalty = max_distance * len(data["locations"])
        for node_index in range(1, len(data["locations"])):
            routing.AddDisjunction([manager.NodeToIndex(node_index)], drop_penalty)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        # Fast initial constructive path discovery strategy
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        # Advanced Metaheuristic escape logic to optimize routes past local minima
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 5

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            routes = []
            travel_times = []
            served = set()

            for vehicle_id in range(data["num_vehicles"]):
                index = routing.Start(vehicle_id)
                route = [data["locations"][manager.IndexToNode(index)]]
                route_time = 0
                while not routing.IsEnd(index):
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                    node = data["locations"][manager.IndexToNode(index)]
                    if not routing.IsEnd(index):
                        route.append(node)
                        served.add(node)
                routes.append(route)
                travel_times.append(route_time)

            skipped = set(customer_nodes) - served

            return FleetSolution(
                routes=routes,
                travel_times=travel_times,
                served=served,
                skipped=skipped,
                solver_name="or_tools",
            )
        else:
            raise Exception("No solution found for the given routing problem.")


    def _build_data_model(self, hub_node, customer_nodes, vehicle_count, capacity,
              net_graph, demands=None):
        """Builds the data model for OR-Tools routing solver."""
        data = {}
        data['locations'], data['node_to_index'] = self._map_nodes_to_indices(hub_node, customer_nodes)
        data['distance_matrix'] = self._build_time_matrix(net_graph, data['locations'])
        data['num_vehicles'] = vehicle_count
        data['vehicle_capacities'] = [capacity] * vehicle_count
        data['depot'] = 0
        data['demands'] = [0] * len(data['locations'])
        for node in customer_nodes:
            data['demands'][data['node_to_index'][node]] = round(demands[node])
        return data

    def _build_time_matrix(self, net_graph, nodes):
        """Builds a square travel-time matrix over hub and customer_nodes."""
        size = len(nodes)
        raw = [[0] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                if i == j:
                    continue
                raw[i][j] = net_graph.get_path_distance(nodes[i], nodes[j])

        finite_values = [v for row in raw for v in row if v != float('inf')]
        unreachable_penalty = int(max(finite_values, default=0)) * size + 1

        matrix = [
            [unreachable_penalty if v == float('inf') else round(v) for v in row] #since OR-Tools requires ints
            for row in raw
        ] #replace inf with large finite penalty (represents unreachable pairs)
        return matrix
    
    def _map_nodes_to_indices(self, hub_node, customer_nodes):
        """Maps nodes to indices for the OR-Tools solver."""
        nodes = [hub_node] + list(customer_nodes)
        node_to_index = {node: index for index, node in enumerate(nodes)}
        return nodes, node_to_index