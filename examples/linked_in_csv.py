#!/usr/bin/env python

import argparse
import csv
import os
import semanticnet as sn
import networkx as nx
import sys

class Contact(object):
    def __init__(self, name, company):
        self.name = name
        self.company = company
        # self.title = title

def add_node(graph, attrs):
    try:
        node = graph.get_node(attrs["label"])
    except KeyError:
        return graph.add_node(attrs, attrs["label"])

    return node["id"]

def process_contact(graph, contact):
    nodes = []
    
    # add all nodes
    for key, val in vars(contact).items():
        if val == "":
            continue
        if key == "name":
            name_node = add_node(graph, {"label": val, "type": key, "depth": 0})
        else:
            nodes.append(add_node(graph, {"label": val, "type": key}))

    # connect this contact's name node to every other node for this contact
    for node in nodes:
        graph.add_edge(name_node, node, id_="{}-{}".format(name_node, node))

def process_csv_file(graph, filename, limit):
    processed = 0
    with open(filename, 'rU') as f:
        reader = csv.DictReader(f, dialect="excel")
        for row in reader:
            contact = Contact(
                " ".join([row["First Name"], row["Last Name"]]),
                row["Company"]
                # row["Job Title"]
            )

            process_contact(graph, contact)

            processed += 1

            if limit > -1 and processed >= limit:
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser("linked_in_csv")
    parser.add_argument('-i', '--intersection', type=str,
        help='Take the intersection of the input graph with the graph given on this argument.')
    parser.add_argument('-l', '--limit', type=int, default=-1,
        help='Load only this many contacts from each CSV file.')
    parser.add_argument('contact_list_filename')
    args = parser.parse_args()

    graph = sn.Graph()

    process_csv_file(graph, args.contact_list_filename, args.limit)

    if args.intersection:
        ugraph = sn.Graph()
        process_csv_file(ugraph, args.intersection, args.limit)

        g1 = graph.networkx_graph()
        g2 = ugraph.networkx_graph()
        
        gi = g1.copy()
        gi.remove_nodes_from(n for n in g1.nodes() if n not in g2.nodes())
        gi.add_edges_from((src, dst) for src, dst in g2.edges() if src in g1.nodes() and dst in g1.nodes())

        # remove any remaining nodes that are not connected to anything
        for id_ in gi.nodes():
            if gi.degree(id_) <= 0:
                gi.remove_node(id_)

        graph = sn.Graph()
        graph.load_networkx_graph(gi)

    path = os.path.dirname(os.path.abspath(args.contact_list_filename))
    file_ext = os.path.splitext(args.contact_list_filename)
    save_json_name = os.path.join(path, os.path.basename(file_ext[0]) + ".json")
    print("Writing results to {}".format(save_json_name))
    graph.save_json(save_json_name)
