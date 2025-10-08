# server_app.py
import os
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from serpapi import GoogleSearch

# Initialize FastMCP
mcp_server = FastMCP(name="YouTubeSearchMCP")

# Create a FastAPI instance manually (FastMCP doesn't expose .app)
app = FastAPI(title="YouTube Search MCP Server")

# Define a YouTube search schema
class YouTubeSearchInput(BaseModel):
    query: str
    max_results: int = 5

# Define MCP tool endpoint
@mcp_server.tool()
def youtube_search_tool(data: YouTubeSearchInput):
    """Search YouTube videos using SerpAPI"""
    params = {
        "engine": "youtube",
        "search_query": data.query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    videos = results.get("video_results", [])
    return videos[:data.max_results]

# ✅ Integrate FastMCP with FastAPI
app.include_router(mcp_server.router, prefix="/mcp")

# Root route for Render health check
@app.get("/")
def home():
    return {"status": "running", "service": "YouTubeSearchMCP"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
