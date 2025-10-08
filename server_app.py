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
# 4️⃣ Mount MCP Routes on FastAPI
# -----------------------------------------
# Some versions of fastmcp may not expose `router`
try:
    app.include_router(mcp_server.router, prefix="/mcp")
except AttributeError:
    # Manual fallback route for FastMCP tool
    @app.post("/mcp/youtube_search_tool")
    def youtube_search(data: YouTubeSearchInput):
        return youtube_search_tool(data)

# -----------------------------------------
# 5️⃣ MCP Compatibility Route: /mcp/run_tool
# -----------------------------------------
@app.post("/mcp/run_tool")
def run_tool(request: dict):
    """Generic endpoint to support Model Context Protocol clients"""
    tool = request.get("tool")
    args = request.get("args", {})

    if tool == "youtube_search_tool":
        data = YouTubeSearchInput(**args)
        return youtube_search_tool(data)
    else:
        return {"error": f"Unknown tool '{tool}'"}

# -----------------------------------------
# 6️⃣ Health Check Route
# -----------------------------------------
@app.get("/")
def home():
    return {
        "status": "running",
        "service": "YouTubeSearchMCP",
        "endpoints": ["/mcp/youtube_search_tool", "/mcp/run_tool"],
    }

# -----------------------------------------
# 7️⃣ Run the Server
# -----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
