from mcp.server.fastmcp import FastMCP
import platform_tools
import vtune_wrapper
mcp = FastMCP("host info mcp")

mcp.add_tool(platform_tools.get_host_info)
mcp.add_tool(vtune_wrapper.run_hotspot_analysis)
# mcp.add_tool(vtune.run_memory_analysis)

def main():
    mcp.run("stdio") # sse


if __name__ == "__main__":
    main()
