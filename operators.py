import semanticnet as sn

### Convenience lambdas ###
def node_in(nid, G):
    '''Returns true if the node n is in the graph G.'''
    # G = _extract_networkx_graph(G)
    return nid in G.get_node_ids()

def edge_in(eid, G):
    return eid in G.get_edge_ids()

### Operators
def _inter(A, B, node_cond, edge_cond):
    '''Generic internal helper for building a new graph, starting with the nodes in A
    and excluding members based on a condition on B.
    Generates and returns a new graph C = (V, E), where

    V = {v in V(A) | node_cond(v, B)}
    E = {e in E(A) | edge_cond(e, B)}

    '''
    C = A.copy()
    C.remove_nodes(n for n in C.get_node_ids() if not node_cond(n, B))
    C.remove_edges(e for e in C.get_edge_ids() if not edge_cond(e, B))
    return C

def difference(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges in A, but not in B.

    User may pass in a lambda which defines what it means for a node to be a
    member of the graph B. By default, it uses the node IDs. The lambda must
    be of the form:

    lambda node_id, new_graph: (expression which determines if node node_id is "in" new_graph)
    '''
    return _inter(A, B, lambda n, new_G: not node_is_member(n, new_G), lambda e, new_G: not edge_is_member(e, new_G))

def intersection(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges in both A and B.

    User may pass in a lambda which defines what it means for an edge to be a
    member of the graph B. By default, it uses the edge IDs. The lambda must
    be of the form:

    lambda edge_id, new_graph: (expression which determines if edge edge_id is "in" new_graph)
    '''
    return _inter(A, B, node_is_member, edge_is_member)
