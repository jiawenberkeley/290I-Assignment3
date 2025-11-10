from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph

    # 1. Check file type
    if not file.filename.endswith(".json"):
        return {"Upload Error": "Invalid file type"}

    # 2. Read file content
    content = await file.read()
    import json
    try:
        active_graph = json.loads(content)
    except json.JSONDecodeError:
        return {"Upload Error": "Invalid JSON format"}
    
    G = Graph()

    for e in edges:
        src_id = str(e["source"])
        tgt_id = str(e["target"])
        w = float(e["weight"])
        bidir = bool(e.get("bidirectional", True))

        # Add nodes if not exist
        if src_id not in G.nodes:
            G.add_node(Node(src_id))
        if tgt_id not in G.nodes:
            G.add_node(Node(tgt_id))

        # Add edge
        G.add_edge(G.nodes[src_id], G.nodes[tgt_id], w, bidirectional=bidir)

    active_graph = G

    # 3. Return success
    return {"Upload Success": file.filename}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
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

    # Run Dijkstra
    dijkstra(active_graph, start_node)

    # Reconstruct path
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
    