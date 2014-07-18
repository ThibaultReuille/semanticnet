#!/usr/bin/env python
import argparse
import json
import os
import semanticnet as sn

def add_node(g, nid, attrs={}):
    try:
        return g.get_node(nid)['id']
    except KeyError:
        return g.add_node(attrs, id_=nid)

def add_edge(g, src, dst, attrs={}):
    edges = g.get_edges_between(src, dst)
    if edges:
        return edges.items()[0][0]

    return g.add_edge(src, dst, attrs)

def load_action(a, g):
    actions = []
    for action_type, data in a.iteritems():
        variety = data.get('variety')
        if variety != None:
            for v in variety:
                actions.append(add_node(g, v, {'label': v, 'type': 'action'}))
    return actions

def load_asset(a, g):
    assets = []
    for asset in a:
        variety = asset.get('variety')
        if variety != None:
            assets.append(add_node(g, variety, {'label': variety, 'type': 'asset'}))
    return assets

def connect_items(g, list1, list2, attrs={}):
    for item1 in list1:
        for item2 in list2:
            add_edge(g, item1, item2, attrs)
    for item2 in list2:
        for item1 in list1:
            add_edge(g, item1, item2, attrs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("vcdb.py")
    parser.add_argument("-i", "--input", type=str)
    args = parser.parse_args()

    vcdb_dir = os.environ['VCDB_DATA']
    g = sn.Graph()
    files = []
    if args.input:
        files.append(args.input)
    else:
        files = [ os.path.join(vcdb_dir, f) for f in os.listdir(vcdb_dir) if os.path.splitext(f)[1] == '.json' ]

    if len(files) > 100:
        files = files[:100]
    
    for f in files:
        j = json.load(open(f, 'r'))
        actions = load_action(j['action'], g)
        assets = load_asset(j['asset']['assets'], g)
        try:
            victim = add_node(g, j['victim']['victim_id'], {'label': j['victim']['victim_id'], 'type': 'victim', 'depth': 0})
        except KeyError:
            victim = None

        #import pprint
        #pprint.pprint("actions")
        #pprint.pprint(actions)
        #pprint.pprint("assets")
        #pprint.pprint(assets)
        #pprint.pprint("victim")
        #pprint.pprint(victim)

        connect_items(g, assets, actions)

        if victim != None:
            for asset in assets:
                add_edge(g, victim, asset)
            for action in actions:
                add_edge(g, victim, action)

    g.save_json("vcdb.json")

