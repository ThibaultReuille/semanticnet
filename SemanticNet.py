import networkx as nx
import json
import uuid
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
        self._g = nx.MultiGraph()
        self.edges = {}
        self.meta = {}
        self.timeline = []

        self.verbose = verbose
        self.attr_reserved = ["id", "src", "dst"]

    def _create_uuid(self):
        id_ = uuid.uuid4()
        while self._g.has_node(id_) or id_ in self.edges:
            id_ = uuid.uuid4()
        return id_

    def _extract_uuid(self, id_):
        if id_.__class__.__name__ == 'UUID':
            return id_

        return uuid.UUID(id_)

    def log(self, line):
        if self.verbose:
            print("[SemanticNet] " + line)

    def add_node(self, data={}, id_=None):
        if id_ == None:
            id_ = self._create_uuid()
        else:
            id_ = self._extract_uuid(id_)

        self.log("add_node " + str(data) + " = " + str(id_))
        self._g.add_node(id_, data)
        return id_

    def remove_node(self, id_):
        '''Removes node id_.'''
        id_ = self._extract_uuid(id_)
        if self._g.has_node(id_):
            for neighbor in self._g.neighbors(id_):
                # need to iterate over items() (which copies the dict) because we are
                # removing items from the edges dict as we are iterating over it
                for edge in self._g.edge[id_][neighbor].items():
                    # edge[0] is the edge's ID
                    self.remove_edge(self._g.edge[id_][neighbor][edge[0]]["id"])
            self._g.remove_node(id_)
        else:
            raise GraphException("Node ID not found.")

    def add_edge(self, src, dst, data={}, id_=None):
        src = self._extract_uuid(src)
        dst = self._extract_uuid(dst)

        if id_ == None:
            id_ = self._create_uuid()
        else:
            id_ = self._extract_uuid(id_)

        if self._g.has_node(src) and self._g.has_node(dst):
            self.log("add_edge " + str(src) + ", " + str(dst) + ", " + str(data) + " = " + str(id_))
            self._g.add_edge(src, dst, id_,
                dict(chain(data.items(),
                    {
                        "id": id_,
                        "src": src,
                        "dst": dst
                    }.items())
                )
            )
            self.edges[id_] = self._g.edge[src][dst][id_]
            return id_
        else:
            raise GraphException("Node ID not found.")

    def remove_edge(self, id_):
        '''Removes edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self.edges:
            edge = self.edges[id_]
            self._g.remove_edge(edge["src"], edge["dst"], id_)
            del self.edges[id_]
        else:
            raise GraphException("Node ID not found.")

    def set_node_attribute(self, id_, attr_name, value):
        id_ = self._extract_uuid(id_)

        if self._g.has_node(id_):
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self._g.node[id_][attr_name] = value
        else:
            raise GraphException("Node id not found, can't set attribute.")

    def get_nodes(self):
        return self._g.nodes()

    def get_node_attribute(self, id_, attr_name):
        id_ = self._extract_uuid(id_)
        if self._g.has_node(id_):
            return self._g.node[id_][attr_name]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_node_attributes(self, id_):
        id_ = self._extract_uuid(id_)
        if self._g.has_node(id_):
            return self._g.node[id_]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_edges(self):
        return self.edges

    def get_edge(self, id_):
        id_ = self._extract_uuid(id_)
        if id_ in self.edges:
            return self.edges[id_]
        else:
            raise GraphException('Node ID not found.')

    def set_edge_attribute(self, id_, attr_name, value):
        id_ = self._extract_uuid(id_)
        if id_ in self.edges:
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self.edges[id_][attr_name] = value
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attributes(self, id_):
        id_ = self._extract_uuid(id_)
        if id_ in self.edges:
            return self.edges[id_]
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attribute(self, id_, attr_name):
        id_ = self._extract_uuid(id_)
        if id_ in self.edges:
            if attr_name in self.edges[id_]:
                return self.edges[id_][attr_name]
            else:
                return None
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def add_event(self, timecode, name, attributes):
        self.timeline.append(Event(timecode, name, attributes))

    def save_json(self, filename):
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = [ dict(chain({"id": id_.hex}.items(), self._g.node[id_].items())) for id_ in self._g.nodes() ]
            graph["edges"] = [
                dict(
                    chain(
                        { "src": i.hex, "dst": j.hex, "id": key.hex}.items(),
                        [ item for item in self._g.edge[i][j][key].items()
                            if  item[0] != 'id' and
                                item[0] != 'src' and
                                item[0] != 'dst'
                        ]
                    )
                )
                for i, j in self._g.edges()
                for key in self._g.edge[i][j]
            ]
            graph["timeline"] = [ [c.timecode, c.name, c.attributes] for c in self.timeline ]
            json.dump(graph, outfile, indent=True)

    def load_json(self, filename):
        with open(filename, 'r') as infile:
            graph = json.load(infile)
            self.meta = graph["meta"]
            self.timeline = graph["timeline"]

            for node in graph["nodes"]:
                self._g.add_node(uuid.UUID(node["id"]), dict([item for item in node.items() if item[0] != 'id']))

            for edge in graph["edges"]:
                src = uuid.UUID(edge["src"])
                dst = uuid.UUID(edge["dst"])
                id_ = uuid.UUID(edge["id"]) if edge["id"] != None else self._create_uuid()
                self.add_edge(
                    src,
                    dst,
                    dict(item for item in edge.items()
                        if (item[0] != "src" and item[0] != "dst" and item[0] != "id") ),
                    id_
                )
                self._g.edge[src][dst][id_]["id"] = id_

if __name__ == "__main__":
    print("Please import this module !")
