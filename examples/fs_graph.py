#!/usr/bin/env python

import sys
import os
import argparse
import semanticnet as sn

def add_node(graph, root, label, node_type):
    data = {}

    if os.path.islink(root):
        data['type'] = 'link'

    path = os.path.join(root, label)

    if not graph.has_node(path):
        graph.add_node({"type": node_type, "label": label}, path)

    graph.add_edge(root, path, data)

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Need a starting dir")
        sys.exit(-1)

    start = sys.argv[1]
    graph = sn.Graph()

    for root, dirs, files in os.walk(start, followlinks=True):
        print(root)

        if not graph.has_node(root):
            graph.add_node({'label': root, 'type': 'dir', 'depth': 0}, root)

        for d in dirs:
            add_node(graph, root, d, "dir")
        for f in files:
            add_node(graph, root, f, os.path.splitext(f)[1])

    graph.save_json("fs.json")

