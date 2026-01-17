
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random

class LogisticsNetwork:

    def __init__(self, input_graph=None):
        self.NetGraph = nx.DiGraph() if input_graph is None else input_graph 
        #ensure that the 'pos' metadata is available for input graphs as well.
        self.add_pos_data()
        self.add_capacity_data()
        self.assign_roles()

    def add_capacity_data(self):
        for u,v,data in self.NetGraph.edges(data=True):
            if 'capacity' not in data:
                self.NetGraph.edges[u,v]['capacity'] = random.randint(10,50)

    def add_pos_data(self):
        """Ensures all nodes have a 'pos' attribute for NetworkX drawing."""
        #TODO: Optimize further to avoid checks for each node.
        for n, data in self.NetGraph.nodes(data=True):
            if 'pos' not in data and 'x' in data and 'y' in data:
                self.NetGraph.nodes[n]['pos'] = (data['x'], data['y'])   

    def add_location(self, loc_id:str, loc_type:str, x:float, y:float, demand:float = 0):
        self.NetGraph.add_node(
            node_for_adding=loc_id,
            type = loc_type,
            pos=(x,y),
            x=x,
            y=y,
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

    def get_stats(self):
        """Returns a dictionary containing high-level graph metrics."""
        return {
            "node_count": self.NetGraph.number_of_nodes(),
            "edge_count": self.NetGraph.number_of_edges(),
            "is_directed": self.NetGraph.is_directed(),
            "density": nx.density(self.NetGraph)
        }

    def assign_roles(self):
        nodes = list(self.NetGraph.nodes)
        random.shuffle(nodes)
        
        # Assign 1 WH, 3 Hubs, rest are customers
        self.NetGraph.nodes[nodes[0]]['type'] = 'warehouse'
        for i in range(1, 4):
            self.NetGraph.nodes[nodes[i]]['type'] = 'hub'
        
        # Ensure remaining nodes are customers
        for i in range(4, len(nodes)):
            if 'type' not in self.NetGraph.nodes[nodes[i]]:
                self.NetGraph.nodes[nodes[i]]['type'] = 'customer'

    def visualize(self):
        if self.NetGraph.number_of_nodes() > 1000:
            print("Graph too large for standard draw. Using OSMnx spatial plot...")
            ox.plot_graph(self.NetGraph)
            return
        
        pos = nx.get_node_attributes(self.NetGraph, 'pos')
        colors = [
            'red' if self.NetGraph.nodes[n]['type'] == 'warehouse' 
            else 'blue' if self.NetGraph.nodes[n]['type'] == 'hub' 
            else 'green' if self.NetGraph.nodes[n].get('type') == 'customer'
            else 'gray' for n in self.NetGraph.nodes
        ]
        
        plt.figure(figsize=(12, 8))
        nx.draw(self.NetGraph, pos, with_labels=True, node_color=colors, node_size=800, font_size=8, edge_color='gray',
            arrowsize=20)
        plt.title("Logistics Network: Red (WH), Blue (Hub), Green (Customer)")
        plt.show()