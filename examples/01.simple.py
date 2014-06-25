#!/usr/bin/python

import sys
import semanticnet as sn

graph = sn.Graph()

a = graph.add_node({"label" : "A"})
b = graph.add_node({"label" : "B"})
c = graph.add_node({"label" : "C"})

graph.add_edge(a, b, {"type" : "belongs"})
graph.add_edge(b, c, {"type" : "owns"})
graph.add_edge(c, a, {"type" : "has"})

graph.save_json("output.json")
