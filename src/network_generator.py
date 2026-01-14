import networkx as nx
import matplotlib.pyplot as plt
import random

class LogisticsNetwork:

    def __init__(self):
        self.NetGraph = nx.DiGraph()

    def add_location(self, loc_id:str, loc_type:str, x:float, y:float, demand:float = 0):
        self.NetGraph.add_node(
            node_for_adding=loc_id,
            type = loc_type,
            pos=(x,y),
            demand=demand
        )

    def add_edge(self, start_loc:str, end_loc:str, distance:float, traffic_factor:float=1):
        weighted_dist = distance*traffic_factor
        self.NetGraph.add_edge(
            u_of_edge=start_loc,
            v_of_edge=end_loc,
            distance=distance,
            weight=weighted_dist
        )

    def visualize(self):
        pos = nx.get_node_attributes(self.NetGraph, 'pos')
        colors = [
            'red' if self.NetGraph.nodes[n]['type'] == 'warehouse' 
            else 'blue' if self.NetGraph.nodes[n]['type'] == 'hub' 
            else 'green' for n in self.NetGraph.nodes
        ]
        
        plt.figure(figsize=(10, 7))
        nx.draw(self.NetGraph, pos, with_labels=True, node_color=colors, node_size=500, font_size=8)
        plt.title("Logistics Network: Red (WH), Blue (Hub), Green (Customer)")
        plt.show()

net = LogisticsNetwork()

# 1. Add Warehouse
net.add_location("WH_01", "warehouse", x=0, y=0)

# 2. Add Regional Hubs
for i in range(3):
    net.add_location(f"HUB_{i}", "hub", x=random.uniform(-5, 5), y=random.uniform(-5, 5))
    net.add_edge("WH_01", f"HUB_{i}", distance=random.uniform(10, 20))

# 3. Add Customer Points
for i in range(10):
    target_hub = f"HUB_{random.randint(0, 2)}"
    net.add_location(f"CUST_{i}", "customer", x=random.uniform(-10, 10), y=random.uniform(-10, 10), demand=random.randint(1, 5))
    net.add_edge(target_hub, f"CUST_{i}", distance=random.uniform(2, 8))

net.visualize()