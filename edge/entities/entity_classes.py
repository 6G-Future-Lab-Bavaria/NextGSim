from edge.entities import Router
from edge.edge_server_types import EdgeServerTypes


def get_entity_class(class_name):
    if class_name == "router":
        return Router
    if class_name == "edge_server1":
        return EdgeServerTypes.EdgeServer1
    if class_name == "edge2":
        return EdgeServerTypes.EdgeServer2
    if class_name == "edge3":
        return EdgeServerTypes.EdgeServer3


def get_entity_type(class_name):
    if class_name == "edge_server1" or "edge_server2" or "edge_server3":
        return "edge_server"
    if class_name == "router":
        return "router"
