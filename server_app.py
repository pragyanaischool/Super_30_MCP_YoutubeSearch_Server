import os
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from serpapi import GoogleSearch

# -----------------------------------------
# 1️⃣ Initialize MCP Server
# -----------------------------------------
mcp_server = FastMCP(name="YouTubeSearchMCP")

# -----------------------------------------
# 2️⃣ Input Schema
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
# 4️⃣ Start MCP Server
# -----------------------------------------
if __name__ == "__main__":
    mcp_server.start(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

