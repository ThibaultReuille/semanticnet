#!/usr/bin/env python

import argparse
import csv
import semanticnet as sn
import sys

def add_edge_ifn(graph, src, dst):
    # get the edges between src and dst
    edges = graph.get_edges_between(src, dst)
    # if there are no edges, add one and return it
    if not edges:
        return graph.add_edge(src, dst)
    # if there is, return the first edge's ID
    return edges.items()[0][0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser("ssv.py")
    parser.add_argument("input_filename", type=str)
    parser.add_argument("output_filename", type=str)
    args = parser.parse_args()

    g = sn.DiGraph()
    with open(args.input_filename, "rU") as infile:
        reader = csv.reader(infile, delimiter=' ')
        for row in reader:
            previous = None
            for elem in row:
                current = g.get_or_add_node(elem, {"label": elem})
                if previous != None:
                    add_edge_ifn(g, previous['id'], current['id'])
                previous = current

    g.save_json(args.output_filename)
