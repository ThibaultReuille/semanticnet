#!/usr/bin/env python

import argparse
import pprint
import semanticnet as sn
import shodan
import sys

def get_node(data, field):
    if field not in data:
        return None

    field_value = str(data[field])

    node = graph.get_nodes_by_attr("label", field_value, nosingleton=True)

    if not node:
        return graph.add_node({"label": field_value, "type": field})

    return node["id"]

def connect(graph, src, dst):
    if src != None and dst != None:
        graph.add_edge(src, dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('shodan_graph')
    parser.add_argument('-k', '--api-key', type=str, required=True)
    parser.add_argument('-s', '--search', type=str, required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    sho = shodan.Shodan(args.api_key)

    try:
        search_results = sho.search(args.search)
    except shodan.APIError, e:
        print("Error during request: {}".format(e))
        sys.exit(-1)

    if args.verbose:
        pprint.pprint(search_results)

    if not search_results['matches']:
        print("No search results.")
        sys.exit(0)

    graph = sn.Graph()
    graph.cache_nodes_by("label") # all labels will be unique

    for match in search_results['matches']:
        ip_node = get_node(match, 'ip_str')
        asn_node = get_node(match, 'asn')
        port_node = get_node(match, 'port')
        title_node = get_node(match, 'title')

        if 'location' in match and 'country_name' in match['location']:
            country_name = match['location']['country_name']
            country_node = graph.get_nodes_by_attr("label", country_name, nosingleton=True)
            if not country_node:
                country_node = graph.add_node({"type": "country_name",
                    "label": country_name,
                    "depth": 0
                })
            else:
                country_node = country_node["id"]
        else:
            country_node = None

        connect(graph, asn_node, country_node)
        connect(graph, ip_node, asn_node)
        connect(graph, ip_node, port_node)
        connect(graph, ip_node, title_node)

    postfix = args.search.replace(" ", "_")
    save_filename = "shodan_{}.json".format(postfix)
    print("Saving results to {}".format(save_filename))
    graph.save_json(save_filename)
