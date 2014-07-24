#!/usr/bin/env python

import argparse
import csv
import semanticnet as sn
import math

def get_node(graph, id_, attrs):
    if graph.has_node(id_):
        return graph.get_node(id_)['id']
    return graph.add_node(attrs, id_=id_)

def process_csv_file(graph, filename):
    global max_amt
    with open(filename, 'rU') as f:
        reader = csv.DictReader(f, dialect="excel")
        for row in reader:
            acquirer = get_node(graph, row['Acquirer'], 
                {'type': 'acquirer', 'label': row['Acquirer'], 'depth': 0}
            )
            target = get_node(graph, row['Target'],
                {'type': 'target', 'label': row['Target']}
            )
            if 'Total Deal Amt.' in row and row['Total Deal Amt.'] != "":
                amt = row['Total Deal Amt.'][1:].replace(',', '')
                try:
                    amt = float(amt)
                    max_amt = max(amt, max_amt)
                    data = {"graphiti:space:activity": amt}
                except ValueError:
                    data = {}
            else:
                data = {}

            graph.add_edge(acquirer, target, data)

def scale_deal_amts(graph):
    global max_amt
    print("max_amt = {}".format(max_amt))
    for nid, attrs in graph.get_edges().iteritems():
        if 'graphiti:space:activity' in attrs:
            attrs['graphiti:space:activity'] = math.log(
                attrs['graphiti:space:activity'], max_amt
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser("merger.py")
    parser.add_argument('csv_file', type=str)
    args = parser.parse_args()

    global max_amt
    max_amt = 0

    g = sn.DiGraph()
    process_csv_file(g, args.csv_file)
    scale_deal_amts(g)
    g.save_json("mergers.json")
