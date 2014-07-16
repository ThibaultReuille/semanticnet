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

def _clear_clutter(U):
    '''Clears up some clutter, so only relevant unchanged nodes/edges
    remain in the graph.
    '''
    same = [n for n, attrs in U.get_nodes().iteritems() if attrs['diffstatus'] == 'same']
    for n in same:
        # get the list of edges incident to or from this node
        successors = U._g.neighbors(n)
        predecessors = U._g.predecessors(n) if type(U) is sn.DiGraph else []
        edges = {}
        map(lambda adj: edges.update(U.get_edges_between(n, adj)), successors + predecessors)

        # a node is "relevant" if any of its incident edges has been changed, OR
        # it is connected to a changed node AND has an in-degree > 0
        changed = [
            # the edge itself has been changed, or
            attrs['diffstatus'] != 'same' or
                # it is connected to a changed node
                U.get_node_attribute(attrs['dst'], 'diffstatus') != 'same' or
                U.get_node_attribute(attrs['src'], 'diffstatus') != 'same'
            for e, attrs in edges.iteritems()
        ]
        if not any(changed):
            U.remove_node(n)

def _check_mods(A, B, AB, S):
    '''Check the 'same' graph for differences in attributes '''
    for nid, attrs in S.get_nodes().iteritems():
        if attrs != A.get_node(nid) or attrs != B.get_node(nid):
            AB.set_node_attribute(nid, 'diffstatus', 'modified')
    for eid, attrs in S.get_edges().iteritems():
        if attrs != A.get_edge(eid) or attrs != B.get_edge(eid):
            AB.set_edge_attribute(eid, 'diffstatus', 'modified')

def diff(A, B, context=False, mods=False):
    '''Given two graphs A and B, where it is generally assumed that B is a "newer" version of A,
    returns a new graph which captures information about which nodes and edges of A were
    removed, added, and remain the same in B.

    Specifically, it returns A ∪ B, such that:
    1. Nodes in A - B are given the "diffstatus" attribute "removed"
    2. Nodes in B - A are given the "diffstatus" attribute "added"
    3. Nodes in A ∩ B are given the "diffstatus" attribute "same"

    Notice that the union of 1 - 3 equals A ∪ B.

    The optional parameter context, when true, will prune the graph so that nodes/edges which are
    the same are only present in the diff graph if:
    1. An edge incident on/to/from it has been changed, or
    2. it is connected to a changed node.

    The optional parameter mods, when true, will check for attribute modifications on nodes and
    edges, in addition to new/removed nodes. Any nodes/edges that have had their attributes
    changed between A and B are marked with the "diffstatus" attribute as "modified."

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

    if mods:
        _check_mods(A, B, AB, same)

    if context:
        _clear_clutter(AB)

    return AB
