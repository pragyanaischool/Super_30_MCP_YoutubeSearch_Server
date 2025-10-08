# server_app.py
import nest_asyncio
nest_asyncio.apply()

from mcp.server.fastmcp import FastMCP
from youtubesearchpython import VideosSearch
import uvicorn

# --- Initialize FastMCP ---
mcp_server = FastMCP()
app = mcp_server.app  # FastAPI app reference

# --- Define tool with decorator ---
@mcp_server.tool()
async def youtube_search(query: str):
    """Search YouTube videos for a given text query."""
    try:
        search = VideosSearch(query, limit=5)
        results = search.result().get("result", [])
        videos = [
            {
                "title": v["title"],
                "link": v["link"],
                "channel": v["channel"]["name"],
                "published": v.get("publishedTime"),
                "views": v.get("viewCount", {}).get("text"),
            }
            for v in results
        ]
        return {"query": query, "results": videos}
    except Exception as e:
        return {"error": str(e)}

# --- Optional: health check endpoint ---
@app.get("/")
async def root():
    return {"status": "✅ YouTube MCP Server running", "tools": ["youtube_search"]}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
