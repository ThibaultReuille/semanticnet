import networkx as nx
import json
from itertools import chain

class GraphException(Exception):
    """Generic Semantic Graph Exception"""
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class Event:
    def __init__(self, timecode, name, attributes):
        self.timecode = timecode
        self.name = name
        self.attributes = attributes

class Graph:
    def __init__(self, verbose=False):
        self.g = nx.MultiGraph()
        self.edges = {}

        self.verbose = verbose
        self.last_node_id = -1
        self.last_edge_id = -1

        self.meta = {}
        self.timeline = []

        self.attr_reserved = ["id", "src", "dst"]

    def log(self, line):
        if self.verbose:
            print("[SemanticNet] " + line)

    def create_node_uid(self):
        self.last_node_id += 1
        return self.last_node_id

    def create_edge_uid(self):
        self.last_edge_id += 1
        return self.last_edge_id

    def add_node(self, data):   
        id = self.create_node_uid()
        self.log("add_node " + str(data) + " = " + str(id)) 
        self.g.add_node(id, data)
        return id

    def add_edge(self, src, dst, data={}):
        if self.g.has_node(src) and self.g.has_node(dst):
            id = self.create_edge_uid()
            self.log("add_edge " + str(src) + ", " + str(dst) + ", " + str(data) + " = " + str(id))
            self.g.add_edge(src, dst, id, dict(chain(data.items(), {"id": id}.items())) )
            self.edges[id] = self.g.edge[src][dst][id]
            return id
        else:
            raise GraphException("Node ID not found, can't create edge.")

    def set_node_attribute(self, id, attr_name, value):
        if self.g.has_node(id):
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self.g.node[id][attr_name] = value
        else:
            raise GraphException("Node id not found, can't set attribute.")

    def get_node_attribute(self, id, attr_name):
        if self.g.has_node(id):
            return self.g.node[id][attr_name]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def set_edge_attribute(self, id, attr_name, value):
        if id in self.edges:
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self.edges[id][attr_name] = value
        else:
            raise GraphException("Edge id '" + str(id) + "' not found!")

    def get_edge_attribute(self, id, attr_name):
        if id in self.edges:
            if attr_name in self.edges[id]:
                return self.edges[id][attr_name]
            else:
                return None
        else:
            raise GraphException("Edge id '" + str(id) + "' not found!")

    def add_event(self, timecode, name, attributes):
        self.timeline.append(Event(timecode, name, attributes))

    def save_json(self, filename):
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = [ dict(chain({"id": i}.items(), self.g.node[i].items())) for i in self.g.nodes() ]
            graph["edges"] = [ dict(
                chain(
                    { "src": i, "dst": j, "id": key}.items(),
                    self.g.edge[i][j][key].items())
                )
                for i, j in self.g.edges()
                for key in self.g.edge[i][j]
            ]
            graph["timeline"] = [ [c.timecode, c.name, c.attributes] for c in self.timeline ]
            json.dump(graph, outfile, indent=True)

    def load_json(self, filename):
        with open(filename, 'r') as infile:
            graph = json.load(infile)
            self.meta = graph["meta"]
            self.timeline = graph["timeline"]

            for node in graph["nodes"]:
                self.g.add_node(node["id"], dict([item for item in node.items() if item[0] != 'id']))

            for edge in graph["edges"]:
                self.g.add_edge(edge["src"], edge["dst"], dict(item for item in edge.items() if (item[0] != "src" and item[0] != "dst") ))

            self.last_node_id = len(self.g.nodes())
            self.last_edge_id = len(self.g.edges())

if __name__ == "__main__":
    print("Please import this module !")
