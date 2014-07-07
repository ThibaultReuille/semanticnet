semanticnet
============

semanticnet is a small python library to create semantic graphs in JSON.
Those created datasets can then be visualized with the 3D graph engine.

## JSON representation
When saving graph objects as JSON, the graph is represented internally as one might expect.
Suppose you have a graph G = (V, E), where

V = {0, 1, 2} and
E = {(0, 1), (0, 2), (1, 2)}

Suppose further that:

1. Vertex 0 has the attributes: `{"type": "A", "id": 0}`
2. Vertex 1 has the attributes: `{"type": "B", "id": 1}`
3. Vertex 2 has the attributes: `{"type": "C", "id": 2}`
4. Edge (0, 1) has the attributes: `{'src': 0, 'dst': 1, 'type': 'normal', 'id': 0}`
5. Edge (0, 2) has the attributes: `{'src': 0, 'dst': 2, 'type': 'normal', 'id': 1}`
6. Edge (1, 2) has the attributes: `{'src': 1, 'dst': 2, 'type': 'irregular', 'id': 1}`

then in JSON format, it would look like:

```json
{
 "timeline": [], 
 "nodes": [
  {
   "type": "A", 
   "id": 0
  }, 
  {
   "type": "B", 
   "id": 1
  }, 
  {
   "type": "C", 
   "id": 2
  }
 ], 
 "meta": {}, 
 "edges": [
  {
   "src": 0, 
   "dst": 1, 
   "type": "normal", 
   "id": 0
  }, 
  {
   "src": 0, 
   "dst": 2, 
   "type": "normal", 
   "id": 1
  }, 
  {
   "src": 1, 
   "dst": 2, 
   "type": "irregular", 
   "id": 2
  }
 ]
}
```

As you can see, there is a list of `"node"` objects, each of which contain the node's attributes and IDs,
as well as a list of `"edge"` objects, each of which have the edge's attributes, and the fields `"src"` and `"dst"`,
which indicate the source and destination vertices, respectively.

In actuality, the `"id"` fields will be [UUIDs](http://en.wikipedia.org/wiki/Globally_unique_identifier).

## Examples
Included in this repo are several example scripts to demonstrate usage of SemanticNet. These are the
instructions for running them.

### File system
To build a graph out of a portion of your file system, run the example script `fs_graph.py`:

```sh
./examples/fs_graph.py ~/src/python
```

This will build a tree out of your `~/src/python` folder save the file `fs.json` in your working directory.
(Obviously, you can change the argument path to any you would like to visualize; although, beware that if
it generates too many nodes, you will run into performance issues during the visualization).
Then, to run the visualizer with this data:

```sh
cd /path/to/Visualization/graphiti
./graphiti demo /path/to/semanticnet/fs.json
```

### Bro Logs
This example builds a graph from an HTTP Bro log. It makes these connections:

```
+----------+       +---------+                  
|          |       |         |                  
|  source  |       |  user   |                  
|    IP    +------->  agent  +----+   +--------+
|          |       |         |    |   |        |
+----------+       +---------+    +--->  host  |
                                  +--->        |
                   +----------+   |   |        |
                   |          |   |   +--------+
                   | referrer +---+             
                   |          |                 
                   +----------+                 
```

One example log is included, which was parsed from a packet capture on http://malware-traffic-analysis.net.

```sh
$ cd examples
$ ./bro_graph.py ./sample/http.log
Opening ./sample/http.log
Building graph...
Writing results to ./sample/http.json
cd /path/to/Visualization/graphiti
./graphiti demo /path/to/semanticnet/examples/sample/http.json
```

To build a graph from your own packet capture, you simply run `tcpdump` and parse it with `bro`:

```sh
$ tcpdump -i <your_network_interface> -w outfile.cap
tcpdump: listening on <your_network_interface>, link-type EN10MB (Ethernet), capture size 65535 bytes
^C307 packets captured
309 packets received by filter
0 packets dropped by kernel

$ bro -r outfile.cap

$ ./graphiti demo /path/to/generated/http.log
```

### Shodan
With this example, you can perform a search on the [Shodan](http://www.shodanhq.com/) API and visualize
the results. In this example script, these connections are made:

```
+---------+     +-------+            
|         |     |       |            
| country +-----+  ASN  |            
|         |     |       |            
+---------+     +---+---+            
                    |                
                    |                
                    |                
              +-----+-----+          
              |           |          
              |    IP     |          
              |  Address  |          
              |           |          
              +--+-----+--+          
                 |     |             
         +-------+     +--------+    
         |                      |    
         |                      |    
     +---+--+               +---+---+
     |      |               |       |
     | port |               | title |
     |      |               |       |
     +------+               +-------+
```

To run the script, use your Shodan API key, and provide a search string (the same you would
type into the search bar on Shodan's web page).

```sh
$ cd examples

$ ./shodan_graph.py -k <YOUR_API_KEY> -s "your search string"
Saving results to shodan_your_search_string.json

$ cd /path/to/Visualization/graphiti

$ ./graphiti demo /path/to/semanticnet/examples/shodan_your_search_string.json
```

## Caching
Should you come across a use case where you'd like quick references to nodes or edges by more than just the ID,
semanticnet provides a mechanism to cache nodes and edges by any of their attributes. For example, suppose you make
the following graph:

```python
>>> g = sn.Graph()
>>> a = g.add_node({"type": "server"}, '3caaa8c09148493dbdf02c574b95526c')
>>> b = g.add_node({"type": "server"}, '2cdfebf3bf9547f19f0412ccdfbe03b7')
>>> c = g.add_node({"type": "client"}, '3cd197c2cf5e42dc9ccd0c2adcaf4bc2')
>>> g.add_edge(a, b, {"method": "GET", "port": 80}, '5f5f44ec7c0144e29c5b7d513f92d9ab')
UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab')
>>> g.add_edge(a, c, {"method": "GET", "port": 80}, '7eb91be54d3746b89a61a282bcc207bb')
UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb')
>>> g.add_edge(b, c, {"method": "POST", "port": 443}, 'c172a3599b7d4ef3bbb688277276b763')
UUID('c172a359-9b7d-4ef3-bbb6-88277276b763')
```

Suppose further that you want to access the nodes by their `"type"` attribute. You can tell semanticnet to
cache the nodes by the `"type"` attribute, and access them like so:

```python
>>> g.cache_nodes_by("type")
>>> g.get_nodes_by_attr("type")
{'client': [{'type': 'client', 'id': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2')}], 'server': [{'type': 'server', 'id': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7')}, {'type': 'server', 'id': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c')}]}
```

Similarly, you could get a list of all connections by port:

```python
>>> g.cache_edges_by("port")
>>> g.get_edges_by_attr("port")
{80: [{'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'), 'method': 'GET'}, {'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'id': UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'), 'method': 'GET'}], 443: [{'port': 443, 'src': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('c172a359-9b7d-4ef3-bbb6-88277276b763'), 'method': 'POST'}]}
```

and you can specify the attribute value as well, to return the list of connections by, say, port 80:

```python
>>> g.get_edges_by_attr("port", 80)
[{'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('3cd197c2-cf5e-42dc-9ccd-0c2adcaf4bc2'), 'id': UUID('7eb91be5-4d37-46b8-9a61-a282bcc207bb'), 'method': 'GET'}, {'port': 80, 'src': UUID('3caaa8c0-9148-493d-bdf0-2c574b95526c'), 'dst': UUID('2cdfebf3-bf95-47f1-9f04-12ccdfbe03b7'), 'id': UUID('5f5f44ec-7c01-44e2-9c5b-7d513f92d9ab'), 'method': 'GET'}]
```

The cache is managed automatically. Any time you add or remove a node/edge with an attribute that you are
caching, or modify an attribute of a node/edge, semanticnet updates the cache.

## Installation

### Dependencies
The only dependency is networkx

Either do: `pip install networkx`

or: `pip install -r ./requirements.txt`

### Installation
#### Set your `$PYTHONPATH`
Be sure your `$PYTHONPATH` environment variable is set to the folder you keep all your
python modules in.

e.g., if you keep your Python modules in `~/src/python`, do:

```sh
export PYTHONPATH=.:$HOME/src/python
```

and restart your shell.

#### Download/Install
```sh
cd /path/to/your/python/modules
git clone https://github.com/ThibaultReuille/semantic-net.git semanticnet
```

#### Tests
If you wish to run the test suite, it uses `py.test`. Install it with:

```sh
pip install pytest
```

and run the tests with:

```sh
py.test -v ./test
```
