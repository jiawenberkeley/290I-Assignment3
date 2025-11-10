from fastapi import FastAPI, UploadFile
import uvicorn
import json
import numpy as np
from graph import Graph
from node import Node
from dijkstra import dijkstra

app = FastAPI()

# global variable to hold the active graph
active_graph = None


@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def upload_graph(file: UploadFile):
    """
    Upload a JSON file containing an edge list to build the graph.
    Example JSON entry:
    {"source": "0", "target": "1", "weight": 1, "bidirectional": true}
    """
    global active_graph

    # Check file type
    if not file.filename.endswith(".json"):
        return {"Upload Error": "Invalid file type"}

    try:
        # Read and parse JSON file
        content = await file.read()
        edges = json.loads(content)
    except Exception as e:
        return {"Upload Error": f"Invalid JSON format: {str(e)}"}

    # Build the Graph
    G = Graph()
    for e in edges:
        src_id = str(e["source"])
        tgt_id = str(e["target"])
        w = float(e["weight"])
        bidir = bool(e.get("bidirectional", True))

        # Add nodes if not already in the graph
        if src_id not in G.nodes:
            G.add_node(Node(src_id))
        if tgt_id not in G.nodes:
            G.add_node(Node(tgt_id))

        # Add edge
        G.add_edge(G.nodes[src_id], G.nodes[tgt_id], w, bidirectional=bidir)

    active_graph = G
    return {
        "Upload Success": file.filename,
        "num_nodes": len(G.nodes),
        "num_edges": len(edges)
    }


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def solve_shortest_path(start_node_id: str, end_node_id: str):
    """
    Compute the shortest path between two node IDs using Dijkstra.
    """
    global active_graph

    if active_graph is None:
        return {"Solver Error": "No active graph uploaded"}

    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID"}

    # Reset distances before running Dijkstra
    for node in active_graph.nodes.values():
        node.dist = np.inf
        node.prev = None

    start_node = active_graph.nodes[start_node_id]
    end_node = active_graph.nodes[end_node_id]

    # Run Dijkstra algorithm
    dijkstra(active_graph, start_node)

    # Reconstruct shortest path
    path = []
    current = end_node
    while current is not None:
        path.insert(0, current.id)
        current = current.prev

    total_distance = float(end_node.dist)
    if total_distance == np.inf:
        return {"shortest_path": None, "total_distance": None}

    return {"shortest_path": path, "total_distance": total_distance}


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
