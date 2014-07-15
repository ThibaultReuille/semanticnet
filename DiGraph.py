import networkx as nx
from semanticnet import Graph

class DiGraph(Graph):

    def __init__(self, verbose=False, json_file=""):
        # don't pass in json_file so it doesn't call load_json() twice
        super(DiGraph, self).__init__(verbose, "")
        self._g = nx.MultiDiGraph()
        if json_file:
            self.load_json(json_file)

    def remove_node(self, id_):
        '''Removes node id_.'''
        id_ = self._extract_id(id_)
        if self._g.has_node(id_):
            # for DiGraph, remove predecessors AND successors
            for successor in self._g.successors(id_):
                # need to iterate over items() (which copies the dict) because we are
                # removing items from the edges dict as we are iterating over it
                for edge in self._g.edge[id_][successor].items():
                    self.remove_edge(self._g.edge[id_][successor][edge[0]]["id"]) # edge[0] is the edge's ID
            for predecessor in self._g.predecessors(id_):
                for edge in self._g.edge[predecessor][id_].items():
                    self.remove_edge(self._g.edge[predecessor][id_][edge[0]]["id"])

            self._remove_node_from_cache(id_)
            self._g.remove_node(id_)
        else:
            raise GraphException("Node ID not found.")

    def predecessors(self, id_):
        return dict([(nid, self.get_node(nid)) for nid in self._g.predecessors(id_)])

