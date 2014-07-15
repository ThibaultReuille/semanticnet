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

class CacheMeta(object):
    def __init__(self, get_func, get_items_func, cache_func, cache):
        self.get_func = get_func
        self.get_items_func = get_items_func
        self.cache_func = cache_func
        self.cache = cache

class Graph(object):
    '''A simple Graph structure which lets you focus on the data.'''

    def __init__(self, verbose=False, json_file=""):
        self._g = nx.MultiGraph()
        self._edges = {}

        self._node_cache = {}
        self._edge_cache = {}
        self._cache_meta = {
            "node": CacheMeta(self.get_node, self.get_nodes, self._cache_node, self._node_cache),
            "edge": CacheMeta(self.get_edge, self.get_edges, self._cache_edge, self._edge_cache)
        }
        
        self.meta = {}
        self.timeline = []

        self.verbose = verbose
        self.attr_reserved = ["id", "src", "dst"]

        if json_file:
            self.load_json(json_file)

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

    def _cache_item(self, item_type, attr_name, attr_values):
        # if we have not cached anything by this attr before,
        # create an empty dict for it
        if attr_name not in self._cache_meta[item_type].cache:
            self._cache_meta[item_type].cache[attr] = {}

        # if we haven't seen this attr value before, make an empty list for it
        if attr_values[attr_name] not in self._cache_meta[item_type].cache[attr_name]:
            self._cache_meta[item_type].cache[attr_name][attr_values[attr_name]] = []

        # add it to the cache
        self._cache_meta[item_type].cache[attr_name][attr_values[attr_name]].append(attr_values)

    def _cache_node(self, attr, node):
        '''Cache a node in self._node_cache'''
        self._cache_item("node", attr, node)

    def _cache_edge(self, attr, edge):
        '''Cache an edge in self._edge_cache'''
        self._cache_item("edge", attr, edge)

    def _cache_new(self, item_type, attrs):
        for key in self._cache_meta[item_type].cache:
            if key in attrs:
                self._cache_meta[item_type].cache_func(key, attrs)

    def _cache_new_node(self, attrs):
        '''Checks a new node's attributes and caches it if we are caching by one or more
        of its attributes.'''
        self._cache_new("node", attrs)

    def _cache_new_edge(self, attrs):
        '''Checks a new edge's attributes and caches it if we are caching by one or more
        of its attributes.'''
        self._cache_new("edge", attrs)

    def _remove_item_from_cache(self, item_type, id_):
        item = self._cache_meta[item_type].get_func(id_)
        for attr, val in item.iteritems():
            try:
                self._cache_meta[item_type].cache[attr][val].remove(item)
            except KeyError:
                pass

    def _remove_node_from_cache(self, id_):
        '''Removes node id_ from all places it occurs in the cache, if anywhere.'''
        self._remove_item_from_cache("node", id_)

    def _remove_edge_from_cache(self, id_):
        '''Removes edge id_ from all places it occurs in the cache, if anywhere.'''
        self._remove_item_from_cache("edge", id_)

    def _update_item_cache(self, item_type, id_, attr_name):
        # if we are not caching by this attribute, there is nothing to do
        if attr_name not in self._cache_meta[item_type].cache:
            return

        # remove any nodes that are in the wrong place in the cache
        for key, nodes in self._cache_meta[item_type].cache[attr_name].items():
            for node in nodes:
                if key not in node:
                    self._cache_meta[item_type].cache[attr_name][key].remove(node)
                    break # should only happen once

        self._cache_meta[item_type].cache_func(attr_name, self._cache_meta[item_type].get_func(id_))

    def _update_node_cache(self, id_, attr_name):
        '''Update the cache for the given node with ID id_ and attribute attr_name

        IMPORTANT: Assumes that the attribute has already been set with the new value!
        '''
        self._update_item_cache("node", id_, attr_name)

    def _update_edge_cache(self, id_, attr_name):
        '''Update the cache for the given edge with ID id_ and attribute attr_name

        IMPORTANT: Assumes that the attribute has already been set with the new value!
        '''
        self._update_item_cache("edge", id_, attr_name)

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

    def add_nodes(self, nodes):
        '''Adds the nodes from the given parameter nodes, where nodes
        is EITHER:

        1. a dictionary that maps node IDs to attributes, e.g.:

        {
            uuid.UUID('3caaa8c09148493dbdf02c574b95526c'): {
                'type': "A"
            },
            uuid.UUID('2cdfebf3bf9547f19f0412ccdfbe03b7'): {
                'type': "B"
            },
            etc...
        }

        OR

        2. a list that contains the attributes of the nodes to add, e.g.

        [ {'type': "A"}, {'type': "B"} ]

        where with this option, the unique IDs will be generated automatically,
        and it will return a list of the IDs in the respective order given.
        '''
        if type(nodes) is dict:
            for id_, data in nodes.items():
                self.add_node(data, id_)
        elif type(nodes) is list:
            ids = []
            for data in nodes:
                ids.append(self.add_node(data))
            return ids

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

    def remove_nodes(self, ids):
        map(self.remove_node, ids)

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
            self._cache_new_edge(self._edges[id_])
            return id_
        else:
            raise GraphException("Node ID not found.")

    def add_edges(self, edges):
        '''Adds the edges in the parameter edges, where edges is EITHER:

        1. a list of triples of the form (src, dst, data) or (src, dst, data, id_),
        where src and dst are the IDs of the nodes,
        data is the dictionary of the edge's attributes,
        and id_ is the unique ID of the edge, e.g.:

        [ (<id of src>, <id of dst>, {'type': 'normal'}), etc... ] or
        [ (<id of src>, <id of dst>, {'type': 'normal'}, <unique ID of edge>), etc... ]

        The two different forms of tuples may be combined, if desired.

        OR

        2. a dictionary that maps edge IDs to their attributes, where attributes
        MUST contain at least the two attributes 'src' and 'dst', which are the
        unique IDs of the source and destination nodes, respectively.

        WARNING: If either 'src' or 'dst' is missing from an edge's attributes,
        it will be silently ignored!
        '''
        if type(edges) is list:
            for tup in edges:
                self.add_edge(*tup)
        elif type(edges) is dict:
            for id_, attrs in edges.items():
                try:
                    self.add_edge(attrs['src'], attrs['dst'], attrs, id_)
                except KeyError:
                    continue

    def remove_edge(self, id_):
        '''Removes edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            edge = self._edges[id_]
            self._g.remove_edge(edge["src"], edge["dst"], id_)
            self._remove_edge_from_cache(id_)
            del self._edges[id_]
        else:
            raise GraphException("Node ID not found.")

    def remove_edges(self, ids):
        map(self.remove_edge, ids)

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
        '''Returns a dict of all nodes in the graph, keyed by their unique ID.'''
        return dict([ (id_, self._g.node[id_]) for id_ in self._g.nodes() ])

    def get_node_ids(self):
        '''Returns a list of the IDs of all nodes in the graph.'''
        return self._g.nodes()

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

    def get_edge_ids(self):
        return [ id_ for id_ in self._edges ]

    def get_edge(self, id_):
        '''Returns edge id_.'''
        id_ = self._extract_id(id_)
        if id_ in self._edges:
            return self._edges[id_]
        else:
            raise GraphException('Node ID not found.')

    def get_edges_between(self, src, dst):
        '''Returns all edges between src and dst and between dst and src'''
        src = self._extract_id(src)
        dst = self._extract_id(dst)
        edges_src_dst = {}
        if self._g.has_node(src) and self._g.has_node(dst):
            if self._g.has_edge(src, dst):
                edges_src_dst = dict(edges_src_dst.items() + self._g.edge[src][dst].items())

            # for DiGraphs, add edges in the other direction too
            if type(self) is not Graph and self._g.has_edge(dst, src):
                edges_src_dst = dict(edges_src_dst.items() + self._g.edge[dst][src].items())

        return edges_src_dst

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
            self._update_edge_cache(id_, attr_name)
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

    def _cache_by(self, item_type, attr, build):
        # If we ARE already caching by this value, do nothing
        if attr in self._cache_meta[item_type].cache:
            return

        # If we ARE NOT not already caching by this value, initialize the dict for it.
        # This is also done in _cache_node/edge(), but this is needed for cases
        # where the user decides to start caching by an attribute, and they haven't
        # added any nodes/edges with that attribute yet
        if attr not in self._cache_meta[item_type].cache:
            self._cache_meta[item_type].cache[attr] = {}

        if not build:
            return

        for id_, item_attrs in self._cache_meta[item_type].get_items_func().items():
            if attr in item_attrs:
                self._cache_meta[item_type].cache_func(attr, item_attrs)

    def cache_nodes_by(self, attr, build=True):
        '''Tells SemanticNet to cache nodes by the given attribute attr.

        After a call to this method, nodes will be accessible by calls to the method get_node_by_attr().
        See the docs for that function for more detail.

        Optinally, if the user wishes to tell SemanticNet to start caching NEW nodes of type attr, but not
        to build a cache from the existing nodes, they may set the 'build' flag to False.
        '''
        self._cache_by("node", attr, build)

    def cache_edges_by(self, attr, build=True):
        '''Tells SemanticNet to cache edges by the given attribute attr.

        After a call to this method, edges will be accessible by calls to the method get_edges_by_attr().
        See the docs for that function for more detail.

        Optinally, if the user wishes to tell SemanticNet to start caching NEW edges of type attr, but not
        to build a cache from the existing edges, they may set the 'build' flag to False.
        '''
        self._cache_by("edge", attr, build)

    def _clear_item_cache(self, item_type, attr):
        if attr == "":
            for key, val in self._cache_meta[item_type].cache.items():
                del self._cache_meta[item_type].cache[key]
        elif attr in self._node_cache:
            self._cache_meta[item_type].cache[attr] = {}

    def clear_node_cache(self, attr=""):
        '''Delete the node cache. If attr is given, delete the cache for that attribute.'''
        self._clear_item_cache("node", attr)

    def clear_edge_cache(self, attr=""):
        '''Delete the edge cache. If attr is given, delete the cache for that attribute.'''
        self._clear_item_cache("edge", attr)

    def _get_items_by_attr(self, item_type, attr, val, nosingleton):
        items = self._cache_meta[item_type].cache.get(attr)

        # if the attribute doesn't exist, return an empty dict
        if items == None:
            return {}

        # if no value was specified for the attribute, return the whole dict
        # of items keyed by attr
        if val == None:
            return items

        # if there are no items with the given attribute and value, return an empty list
        if val not in items:
            return []

        # if user set nosingleton to true, and there is only a single node with this value,
        # just return the node, rather than a singleton list
        if nosingleton and len(items[val]) == 1:
            return items[val][0]

        # otherwise, return all nodes with the attribute attr and the value val
        return items[val]

    def get_nodes_by_attr(self, attr, val=None, nosingleton=False):
        '''Gets all nodes with the given attribute attr and value val.

        If val is not specified, returns a dict of all nodes, keyed by attr.

        If there are no nodes with the given attr or val, returns an empty list.

        Optionally, if the nosingleton parameter is set to True, and there is only one node in a list,
        the method will only return that single node, rather than a singleton list. This is useful,
        for instance, if the user knows all nodes with attributes of a certain type will be unique,
        and wishes to simply use attr as the node key.
        '''
        return self._get_items_by_attr("node", attr, val, nosingleton)

    def get_edges_by_attr(self, attr, val=None, nosingleton=False):
        '''Gets all edges with the given attribute attr and value val.

        If val is not specified, returns a dict of all edges, keyed by attr.

        If there are no edges with the given attr or val, returns an empty list.

        Optionally, if the nosingleton parameter is set to True, and there is only one edge in a list,
        the method will only return that single edge, rather than a singleton list. This is useful,
        for instance, if the user knows all edges with attributes of a certain type will be unique,
        and wishes to simply use attr as the edge key.
        '''
        return self._get_items_by_attr("edge", attr, val, nosingleton)

    def neighbors(self, id_):
        return dict([(nid, self.get_node(nid)) for nid in self._g.neighbors(id_)])

    def _get_export_id_str(self, id_):
        if id_.__class__.__name__ == "UUID":
            return id_.hex
        return id_

    def _hexify_attrs(self, attrs):
        for key, val in attrs.iteritems():
            if key in ['src', 'dst', 'id']:
                attrs[key] = self._get_export_id_str(attrs[key])
        return attrs

    def save_json(self, filename):
        '''Exports the graph to a JSON file for use in the Gaia visualizer.'''
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = [ dict(chain(self._g.node[id_].items(), {"id": self._get_export_id_str(id_)}.items())) for id_ in self._g.nodes() ]
            graph["edges"] = [
                dict(
                    chain(
                        self._g.edge[i][j][key].items(),
                        { "src": self._get_export_id_str(i), "dst": self._get_export_id_str(j), "id": self._get_export_id_str(key)}.items()
                    )
                )
                for i, j in self._g.edges()
                for key in self._g.edge[i][j]
            ]
            graph["timeline"] = [ [c.timecode, c.name, self._hexify_attrs( c.attributes )] for c in self.timeline ]
            json.dump(graph, outfile, indent=True)

    def load_json(self, j):
        '''Generates a graph from the given JSON file j. j may be the filename string, or a JSON object.'''
        if type(j) is str:
            jfile = open(j, 'r')
            graph = json.load(jfile)
        else:
            graph = j

        self.meta = graph["meta"]
        self.timeline = graph["timeline"]

        for node in graph["nodes"]:
            id_ = self._extract_id(node["id"])
            self.add_node(node, id_)

        for edge in graph["edges"]:
            src = self._extract_id(edge["src"])
            dst = self._extract_id(edge["dst"])
            id_ = self._extract_id(edge["id"]) if edge["id"] != None else self._create_uuid()
            self.add_edge(
                src,
                dst,
                dict([item for item in edge.items()
                        if (item[0] != "src" and item[0] != "dst" and item[0] != "id")] ),
                id_
            )
            self._g.edge[src][dst][id_]["id"] = id_

    def copy(self):
        return copy.deepcopy(self)

    def _check_key_presence(self, d, key, val):
        try:
            d[key]
        except KeyError:
            d[key] = val

    def networkx_graph(self):
        return copy.deepcopy(self._g)

    def load_networkx_graph(self, nxgraph):
        self._g = nxgraph

        # add id fields on nodes that don't have them
        for id_ in self._g.nodes():
            self._check_key_presence(self._g.node[id_], "id", id_)

        for src, dst in nxgraph.edges():
            for key in nxgraph.edge[src][dst]:
                attrs = nxgraph.edge[src][dst][key]
                self._edges[key] = attrs
                self._check_key_presence(self._edges[key], "id", key)
                self._check_key_presence(self._edges[key], "src", src)
                self._check_key_presence(self._edges[key], "dst", dst)

if __name__ == "__main__":
    print("Please import this module !")
