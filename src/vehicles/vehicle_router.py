class Vehicle:

    def __init__(self, vehicle_id, start_node, capacity=100):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        self.hub = start_node #Assign a home hub if necessary
        self.customer_nodes = [] #List of customer nodes to be visited
        self.current_node = start_node #Node at which the vehicle is present currently.
        self.route_history = [start_node] #List of nodes visited in order
        self.travel_time = 0 #Total travel time of the vehicle
        self.carried_load = 0 #Current load assigned to the vehicle
        self.skipped_nodes = [] #List of nodes that were skipped due to capacity constraints

    def move_to_target(self, target_node, node_travel_time, demand):
        """Moves the vehicle to the target node"""
        self.current_node = target_node
        self.travel_time += node_travel_time
        self.carried_load += demand
