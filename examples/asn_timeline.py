#!/usr/bin/env python

# Currently not functional, due to Graphiti not accepting UUIDs.

import argparse
import semanticnet as sn

timeline_counter = 0
timeline_delta = 1000
timeline_delta_small = 500

def add_edges(bg, edges):
    global timeline_counter
    global timeline_delta_small
    bg.add_edges(edges) # add them to the bookkeeping graph
    # add an event for each edge
    for e, attrs in edges.iteritems():
        tg.add_event(timeline_counter, "graph:add_link", attrs)
        timeline_counter += timeline_delta_small

if __name__ == "__main__":
    global timeline_counter
    global timeline_delta
    global timeline_delta_small

    parser = argparse.ArgumentParser("asn_timeline")
    parser.add_argument('asn_graph', help="The JSON file of the ASN graph.")
    args = parser.parse_args()

    queue = {} # maps node IDs to their queue of edges
    g = sn.DiGraph(json_file=args.asn_graph) # the JSON graph
    bg = sn.DiGraph() # bookkeeping graph for tg
    tg = sn.DiGraph() # the timeline graph

    for nid, attrs in g.get_nodes().iteritems():
        bg.add_node(attrs, id_=attrs['id'])
        tg.add_event(timeline_counter, "graph:add_node", attrs)
        timeline_counter += timeline_delta
        for predecessor in g.predecessors(nid):
            if predecessor in queue:
                edges = dict([ ( eid, attrs ) for eid, attrs in g.get_edges_between(nid, predecessor).iteritems() if attrs['dst'] == nid ] )
                add_edges(bg, edges)
        for neighbor in g.neighbors(nid):
            # get all edges between this node and its neighbor
            edges = dict([ ( eid, attrs ) for eid, attrs in g.get_edges_between(nid, neighbor).iteritems() if attrs['src'] == nid ] )
            if neighbor in bg.get_node_ids():
                add_edges(bg, edges)
            else:
                queue[nid] = edges
    
    tg.save_json('timeline.json')

