import networkx as nx
import json


def save_json(graph):
    cytoscape_json = nx.readwrite.cytoscape_data(graph)
    # with open("../result_collection/data.json"):
    #     json.dump(cytoscape_json)
    print(cytoscape_json)