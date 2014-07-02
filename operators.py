import semanticnet as sn

### Convenience lambdas ###
def node_in(nid, G):
    '''Returns true if the node n is in the graph G.'''
    # G = _extract_networkx_graph(G)
    return nid in G.get_node_ids()

def edge_in(eid, G):
    return eid in G.get_edge_ids()

### Operators
def difference(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges in A, but not in B.'''
    C = A.copy()
    C.remove_nodes(n for n in C.get_node_ids() if node_is_member(n, B))
    C.remove_edges(e for e in C.get_edge_ids() if edge_is_member(e, B))
    return C

def intersection(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges in both A and B.'''
    C = A.copy()
    C.remove_nodes(n for n in C.get_node_ids() if not node_is_member(n, B))
    C.remove_edges(e for e in C.get_edge_ids() if not edge_is_member(e, B))
    return C
