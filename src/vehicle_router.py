import pandas as pd

class Vehicle:

    def __init__(self, vehicle_id, capacity=100):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        self.hub = None #Assign a home hub if necessary
        self.cusomer_nodes = [] #List of customer nodes to be visited
        self.current_node = None #Node at which the vehicle is present currently.
        self.route_history = [] #List of nodes visited in order
        self.travel_time = 0 #Total travel time of the vehicle

    def generate_greedy_path(self, nodes_df, edged_df):
        #Only traveling to urgent nodes
        urgent_nodes = nodes_df.loc[nodes_df['urgency']>=1]             
        pass