# server.py
import nest_asyncio
nest_asyncio.apply()

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from youtubesearchpython import VideosSearch
import uvicorn

# --- Initialize FastAPI app ---
app = FastAPI(title="🎥 YouTube MCP Server")

# --- Initialize FastMCP server ---
mcp_server = FastMCP(app=app)

# --- Tool 1: YouTube Search ---
async def youtube_search(query: str):
    """Search YouTube for videos matching the given query."""
    try:
        search = VideosSearch(query, limit=5)
        results = search.result()['result']
        videos = [
            {
                "title": v['title'],
                "link": v['link'],
                "channel": v['channel']['name'],
                "published": v.get('publishedTime'),
                "views": v.get('viewCount', {}).get('text')
            }
            for v in results
        ]
        return {"query": query, "results": videos}
    except Exception as e:
        return {"error": str(e)}

# Register the tool with MCP
mcp_server.register_tool(
    youtube_search,
    name="youtube_search",
    description="Search YouTube for videos based on a text query."
)

# --- Root endpoint ---
@app.get("/")
async def home():
    return {"status": "✅ YouTube MCP Server is running!", "tools": ["youtube_search"]}

# --- Run the server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
