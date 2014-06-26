#!/usr/bin/env python

import argparse
import pprint
import semanticnet as sn
import shodan
import sys

nodes = {}

def get_node(data, field):
    global nodes

    if field not in data:
        return None

    field_value = str(data[field])

    if field_value in nodes:
        node = nodes[field_value]
    else:
        node = graph.add_node({"label": field_value, "type": field})
        nodes[field_value] = node
    return node

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
    global nodes

    for match in search_results['matches']:
        ip_node = get_node(match, 'ip_str')
        asn_node = get_node(match, 'asn')
        port_node = get_node(match, 'port')
        title_node = get_node(match, 'title')

        if 'location' in match:
            if 'country_name' in match['location']:
                if match['location']['country_name'] in nodes:
                    country_node = nodes[match['location']['country_name']]
                else:
                    country_node = graph.add_node({"type": "country_name",
                        "label": match['location']['country_name'],
                        "depth": 0
                        }
                    )
                    nodes[match['location']['country_name']] = country_node
            else:
                country_node = None
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
