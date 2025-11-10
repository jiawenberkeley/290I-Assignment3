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

    # 3. Return success
    return {"Upload Success": file.filename}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph uploaded"}

    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID"}

    start_node = active_graph.nodes[start_node_id]
    end_node = active_graph.nodes[end_node_id]
    path, dist = get_shortest_path(active_graph, start_node, end_node)

    return {"shortest_path": path, "total_distance": dist}

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    