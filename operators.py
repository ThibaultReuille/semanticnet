import semanticnet as sn

### Convenience lambdas ###
def node_in(nid, G):
    '''Returns true if the node n is in the graph G.'''
    return G._g.has_node(nid)

def edge_in(eid, G):
    return eid in G.get_edges()

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

    User may pass in a lambda which defines what it means for an element (node or edge)
    to be a member of a graph. By default, it uses the unique IDs. The lambda must
    be of the form:

    lambda id_, G: (expression which determines if the element id_ is "in" the graph G)
    '''
    return _inter(A, B, lambda n, new_G: not node_is_member(n, new_G), lambda e, new_G: not edge_is_member(e, new_G))

def intersection(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges which are in BOTH A and B.

    User may pass in a lambda which defines what it means for an element (node or edge)
    to be a member of a graph. By default, it uses the unique IDs. The lambda must
    be of the form:

    lambda id_, G: (expression which determines if the element id_ is "in" the graph G)
    '''
    return _inter(A, B, node_is_member, edge_is_member)

def union(A, B, node_is_member=node_in, edge_is_member=edge_in):
    '''Returns a new graph which contains the nodes and edges in EITHER A or B.

    User may pass in a lambda which defines what it means for an element (node or edge)
    to be a member of a graph. By default, it uses the unique IDs. The lambda must
    be of the form:

    lambda id_, G: (expression which determines if the element id_ is "in" the graph G)
    '''
    # copy A and B, and combine all their nodes and edges based on ID first, to create
    # a universal set AB to use in building the union
    AB = B.copy()
    AB.add_nodes(dict((nid, attrs) for nid, attrs in A.get_nodes().iteritems() if nid not in AB.get_node_ids()))
    AB.add_edges(dict((eid, attrs) for eid, attrs in A.get_edges().iteritems() if eid not in AB.get_edges()))

    # then use the universal set AB to build the union, based on the lambdas
    C = type(AB)()
    C.add_nodes(
        dict(
            (nid, attrs)
            for nid, attrs in AB.get_nodes().items()
            if node_is_member(nid, A) or node_is_member(nid, B)
        )
    )
    C.add_edges(
        dict(
            (eid, attrs)
            for eid, attrs in AB.get_edges().items()
            if edge_is_member(eid, A) or edge_is_member(eid, B)
        )
    )
    return C
