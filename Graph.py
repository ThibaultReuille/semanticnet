import networkx as nx
import json
import uuid
import copy
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
    '''A simple Graph structure which lets you focus on the data.'''

    def __init__(self, verbose=False):
        self._g = nx.MultiGraph()
        self._edges = {}
        self.meta = {}
        self.timeline = []

        self.verbose = verbose
        self.attr_reserved = ["id", "src", "dst"]

    def _create_uuid(self):
        '''Create a random UUID for a new node or edge. Checks for collisions.'''
        id_ = uuid.uuid4()
        while self._g.has_node(id_) or id_ in self._edges:
            id_ = uuid.uuid4()
        return id_

    def _extract_uuid(self, id_):
        '''Parse a UUID out of the string id_.'''
        if id_.__class__.__name__ == 'UUID':
            return id_

        return uuid.UUID(id_)

    def log(self, line):
        '''Print the message line to standard output.'''
        if self.verbose:
            print("[SemanticNet] " + line)

    def add_node(self, data={}, id_=None):
        '''Add a node to the graph, with an optional dict of attributes, data.
        Although you can specify your own id with id_, it is recommended NOT
        to do this, to avoid unintentional collisions and/or data loss.
        '''
        if id_ == None:
            id_ = self._create_uuid()
        else:
            id_ = self._extract_uuid(id_)

        data['id'] = id_ # add the ID to the attributes
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
        '''Add an edge from src to dst, with an optional dict of attributes, data.
        Although you can specify your own id with id_, it is recommended NOT
        to do this, to avoid unintentional collisions and/or data loss.
        '''
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
            self._edges[id_] = self._g.edge[src][dst][id_]
            return id_
        else:
            raise GraphException("Node ID not found.")

    def remove_edge(self, id_):
        '''Removes edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self._edges:
            edge = self._edges[id_]
            self._g.remove_edge(edge["src"], edge["dst"], id_)
            del self._edges[id_]
        else:
            raise GraphException("Node ID not found.")

    def set_node_attribute(self, id_, attr_name, value):
        '''Sets the attribute attr_name to value for node id_.'''
        id_ = self._extract_uuid(id_)

        if self._g.has_node(id_):
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self._g.node[id_][attr_name] = value
        else:
            raise GraphException("Node id not found, can't set attribute.")

    def get_nodes(self):
        '''Returns a list of all nodes in the graph.'''
        return dict([ (id_, self._g.node[id_]) for id_ in self._g.nodes() ])

    def get_node_attribute(self, id_, attr_name):
        '''Returns the attribute attr_name of node id_.'''
        id_ = self._extract_uuid(id_)
        if self._g.has_node(id_):
            return self._g.node[id_][attr_name]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_node_attributes(self, id_):
        '''Returns all attributes of node id_.'''
        id_ = self._extract_uuid(id_)
        if self._g.has_node(id_):
            return self._g.node[id_]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_edges(self):
        '''Returns all edges in the graph.'''
        return self._edges

    def get_edge(self, id_):
        '''Returns edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self._edges:
            return self._edges[id_]
        else:
            raise GraphException('Node ID not found.')

    def set_edge_attribute(self, id_, attr_name, value):
        '''Sets the attribute attr_name to value for edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self._edges:
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self._edges[id_][attr_name] = value
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attributes(self, id_):
        '''Returns all attributes for edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self._edges:
            return self._edges[id_]
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attribute(self, id_, attr_name):
        '''Returns the attribute attr_name for edge id_.'''
        id_ = self._extract_uuid(id_)
        if id_ in self._edges:
            if attr_name in self._edges[id_]:
                return self._edges[id_][attr_name]
            else:
                return None
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def add_event(self, timecode, name, attributes):
        self.timeline.append(Event(timecode, name, attributes))

    def save_json(self, filename):
        '''Exports the graph to a JSON file for use in the Gaia visualizer.'''
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = [ dict(chain(self._g.node[id_].items(), {"id": id_.hex}.items())) for id_ in self._g.nodes() ]
            graph["edges"] = [
                dict(
                    chain(
                        self._g.edge[i][j][key].items(),
                        { "src": i.hex, "dst": j.hex, "id": key.hex}.items()
                    )
                )
                for i, j in self._g.edges()
                for key in self._g.edge[i][j]
            ]
            graph["timeline"] = [ [c.timecode, c.name, c.attributes] for c in self.timeline ]
            json.dump(graph, outfile, indent=True)

    def load_json(self, filename):
        '''Generates a graph from the JSON file filename.'''
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
                    dict([item for item in edge.items()
                            if (item[0] != "src" and item[0] != "dst" and item[0] != "id")] ),
                    id_
                )
                self._g.edge[src][dst][id_]["id"] = id_

    def networkx_graph(self):
        return copy.deepcopy(self._g)

if __name__ == "__main__":
    print("Please import this module !")
