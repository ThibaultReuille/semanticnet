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

class Event(object):
    def __init__(self, timecode, name, attributes):
        self.timecode = timecode
        self.name = name
        self.attributes = attributes

class Graph(object):
    '''A simple Graph structure which lets you focus on the data.'''

    def __init__(self, verbose=False):
        self._g = nx.MultiGraph()
        self._edges = {}
        self._node_cache = {}
        
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

    def _extract_id(self, id_):
        '''Parse a UUID out of the string id_.'''
        if id_.__class__.__name__ == 'UUID':
            return id_

        # convert to a UUID if possible
        try:
            id_ = uuid.UUID(id_)
        # if it's not a UUID, just return what was sent
        except:
            pass

        return id_

    def _cache_node(self, attr, node):
        '''Cache a node in self._node_cache'''
        # if we have not cached anything by this attr before,
        # create an empty dict for it
        if attr not in self._node_cache:
            self._node_cache[attr] = {}

        # if we haven't seen this attr value before, make an empty list for it
        if node[attr] not in self._node_cache[attr]:
            self._node_cache[attr][node[attr]] = []

        # add it to the cache
        self._node_cache[attr][node[attr]].append(node)

    def _cache_new_node(self, attrs):
        '''Checks a new node's attributes and caches it if we are caching by one or more
        of its attributes.
        '''
        for key in self._node_cache:
            if key in attrs:
                self._cache_node(key, attrs)

    def _remove_node_from_cache(self, id_):
        '''Removes node id_ from all places it occurs in the cache, if anywhere.'''
        node = self._g.node[id_]
        for attr, val in node.iteritems():
            try:
                self._node_cache[attr][val].remove(node)
            except KeyError:
                pass

    def _update_node_cache(self, id_, attr_name):
        '''Update the cache for the given node with ID id_ and attribute attr_name

        IMPORTANT: Assumes that the attribute has already been set with the new value!
        '''

        # if we are not caching by this attribute, there is nothing to do
        if attr_name not in self._node_cache:
            return

        # remove any nodes that are in the wrong place in the cache
        for key, nodes in self._node_cache[attr_name].items():
            for node in nodes:
                if key not in node:
                    self._node_cache[attr_name][key].remove(node)
                    break # should only happen once

        self._cache_node(attr_name, self._g.node[id_])

    def log(self, line):
        '''Print the message line to standard output.'''
        if self.verbose:
            print("[SemanticNet] " + line)

    def add_node(self, data={}, id_=None):
        '''Add a node to the graph, with an optional dict of attributes, data.

        By default, providing an ID is unnecessary; a random UUID is generated for each node.
        However, if you wish to key by something else, you can do so with the id_ parameter.
        If you choose to do this, please note that adding a node with the same ID twice
        overwrites the node that was previously there, so you must check for the presence
        of a node with an ID manually, if you wish to avoid this.
        '''
        if id_ == None:
            id_ = self._create_uuid()
        else:
            id_ = self._extract_id(id_)

        data['id'] = id_ # add the ID to the attributes
        self.log("add_node " + str(data) + " = " + str(id_))
        self._g.add_node(id_, data)
        self._cache_new_node(data)
        return id_

    def remove_node(self, id_):
        '''Removes node id_.'''
        id_ = self._extract_id(id_)
        if self._g.has_node(id_):
            # remove all edges incident on this node
            for neighbor in self._g.neighbors(id_):
                # need to iterate over items() (which copies the dict) because we are
                # removing items from the edges dict as we are iterating over it
                for edge in self._g.edge[id_][neighbor].items():
                    # edge[0] is the edge's ID
                    self.remove_edge(self._g.edge[id_][neighbor][edge[0]]["id"])
            self._remove_node_from_cache(id_)
            self._g.remove_node(id_)
        else:
            raise GraphException("Node ID not found.")

    def add_edge(self, src, dst, data={}, id_=None):
        '''Add an edge from src to dst, with an optional dict of attributes, data.

        By default, providing an ID is unnecessary; a random UUID is generated for each edge.
        However, if you wish to key by something else, you can do so with the id_ parameter.
        If you choose to do this, please note that adding an edge with the same ID twice
        overwrites the edge that was previously there, so you must check for the presence
        of an edge with an ID manually, if you wish to avoid this.
        '''
        src = self._extract_id(src)
        dst = self._extract_id(dst)

        if id_ == None:
            id_ = self._create_uuid()
        else:
            id_ = self._extract_id(id_)

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
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            edge = self._edges[id_]
            self._g.remove_edge(edge["src"], edge["dst"], id_)
            del self._edges[id_]
        else:
            raise GraphException("Node ID not found.")

    def set_node_attribute(self, id_, attr_name, value):
        '''Sets the attribute attr_name to value for node id_.'''
        id_ = self._extract_id(id_)

        if self._g.has_node(id_):
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self._g.node[id_][attr_name] = value
            self._update_node_cache(id_, attr_name)
        else:
            raise GraphException("Node id not found, can't set attribute.")

    def get_nodes(self):
        '''Returns a list of all nodes in the graph.'''
        return dict([ (id_, self._g.node[id_]) for id_ in self._g.nodes() ])

    def get_node(self, id_):
        id_ = self._extract_id(id_)
        return self._g.node[id_]

    def has_node(self, id_):
        id_ = self._extract_id(id_)
        return self._g.has_node(id_)

    def get_node_attribute(self, id_, attr_name):
        '''Returns the attribute attr_name of node id_.'''
        id_ = self._extract_id(id_)
        if self._g.has_node(id_):
            return self._g.node[id_][attr_name]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_node_attributes(self, id_):
        '''Returns all attributes of node id_.'''
        id_ = self._extract_id(id_)
        if self._g.has_node(id_):
            return self._g.node[id_]
        else:
            raise GraphException("Node ID not found, can't get attribute")

    def get_edges(self):
        '''Returns all edges in the graph.'''
        return self._edges

    def get_edge(self, id_):
        '''Returns edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            return self._edges[id_]
        else:
            raise GraphException('Node ID not found.')

    def get_edges_between(self, src, dst):
        '''Returns all edges between src and dst'''
        src = self._extract_id(src)
        dst = self._extract_id(dst)
        if self._g.has_node(src) and self._g.has_node(dst) and self._g.has_edge(src, dst):
            return self._g.edge[src][dst]
        return {}

    def has_edge(self, id_):
        id_ = self._extract_id(id_)
        return id_ in self._edges

    def has_edge_between(self, src, dst):
        src = self._extract_id(src)
        dst = self._extract_id(dst)
        return self._g.has_node(src) and self._g.has_node(dst) and self._g.has_edge(src, dst)

    def set_edge_attribute(self, id_, attr_name, value):
        '''Sets the attribute attr_name to value for edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            if attr_name in self.attr_reserved:
                raise GraphException("Attribute {} is reserved.".format(attr_name))

            self._edges[id_][attr_name] = value
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attributes(self, id_):
        '''Returns all attributes for edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            return self._edges[id_]
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def get_edge_attribute(self, id_, attr_name):
        '''Returns the attribute attr_name for edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            if attr_name in self._edges[id_]:
                return self._edges[id_][attr_name]
            else:
                return None
        else:
            raise GraphException("Edge id '" + str(id_) + "' not found!")

    def add_event(self, timecode, name, attributes):
        self.timeline.append(Event(timecode, name, attributes))

    def cache_nodes_by(self, attr, build=True):
        '''Tells SemanticNet to cache nodes by the given attribute attr.

        After a call to this method, nodes will be accessible by calls to the method get_node_by_attr().
        See the docs for that function for more detail.

        Optinally, if the user wishes to tell SemanticNet to start caching NEW nodes of type attr, but not
        to build a cache from the existing nodes, they may set the 'build' flag to False.
        '''

        # If we're not already caching by this value, initialize the dict for it.
        # This is also done in _cache_node(), but this is needed for cases
        # where the user decides to start caching by an attribute, and they haven't
        # added any nodes with that attribute yet
        if attr not in self._node_cache:
            self._node_cache[attr] = {}

        if not build:
            return

        for node in [ self._g.node[i] for i in self._g.nodes() ]:
            if attr in node:
                self._cache_node(attr, node)

    def clear_node_cache(self, attr=""):
        '''Delete the cache. If attr is given, delete the cache for that attribute.'''

        if attr == "":
            self._node_cache = {}
        elif attr in self._node_cache:
            self._node_cache[attr] = {}

    def get_nodes_by_attr(self, attr, val=None, nosingleton=False):
        '''Gets all nodes with the given attribute attr and value val.

        If val is not specified, returns a dict of all nodes, keyed by attr.

        If there are no nodes with the given attr or val, returns an empty list.

        Optionally, if the nosingleton parameter is set to True, and there is only one node in a list,
        the method will only return that single node, rather than a singleton list. This is useful,
        for instance, if the user knows all nodes with attributes of a certain type will be unique,
        and wishes to simply use attr as the node key.
        '''
        nodes = self._node_cache.get(attr)

        # if the attribute doesn't exist, return an empty dict
        if nodes == None:
            return {}

        # if no value was specified for the attribute, return the whole dict
        # of nodes keyed by attr
        if val == None:
            return nodes

        # if there are no nodes with the given attribute and value, return an empty list
        if val not in nodes:
            return []

        # if user set nosingleton to true, and there is only a single node with this value,
        # just return the node, rather than a singleton list
        if nosingleton and len(nodes[val]) == 1:
            return nodes[val][0]

        # otherwise, return all nodes with the attribute attr and the value val
        return nodes[val]

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
