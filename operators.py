import networkx as nx
import semanticnet as sn

def difference(A, B):
    '''Returns a new graph which contains the nodes and edges in A, but not in B.'''
    A = A.networkx_graph()
    B = B.networkx_graph()
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
