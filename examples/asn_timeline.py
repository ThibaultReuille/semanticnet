#!/usr/bin/env python

# Currently not functional, due to Graphiti not accepting UUIDs.

import argparse
import semanticnet as sn

def set_invisible(g):
    for nid in g.get_node_ids():
        g.set_node_attribute(nid, 'og:space:lod', 0.0 )
    for eid in g.get_edge_ids():
        g.set_edge_attribute(eid, 'og:space:lod', 0.0 )

def timeline_set_node_visible(g, nid):
    '''Add an event to set the node visible and increment counter.'''
    global timeline_counter
    global timeline_delta
    g.add_event(timeline_counter, "graph:set_node_attribute",
        {
            'id': nid,
            'name': 'og:space:lod',
            'type': 'float',
            'value': '1.0'
        }
    )
    g.set_node_attribute(nid, 'og:space:lod', 1.0)
    timeline_counter += timeline_delta

def timeline_set_edge_visible(g, eid):
    if edge_is_visible(g, eid):
        return

    global timeline_counter
    global timeline_delta_small
    g.add_event(timeline_counter, "graph:set_link_attribute",
        {
            'id': eid,
            'name': 'og:space:lod',
            'type': 'float',
            'value': '1.0'
        }
    )
    g.set_edge_attribute(eid, 'og:space:lod', 1.0)
    timeline_counter += timeline_delta_small

def node_is_visible(g, nid):
    return g.get_node_attribute(nid, 'og:space:lod') != 0.0

def edge_is_visible(g, eid):
    return g.get_edge_attribute(eid, 'og:space:lod') != 0.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser("asn_timeline")
    parser.add_argument('asn_graph', help="The JSON file of the ASN graph.")
    args = parser.parse_args()

    global timeline_counter
    global timeline_delta
    global timeline_delta_small

    timeline_counter = 100
    timeline_delta = 100
    timeline_delta_small = 50

    queue = {} # maps node IDs to their queue of edges
    g = sn.DiGraph(json_file=args.asn_graph) # the JSON graph
    set_invisible(g) # set the nodes/edges to invisible initially

    for nid, attrs in sorted(g.get_nodes().iteritems(), key=lambda n: n[1]['registration']
            if 'registration' in n[1] else n[1]['label']):
        timeline_set_node_visible(g, nid)
        if nid in queue:
            for eid in queue[nid]:
                timeline_set_edge_visible(g, eid)
            queue.pop(nid) # remove from the queue, once visible
        for neighbor in dict(g.neighbors(nid).items() + g.predecessors(nid).items()):
            # get all edges between this node and its neighbor
            edges = [ eid for eid, attrs in g.get_edges_between(nid, neighbor).iteritems() ]
            if node_is_visible(g, neighbor):
                for eid in edges:
                    timeline_set_edge_visible(g, eid)
            else:
                queue[neighbor] = edges
    
    set_invisible(g)
    g.save_json('timeline.json')

