#!/usr/bin/env python

import sys
import os
import argparse
import semanticnet as sn

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Need a starting dir")
        sys.exit(-1)

    start = sys.argv[1]

    nodesByName = {}
    graph = sn.Graph()
    cur = graph.add_node({"label": start, "type": "dir", "depth": 0})
    nodesByName[start] = cur

    def add_node(root, label, node_type):
        data = {}
        node = None
        path = ""

        if os.path.islink(root):
            data = {"type": "link"}
            root = os.path.realpath(root)

        path = os.path.join(root, label)

        if path in nodesByName:
            node = nodesByName[path]
        else:
            node = graph.add_node({"type": node_type, "label": label})
            nodesByName[path] = node

        graph.add_edge(cur, node, data)

    for root, dirs, files in os.walk(start, followlinks=True):
        print(root)

        if root in nodesByName:
            cur = nodesByName[root] 
        else:    
            cur = graph.add_node({"label": root, "type": "dir"})
            nodesByName[root] = cur

        for d in dirs:
            add_node(root, d, "dir")
        for f in files:
            add_node(root, f, os.path.splitext(f)[1])

    graph.save_json("fs.json")
