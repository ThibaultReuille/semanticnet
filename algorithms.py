# coding=utf-8
import semanticnet as sn

def _mark_incident_edges_as(U, G, status):
    for nid in G.get_node_ids():
        # for every successor of the removed node rnid
        for neighbor in U._g.neighbors(nid):
            edges_nid_neighbor = [eid for eid, attrs in U.get_edges_between(nid, neighbor).items()]
            map(lambda reid: U.set_edge_attribute(reid, 'diffstatus', status), edges_nid_neighbor)
        if type(U) is sn.DiGraph:
            for predecessor in U._g.predecessors(nid):
                edges_predecessor_nid = [eid for eid, attrs in U.get_edges_between(nid, predecessor).items()]
                map(lambda reid: U.set_edge_attribute(reid, 'diffstatus', status), edges_predecessor_nid)

def _mark_nodes_edges_as(U, G, status):
    map(lambda nid: U.set_node_attribute(nid, 'diffstatus', status), G.get_node_ids())
    map(lambda eid: U.set_edge_attribute(eid, 'diffstatus', status), G.get_edge_ids())

def diff(A, B):
    '''Given two graphs A and B, where it is generally assumed that B is a "newer" version of A,
    returns a new graph which captures information about which nodes and edges of A were
    removed, added, and remain the same in B.

    Specifically, it returns A ∪ B, such that:
    1. Nodes in A - B marked with the "diffstatus" attribute as "removed"
    2. Nodes in B - A marked with the "diffstatus" attribute as "added"
    3. Nodes in A ∩ B marked with the "diffstatus" attribute as "same"

    Notice that the union of 1 - 3 equals A ∪ B.

    '''
    # must take their union first, then mark appropriate nodes/edges
    AB = sn.union(A, B)

    # any edges incident on, to, or from the removed nodes will not be in the removed graph,
    # since we cannot have edges incident on, to, or from non-existent nodes
    removed = sn.difference(A, B)
    _mark_nodes_edges_as(AB, removed, 'removed')
    _mark_incident_edges_as(AB, removed, 'removed')

    added = sn.difference(B, A)
    _mark_nodes_edges_as(AB, added, 'added')
    _mark_incident_edges_as(AB, added, 'added')

    same = sn.intersection(B, A)
    _mark_nodes_edges_as(AB, same, 'same')

    return AB
