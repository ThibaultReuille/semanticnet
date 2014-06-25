#!/usr/bin/env python
import csv
import os
import pprint
import re
import semanticnet as sn
import sys
import urlparse

delim_pattern = '(#separator.+)'
var_line_pattern = '(\#.+)'
var_pattern = '((?<=\#).+)'
nodes = {}

def log_delim(log):
    global delim_pattern
    delim_match = re.search(delim_pattern, log)
    if delim_match == None:
        print("No separator in log. Exiting.")
        sys.exit(-1)
    else:
        delim_line = delim_match.groups()[0]

    return delim_line.split(' ')[1].decode("string-escape")

def extract_vars(log):
    global var_pattern
    var_lines = [ line for line in re.findall(var_pattern, log) if re.match("^separator", line) == None ]
    vars_ = dict([ tuple(line.split(delim, 1)) for line in var_lines ])
    vars_['fields'] = vars_['fields'].split(delim)
    vars_['types'] = vars_['types'].split(delim)

    return vars_

def extract_data(fields, log, limit=0):
    data = {}
    global var_line_pattern
    data_lines_matches = re.subn(var_line_pattern + "\n", '', log)

    if data_lines_matches == None:
        return {}

    data_lines = data_lines_matches[0]
    data_lines = data_lines.split("\n")
    bro_reader = csv.DictReader(data_lines, fieldnames=fields, delimiter=delim)

    if limit == 0:
        limit = len(data_lines)
    
    # for row in bro_reader:
    num_rows = 0
    for row in bro_reader:
        if num_rows >= limit:
            break
        else:
            num_rows += 1

        if row['id.orig_h'] in data:
            data[row['id.orig_h']].append(row)
        else:
            data[row['id.orig_h']] = [ row ]

    return data

def print_data(data):
    for ip, ip_data in data.items():
        for item in ip_data:
            for key, val in item.items():
                print("{}: {}".format(key, val))
            print

def get_node(field, log_entry, label=""):
    global nodes

    if label == "":
        try:
            field_value = log_entry[field]
        except KeyError:
            return None

        if field_value == "-":
            return None
    else:
        field_value = label

    if field_value in nodes:
        node = nodes[field_value]
    else:
        node = graph.add_node({"label": field_value, "type": field})
        nodes[field_value] = node

    return node

def connect(graph, src, dst, attrs):
    edges = graph.get_edges_between(src, dst)

    if len(edges) != 0:
        combine_edge_id = None
        for id_, edge_attrs in edges.items():
            if all(item in edge_attrs.items() for item in attrs.items()):
                combine_edge_id = id_
                break
        if combine_edge_id != None:
            if "raindance:space:activity" in edges[combine_edge_id]:
                edges[combine_edge_id]["raindance:space:activity"] += .005
            else:
                edges[combine_edge_id]["raindance:space:activity"] = .005
        else:
            graph.add_edge(src, dst, attrs)
    else:
        graph.add_edge(src, dst, attrs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Need a capture file")
        sys.exit(-1)

    logfilename = sys.argv[1]
    print("Opening {}".format(logfilename))

    with open(logfilename) as logfile:
        log = logfile.read()

    print("Building graph...")

    delim = log_delim(log)
    vars_ = extract_vars(log)
    data = extract_data(vars_['fields'], log, 500)

    # print_data(data)

    graph = sn.DiGraph()
    global nodes

    for ip, items in data.items():
        nodes = {}
        for item in items:
            src_ip_node = get_node('id.orig_h', item)
            user_agent_node = get_node('user_agent', item)

            if src_ip_node == None or user_agent_node == None:
                continue

            connect(graph, src_ip_node, user_agent_node, {"type": "user_agent"})

            label = item['host'] + item['uri']
            ext = os.path.splitext(item['uri'])[1]
            host_node = get_node("host:{}".format(ext), item, label)

            if host_node == None:
                continue

            connect(graph, user_agent_node, host_node, {"type": item['method']})

            try:
                ref_url = item['referrer']
            except KeyError:
                continue

            if ref_url == "-":
                continue

            ref = urlparse.urlparse(ref_url)
            ref = ref.netloc + ref.path

            ref_node = get_node('referrer', item, ref)

            if ref_node == None:
                continue

            connect(graph, ref_node, host_node, {"type": "ref"})

    path = os.path.dirname(os.path.abspath(logfilename))
    file_ext = os.path.splitext(logfilename)
    save_json_name = os.path.join(path, os.path.basename(file_ext[0]) + ".json")
    print("Writing results to {}".format(save_json_name))
    graph.save_json(save_json_name)
