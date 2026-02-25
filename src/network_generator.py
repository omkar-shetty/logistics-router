
import json
import osmnx as ox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
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
        if not any('type' in data for _, data in self.NetGraph.nodes(data=True)) or \
            not any('urgency' in data for _, data in self.NetGraph.nodes(data=True)) or \
            not any('demand' in data for _, data in self.NetGraph.nodes(data=True)):
            self.assign_roles()
            
        # Check if any edge has capacity
        sample_edge = next(iter(self.NetGraph.edges(data=True)), (None, None, {}))
        if 'capacity' not in sample_edge[2]:
            self.add_capacity_data()
            
        # Ensure travel times/weights are calculated
        if 'weight' not in sample_edge[2]:
            self.add_travel_time()

        self.normalize_edge_attributes(time_weight=0.7, dist_weight=0.3)

    def add_capacity_data(self):
        """Adds maximum travel capacity to network edges."""
        for u,v,data in self.NetGraph.edges(data=True):
            if 'capacity' not in data:
                self.NetGraph.edges[u,v]['capacity'] = random.randint(10,50)
    
    def add_travel_time(self):
        """Adds nominal travel times to edges - which are also used as weights."""
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
        """Adds node to the network."""
        self.NetGraph.add_node(
            node_for_adding=loc_id,
            type = loc_type,
            pos=(x,y),
            x=x,
            y=y,
            demand=demand
        )

    def add_edge(self, start_loc:str, end_loc:str, distance:float, traffic_factor:float=1):
        """Adds an edge to the network."""
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
        """Assign roles, urgency and demand to nodes."""
        nodes = list(self.NetGraph.nodes)
        random.shuffle(nodes)
        
        # Assign 1 WH, 3 Hubs, rest are customers
        self.NetGraph.nodes[nodes[0]].update({'type': 'warehouse', 'urgency': 0, 'demand': 0})

        for i in range(1, 4):
            self.NetGraph.nodes[nodes[i]].update({'type': 'hub', 'urgency': 0, 'demand': 0})
        
        # Ensure remaining nodes are customers
        for i in range(4, len(nodes)):
            self.NetGraph.nodes[nodes[i]]['type'] = 'customer'
            self.NetGraph.nodes[nodes[i]]['urgency'] = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
            if 'demand' not in self.NetGraph.nodes[nodes[i]]:
                self.NetGraph.nodes[nodes[i]]['demand'] = random.uniform(5,25)

    def get_path_distance(self, source_node, target_node):
        """Returns the shortest path distance between the source and the target."""
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
        """Advanced visualization using normalized costs and node demand."""

        if self.NetGraph.number_of_nodes() > 1000:
            print("Graph too large for standard draw. Using OSMnx spatial plot...")
            ox.plot_graph(self.NetGraph, node_size=5, edge_linewidth=0.5)
            return
        
        pos = nx.get_node_attributes(self.NetGraph, 'pos')
        
        # --- 1. Edge Styling (Based on Weight/Cost) ---
        weights = [d.get('weight', 0.5) for _, _, d in self.NetGraph.edges(data=True)]
        # Map weights to a Red-Yellow-Green colormap (reversed because low cost = green)
        cmap = cm.get_cmap('RdYlGn_r') 
        edge_colors = [cmap(w) for w in weights]
        
        # --- 2. Node Styling ---
        node_colors = []
        node_sizes = []
        
        for n in self.NetGraph.nodes:
            data = self.NetGraph.nodes[n]
            n_type = data.get('type', 'customer')
            
            # Color by type
            if n_type == 'warehouse':
                node_colors.append('#e74c3c') # Bright Red
                node_sizes.append(1200)
            elif n_type == 'hub':
                node_colors.append('#3498db') # Bright Blue
                node_sizes.append(800)
            else:
                # Customer color depends on urgency
                urgency = data.get('urgency', 0)
                node_colors.append(['#2ecc71', '#f1c40f', '#e67e22'][urgency])
                # Size depends on demand
                demand = data.get('demand', 10)
                node_sizes.append(100 + (demand * 20))

        # --- 3. Plotting ---
        plt.figure(figsize=(14, 10))
        
        # Draw edges first
        nx.draw_networkx_edges(
            self.NetGraph, pos, 
            edge_color=edge_colors, 
            width=2, 
            alpha=0.6, 
            arrows=True, 
            arrowsize=15
        )
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.NetGraph, pos, 
            node_color=node_colors, 
            node_size=node_sizes, 
            edgecolors='white', 
            linewidths=1
        )

        # Only draw labels if the graph is readable (< 50 nodes)
        if self.NetGraph.number_of_nodes() < 50:
            nx.draw_networkx_labels(self.NetGraph, pos, font_size=8, font_family="sans-serif")

        plt.title("Brooklyn Logistics: Edge Color = Congestion/Cost | Node Size = Demand", fontsize=15)
        plt.axis('off')
        
        # Add a colorbar to explain the edge colors
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
        plt.colorbar(sm, label="Normalized Edge Cost (0=Fast, 1=Congested)", ax=plt.gca(), shrink=0.5)
        
        plt.show()

    def save_to_json(self, file_path: str):
        """Saves the edge data to json files."""
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
            capacity = data.get('capacity', 30)

            volatility = 0.4 if capacity < 20 else 0.1

            multi_factor = max(1.0, random.gauss(intensity, intensity*volatility))

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
            
            for key, value in data.items():
                if key == 'geometry': continue 
                # Convert lists (like multiple street names) to strings
                if isinstance(value, list):
                    edge_info[key] = ", ".join(map(str, value))
                else:
                    edge_info[key] = value
                    
            edges_data.append(edge_info)
        
        return pd.DataFrame(nodes_data), pd.DataFrame(edges_data)
    
    def export_to_csv(self, prefix="network"):
        """Exports the current state of nodes and edges to CSV files."""
        nodes_df, edges_df = self.convert_to_dataframes()
        
        nodes_file = f"{prefix}_nodes.csv"
        edges_file = f"{prefix}_edges.csv"
        
        nodes_df.to_csv(nodes_file, index=False)
        edges_df.to_csv(edges_file, index=False)
        
        print(f"Tabular export complete: \n- {nodes_file} \n- {edges_file}")

    def _min_max_scale(self, values: list, inverse=False):
        """Helper to scale a list of values between 0 and 1."""
        v_min, v_max = min(values), max(values)
        v_range = (v_max - v_min) if v_max != v_min else 1
        
        if inverse:
            return [(v_max - v) / v_range for v in values]
        return [(v - v_min) / v_range for v in values]
    
    def normalize_edge_attributes(self, time_weight=0.7, dist_weight=0.3):
        """Normalizes edge weights to a 0-1 scale, where higher values indicate more congestion."""
        edges = list(self.NetGraph.edges(data=True))
        travel_times = [data.get('travel_time', 1.0) for _, _, data in self.NetGraph.edges(data=True)]
        norm_times = self._min_max_scale(travel_times)

        lengths = [data.get('length', 1.0) for _, _, data in self.NetGraph.edges(data=True)]
        norm_dists = self._min_max_scale(lengths)
        
        for i, (u, v, data) in enumerate(edges):
            t_cost = norm_times[i]
            d_cost = norm_dists[i]
            
            # Combine into a single cost metric
            composite_cost = (time_weight * t_cost) + (dist_weight * d_cost)
            
            # Update edge metadata
            self.NetGraph.edges[u, v].update({
                'norm_time_cost': t_cost,
                'norm_dist_cost': d_cost,
                'weight': composite_cost  # Primary weight for Dijkstra
            })

    @classmethod
    def load_from_json(cls, file_path: str):
        """Creates a LogisticsNetwork instance from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Reconstruct the graph from dictionary
        graph = nx.node_link_graph(data)
        print(f"Network successfully loaded from {file_path}")
        return cls(input_graph=graph)