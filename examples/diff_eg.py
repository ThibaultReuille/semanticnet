#!/usr/bin/env python

import json
import semanticnet as sn
import argparse
import sys
import os

def attr_to_id(j, attr):
    node_ids_to_attrs = {}
    for node in j['nodes']:
        if attr in node:
            node_ids_to_attrs[node['id']] = node[attr]
            node['id'] = node[attr]
        else:
            raise "attribute {} not in node {}".format(attr, node)
    for edge in j['edges']:
        edge['src'] = node_ids_to_attrs[edge['src']]
        edge['dst'] = node_ids_to_attrs[edge['dst']]
        edge['id'] = edge['src'] + "|" + edge['dst']

if __name__ == "__main__":
    parser = argparse.ArgumentParser("diff_eg")
    parser.add_argument('-a', '--attr', type=str,
        help="If you used an attribute to identify nodes and edges, pass the attribute here.")
    parser.add_argument('-o', '--outfile', type=str, help="Output file path")
    parser.add_argument('old_graph', type=str)
    parser.add_argument('new_graph', type=str)
    args = parser.parse_args()

    if not args.outfile:
        old_base = os.path.splitext(os.path.basename(args.old_graph))[0]
        new_base = os.path.splitext(os.path.basename(args.new_graph))[0]
        args.outfile = old_base + "-" + new_base + "-diff.json"

    if args.attr:
        a_obj = json.load(open(args.old_graph, 'r'))
        b_obj = json.load(open(args.new_graph, 'r'))
        print("Converting old graph...")
        attr_to_id(a_obj, args.attr)
        print("Converting new graph...")
        attr_to_id(b_obj, args.attr)
    else:
        a_obj = args.old_graph
        b_obj = args.new_graph

    A = sn.DiGraph()
    A.load_json(a_obj)
    B = sn.DiGraph()
    B.load_json(b_obj)
    print("Performing diff...\n")
    D = sn.diff(A, B)
    print("Nodes added: {}".format(len([n for n, attrs in D.get_nodes().items() if attrs['diffstatus'] == 'added'])))
    print("Nodes removed: {}".format(len([n for n, attrs in D.get_nodes().items() if attrs['diffstatus'] == 'removed'])))
    print("Edges added: {}".format(len([e for e, attrs in D.get_edges().items() if attrs['diffstatus'] == 'added'])))
    print("Edges removed: {}".format(len([e for e, attrs in D.get_edges().items() if attrs['diffstatus'] == 'removed'])))
    print("Writing results to {}".format(args.outfile))
    D.save_json(args.outfile)
