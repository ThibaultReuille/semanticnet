import json

class GraphException(Exception):
    """Generic Semantic Graph Exception"""
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class Node(object):
    def __init__(self, id, data):
      self.id = id
      self.data = data

class Edge(object):
    def __init__(self, id, src, dst, data):
      self.id = id
      self.src = src
      self.dst = dst
      self.data = data

class Graph(object):

    def __init__(self, verbose=False):
        self.meta = dict()
        self.nodes = list()
        self.last_node_id = -1
        self.edges = list()
        self.last_edge_id = -1
        self.verbose = verbose

    def log(self, line):
        if self.verbose:
            print("[SemanticNet] " + line)

    def create_node_uid(self):
        self.last_node_id += 1
        return self.last_node_id

    def create_edge_uid(self):
        self.last_edge_id += 1
        return self.last_edge_id

    def node_id_exists(self, id):
        search = [n for n in self.nodes if n.id == id]
        if len(search) == 0:
            return False
        elif len(search) == 1:
            return True
        else:
            raise GraphException("Node id '" + str(id) + "' isn't unique.")

    def add_node(self, data):   
        id = self.create_node_uid()
        self.log("add_node " + str(data) + " = " + str(id)) 
        self.nodes.append(Node(id, data))
        return id

    def add_edge(self, src, dst, data = None):
        if self.node_id_exists(src) and self.node_id_exists(dst):
            id = self.create_edge_uid()
            self.log("add_edge " + str(src) + ", " + str(dst) + ", " + str(data) + " = " + str(id))
            self.edges.append(Edge(id, src, dst, data))
            return id
        else:
            raise GraphException("Node ID not found, can't create edge.")

    def set_node_attribute(self, id, name, value):
        search = [i for i in range(len(self.nodes)) if self.nodes[i].id == id]
        if len(search) == 0:
            raise GraphException("Node id '" + str(id) + "' not found!")
        elif len(search) == 1:
            self.nodes[search[0]].data[name] = value
        else:
            raise GraphException("Node id '" + str(id) + "' isn't unique.")

    def get_node_attribute(self, id, name):
        search = [n for n in self.nodes if n.id == id]
        if len(search) == 0:
            raise GraphException("Node id '" + str(id) + "' not found!")
        elif len(search) == 1:
            if name in search[0].data:
                return search[0].data[name]
            else:
                return None
        else:
            raise GraphException("Node id '" + str(id) + "' isn't unique.")

    def set_edge_attribute(self, id, name, value):
        search = [i for i in range(len(self.edges)) if self.edges[i].id == id]
        if len(search) == 0:
            raise GraphException("Edge id '" + str(id) + "' not found!")
        elif len(search) == 1:
            self.edges[search[0]].data[name] = value
        else:
            raise GraphException("Edge id '" + str(id) + "' isn't unique.")

    def get_edge_attribute(self, id, name):
        search = [e for e in self.edges if e.id == id]
        if len(search) == 0:
            raise GraphException("Edge id '" + str(id) + "' not found!")
        elif len(search) == 1:
            if name in search[0].data:
                return search[0].data[name]
            else:
                return None
        else:
            raise GraphException("Edge id '" + str(id) + "' isn't unique.")

    def save_json(self, filename):
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = [ n.__dict__ for n in self.nodes ]
            graph["edges"] = [ e.__dict__ for e in self.edges ]
            json.dump(graph, outfile)

    def load_json(self, filename):
        with open(filename, 'r') as infile:
            graph = json.load(infile)
            self.meta = graph["meta"]
            self.nodes = graph["nodes"]
            self.edges = graph["edges"]

            self.last_node_id = max(n.id for n in self.nodes)
            self.last_edge_id = max(e.id for e in self.edges)

    def save_gaia_json(self, filename):
        with open(filename, 'w') as outfile:
            graph = dict()
            graph["meta"] = self.meta
            graph["nodes"] = list()
            for n in self.nodes:
                node = { "id" : n.id }
                if n.data is not None:
                    node.update(n.data)
                graph["nodes"].append(node)
            graph["edges"] = list()
            for e in self.edges:
                edge = { "id" : e.id, "src" : e.src, "dst" : e.dst }
                if e.data is not None:
                    edge.update(e.data)
                graph["edges"].append(edge)
            json.dump(graph, outfile, indent=True)

    def load_gaia_json(self, filename):
        with open(filename, 'r') as infile:
            jdata = json.load(infile)
            self.meta = jdata["meta"]

            for n in jdata["nodes"]:
                id = n["id"]
                del n["id"]
                data = n
                self.nodes.append(Node(id, data))

                if id > self.last_node_id:
                    self.last_node_id = id

            for e in jdata["edges"]:
                id = e["id"]
                del e["id"]
                src = e["src"]
                del e["src"]
                dst = e["dst"]
                del e["dst"]
                data = e
                self.edges.append(Edge(id, src, dst, data))

                if id > self.last_edge_id:
                    self.last_edge_id = id

class Algorithms(object):

    def __init_(self):
        pass

    def diff(self, g1, g2):
        pass

if __name__ == "__main__":
    print("Please import this module !")
