import networkx as nx
import matplotlib.pyplot as plt

graph = nx.erdos_renyi_graph(10, 0.3)
pos = nx.spring_layout(graph)
nx.draw(graph, pos=pos)
plt.show()
