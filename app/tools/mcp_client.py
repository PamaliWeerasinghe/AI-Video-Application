import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
# LangChain provides adapters to convert MCP tools into standard LangChain tools
from langchain_mcp_adapters.tools import load_mcp_tools 

async def setup_mcp_and_agent():
    # 1. Define the connection to your local MCP server
    # For example, this could be an FFmpeg tool server or a local filesystem server
    server_params = StdioServerParameters(
        command="node",
        args=["/path/to/your/ffmpeg-mcp-server/index.js"]
    )

    # 2. Connect to the MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. Retrieve the available tools from the MCP server
            # and adapt them into LangChain-compatible tools
            mcp_tools = await load_mcp_tools(session)
            
            print(f"Loaded tools from MCP: {[t.name for t in mcp_tools]}")
            
            # 4. Bind the MCP tools to your LangChain LLM 
            llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
            
            # The agent can now autonomously use your local FFmpeg tools
            # without you having to write any custom LangChain @tool wrappers
            agent = create_react_agent(llm, tools=mcp_tools)
            
            return agent

# To run it:
# agent = asyncio.run(setup_mcp_and_agent())