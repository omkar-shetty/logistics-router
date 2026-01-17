import osmnx as ox
import random 

from .network_generator import LogisticsNetwork

#from src.network_generator import LogisticsNetwork

class SpatialDataMapper:

    @staticmethod
    def from_place(place_name, target_nodes=30):
        graph = ox.graph_from_place(place_name, network_type='drive')
        print(f'downloaded map for {place_name}.')
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)
        graph = ox.convert.to_digraph(graph)

        #Generate a sub-graph
        start_node = random.choice(list(graph.nodes))
        nodes = {start_node}
        while len(nodes) < target_nodes:
            new_nodes = set()
            for n in nodes:
                new_nodes.update(graph.neighbors(n))
            nodes.update(new_nodes)
            if len(new_nodes) == 0: break # Safety break
            
        # Keep only the first 30 nodes from our expanded set
        sub_graph = graph.subgraph(list(nodes)[:target_nodes]).copy()

        return LogisticsNetwork(sub_graph)
