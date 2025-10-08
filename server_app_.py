import os
from fastapi import FastAPI
from pydantic import BaseModel
from serpapi import GoogleSearch
from mcp.server.fastmcp import FastMCP

# -----------------------------------------
# 1️⃣ Initialize FastAPI and FastMCP
# -----------------------------------------
app = FastAPI(title="YouTube Search MCP Server")
mcp_server = FastMCP(name="YouTubeSearchMCP")

# -----------------------------------------
# 2️⃣ Define Input Schema
# -----------------------------------------
class YouTubeSearchInput(BaseModel):
    query: str
    max_results: int = 5

# -----------------------------------------
# 3️⃣ Define MCP Tool
# -----------------------------------------
@mcp_server.tool()
def youtube_search_tool(data: YouTubeSearchInput):
    """Search YouTube videos using SerpAPI"""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "Missing SERPAPI_API_KEY"}

    params = {
        "engine": "youtube",
        "search_query": data.query,
        "api_key": api_key,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    videos = results.get("video_results", [])
    return videos[:data.max_results]

# -----------------------------------------
# 4️⃣ Mount MCP routes on FastAPI
# -----------------------------------------
# New versions expose router via `mcp_server.router`
try:
    app.include_router(mcp_server.router, prefix="/mcp")
except AttributeError:
    # If `.router` not available, fallback manual route
    @app.post("/mcp/youtube_search")
    def youtube_search(data: YouTubeSearchInput):
        return youtube_search_tool(data)

# -----------------------------------------
# 5️⃣ Health check route
# -----------------------------------------
@app.get("/")
def home():
    return {"status": "running", "service": "YouTubeSearchMCP"}

# -----------------------------------------
# 6️⃣ Run Server
# -----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
