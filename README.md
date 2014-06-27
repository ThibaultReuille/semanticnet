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
$ ./bro_graph.py ./http.log
Opening ./http.log
Building graph...
Writing results to ./http.json
cd /path/to/Visualization/graphiti
./graphiti demo /path/to/semanticnet/examples/http.json
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
py.test -v ./test/test_semanticnet.py
```
