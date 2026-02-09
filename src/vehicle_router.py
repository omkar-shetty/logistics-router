from src.network_generator import LogisticsNetwork

class Vehicle:

    def __init__(self, vehicle_id, capacity=100):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        self.hub = None #Assign a home hub if necessary
        self.cusomer_nodes = [] #List of customer nodes to be visited
        self.current_node = None #Node at which the vehicle is present currently.
        self.route_history = [] #List of nodes visited in order
        self.travel_time = 0 #Total travel time of the vehicle

    def move_to_target(self, target_node, node_travel_time):
        self.current_node = target_node
        self.travel_time += node_travel_time

    def generate_greedy_path(self, nodes_to_visit, net_graph: LogisticsNetwork):

        univisited_nodes = set(nodes_to_visit)
        while univisited_nodes:
            travel_dist = {}
            for node in univisited_nodes:
                dist = net_graph.get_path_distance(self.current_node,
                                                                node)
                travel_dist[node] = dist
            next_node = min(travel_dist, key=travel_dist.get)
            travel_time = travel_dist[next_node]
            self.move_to_target(next_node, travel_time)
            self.route_history.append(next_node)
            if next_node in univisited_nodes:
                univisited_nodes.remove(next_node)
       