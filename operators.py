import networkx as nx
import semanticnet as sn

def _extract_networkx_graph(G):
    mod = G.__module__.split('.')[0]
    if mod == 'semanticnet':
        return G.networkx_graph()
    elif mod == 'networkx':
        return G
    else:
        raise GraphException("Invalid graph object. Must be from networkx or semanticnet.")

def difference(A, B):
    '''Returns a new graph which contains the nodes and edges in A, but not in B.'''
    A = _extract_networkx_graph(A)
    B = _extract_networkx_graph(B)
    C = A.copy()
    C.remove_nodes_from(n for n in A.nodes() if n in B.nodes())
    C.remove_edges_from(
        (src, dst, key)
        for src, dst in A.edges()
        for key in A.edge[src][dst]
        if (src, dst) in B.edges()
            and key in B.edge[src][dst]
    )
    g = sn.Graph()
    g.load_networkx_graph(C)
    return g
