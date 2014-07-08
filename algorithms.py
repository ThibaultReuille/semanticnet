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
    map(lambda eid: U.set_edge_attribute(eid, 'diffstatus', status), G.get_edges())

# I is the graph of nodes/edges which are in both A and B
def _check_changed_edges(A, B, AB, I):
    # Go through the remaining edges that haven't been marked with a 'diffstatus'.
    # These are edges that are incident on, to, or from two nodes which are in
    # both A and B
    for eid in [ eid for eid, attrs in AB.get_edges().iteritems() if 'diffstatus' not in attrs ]:
        # removed edges
        if eid in A.get_edges() and eid not in B.get_edges():
            AB.set_edge_attribute(eid, 'diffstatus', 'removed')
        # added edges
        elif eid in B.get_edges() and eid not in A.get_edges():
            AB.set_edge_attribute(eid, 'diffstatus', 'added')

def diff(A, B):
    '''Given two graphs A and B, where it is generally assumed that B is a "newer" version of A,
    returns a new graph which captures information about which nodes and edges of A were
    removed, added, and remain the same in B.

    Specifically, it returns A ∪ B, such that:
    1. Nodes in A - B are given the "diffstatus" attribute "removed"
    2. Nodes in B - A are given the "diffstatus" attribute "added"
    3. Nodes in A ∩ B are given the "diffstatus" attribute "same"

    Notice that the union of 1 - 3 equals A ∪ B.

    WARNING: Currently, this method only works if both A and B were generated with unique IDs in a
    deterministic fashion; i.e., two identical nodes are given the same ID at both points in time.
    This means that diff() will not work on graphs which were generated with automatic random UUIDs.
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
    _check_changed_edges(A, B, AB, same)

    return AB
