
import json
import osmnx as ox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random

class LogisticsNetwork:

    def __init__(self, input_graph=None):
        self.NetGraph = nx.DiGraph() if input_graph is None else input_graph 
        #ensure that the 'pos' metadata is available for input graphs as well.
        self.add_pos_data()
        self._initialize_metadata()
        # self.add_capacity_data()
        # self.assign_roles()
    
    def _initialize_metadata(self):
        """Ensures the graph has necessary attributes without overwriting existing ones."""
        # Check if any node has a type; if not, assign roles
        if not any('type' in data for _, data in self.NetGraph.nodes(data=True)):
            self.assign_roles()
            
        # Check if any edge has capacity
        sample_edge = next(iter(self.NetGraph.edges(data=True)), (None, None, {}))
        if 'capacity' not in sample_edge[2]:
            self.add_capacity_data()
            
        # Ensure travel times/weights are calculated
        if 'weight' not in sample_edge[2]:
            self.add_travel_time()

    def add_capacity_data(self):
        for u,v,data in self.NetGraph.edges(data=True):
            if 'capacity' not in data:
                self.NetGraph.edges[u,v]['capacity'] = random.randint(10,50)
    
    def add_travel_time(self):
        for u,v, data in self.NetGraph.edges(data=True):
            distance_metres = data.get('length',1)
            speed_kmh = data.get('speed_kph',30)
            speed_mpm = (speed_kmh * 1000) / 60  # meters per minute
            travel_time_min = distance_metres / speed_mpm

            self.NetGraph.edges[u, v]['travel_time'] = travel_time_min
            self.NetGraph.edges[u, v]['weight'] = travel_time_min

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
        self.NetGraph.nodes[nodes[0]]['urgency'] = 0

        for i in range(1, 4):
            self.NetGraph.nodes[nodes[i]]['type'] = 'hub'
            self.NetGraph.nodes[nodes[i]]['urgency'] = 0
        
        # Ensure remaining nodes are customers
        for i in range(4, len(nodes)):
            if 'type' not in self.NetGraph.nodes[nodes[i]]:
                self.NetGraph.nodes[nodes[i]]['type'] = 'customer'
                self.NetGraph.nodes[nodes[i]]['urgency'] = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]

    def get_path_distance(self, source_node, target_node):
        try:
            path_dist = nx.shortest_path_length(self.NetGraph, 
                                        source=source_node, 
                                        target=target_node, 
                                        weight='weight')

            return path_dist
        except nx.NetworkXNoPath:
            # Instead of crashing, return a penalty value (infinity)
            print(f"Warning: No path found between {source_node} and {target_node}")
            return float('inf')

    def visualize(self):
        if self.NetGraph.number_of_nodes() > 1000:
            print("Graph too large for standard draw. Using OSMnx spatial plot...")
            ox.plot_graph(self.NetGraph)
            return
        
        pos = nx.get_node_attributes(self.NetGraph, 'pos')
        colors = []
        for n in self.NetGraph.nodes:
            node_type = self.NetGraph.nodes[n].get('type', 'unknown')
            if node_type == 'warehouse':
                colors.append('red')
            elif node_type == 'hub':
                colors.append('blue')
            elif node_type == 'customer':
                urgency = self.NetGraph.nodes[n].get('urgency', 0)
                if urgency == 2:
                    colors.append('darkgreen')
                elif urgency == 1:
                    colors.append('green')
                else:
                    colors.append('lightgreen')
        
        plt.figure(figsize=(12, 8))
        nx.draw(self.NetGraph, pos, with_labels=True, node_color=colors, node_size=800, font_size=8, edge_color='gray',
            arrowsize=20)
        plt.title("Logistics Network: Red (WH), Blue (Hub), Green (Customer)")
        plt.show()

    def save_to_json(self, file_path: str):
        G_copy = self.NetGraph.copy()
        
        # Remove 'geometry' attribute from all edges
        for u, v, data in G_copy.edges(data=True):
            if 'geometry' in data:
                del data['geometry']
                
        data = nx.node_link_data(G_copy)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Network successfully saved to {file_path}")

    def simulate_traffic(self, intensity=1.5):
        """Generates traffick data to simulate rush hour.

        Args:
            intensity (float, optional): Ranges between 1(low traffic) to 3(rush hour). Defaults to 1.5.
        """
        for u,v, data in self.NetGraph.edges(data=True):

            base_time = data.get('travel_time', 1.0)
            multi_factor = random.uniform(intensity*0.8, intensity*1.2)
            self.NetGraph.edges[u,v]['weight'] = base_time*multi_factor
            self.NetGraph.edges[u,v]['congestion_factor'] = multi_factor

    def convert_to_dataframes(self):
        """Converts the graph's nodes and edges to pandas DataFrames."""

        nodes_data = []
        for n, data in self.NetGraph.nodes(data=True):
            node_info = {'node_id': n}
            node_info.update(data)
            nodes_data.append(node_info)
        nodes_df = pd.DataFrame(nodes_data)

        edges_data = []
        for u, v, data in self.NetGraph.edges(data=True):
            edge_info = {'start_node': u, 'end_node': v}
            edge_info.update(data)
            edges_data.append(edge_info)
        edges_df = pd.DataFrame(edges_data)

        return nodes_df, edges_df

    @classmethod
    def load_from_json(cls, file_path: str):
        """Creates a LogisticsNetwork instance from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Reconstruct the graph from dictionary
        graph = nx.node_link_graph(data)
        print(f"Network successfully loaded from {file_path}")
        return cls(input_graph=graph)