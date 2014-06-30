#!/usr/bin/env python

import csv
import os
import semanticnet as sn
import sys

class Contact(object):
    def __init__(self, name, email_domain, company, title):
        self.name = name
        self.email_domain = email_domain
        self.company = company
        self.title = title

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
        if key == "name":
            name_node = add_node(graph, {"label": val})
        else:
            nodes.append(add_node(graph, {"label": val}))

    # connect this contact's name node to every other node for this contact
    for node in nodes:
        graph.add_edge(name_node, node)

if __name__ == "__main__":
    
    if len(sys.argv) <= 1:
        print("Need a CSV file.")

    graph = sn.Graph()
    contact_list_filename = sys.argv[1]

    with open(contact_list_filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            contact = Contact(
                " ".join([row["First Name"], row["Last Name"]]),
                row["E-mail Address"].split("@")[1],
                row["Company"],
                row["Job Title"]
            )

            process_contact(graph, contact)

    path = os.path.dirname(os.path.abspath(contact_list_filename))
    file_ext = os.path.splitext(contact_list_filename)
    save_json_name = os.path.join(path, os.path.basename(file_ext[0]) + ".json")
    print("Writing results to {}".format(save_json_name))
    graph.save_json(save_json_name)
