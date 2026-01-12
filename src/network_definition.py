import networkx as nx
import matplotlib.pyplot as plt
import random

def create_logistics_hub(num_spokes=8):
    # star_graph(n) creates a center node (0) and n peripheral nodes
    G = nx.star_graph(num_spokes)
    
    #sAdd business metadata to nodes
    for node in G.nodes:
        if node == 0:
            G.nodes[node]['type'] = 'Regional Hub'
            G.nodes[node]['color'] = 'red'
        else:
            G.nodes[node]['type'] = 'Customer/Spoke'
            G.nodes[node]['color'] = 'skyblue'
            G.nodes[node]['demand'] = 10 

    return G
    
# Initialize and draw
num_nodes = random.randint(2,12)
logistics_map = create_logistics_hub(num_nodes)
colors = [logistics_map.nodes[n]['color'] for n in logistics_map.nodes]

plt.figure(figsize=(8, 6))
nx.draw(logistics_map, with_labels=True, node_color=colors, node_size=800)
plt.title("Initial Logistics Hub-and-Spoke Topology")
plt.show()

# Verification of connectivity (The Dijkstra foundation)
print(f"Total connections from Hub: {logistics_map.degree(0)}")