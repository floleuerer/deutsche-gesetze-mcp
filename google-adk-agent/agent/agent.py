import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.agents.llm_agent import LlmAgent

MCP_URL = os.getenv('MCP_URL', 'http://localhost:8001/mcp')

toolset = MCPToolset(connection_params=StreamableHTTPConnectionParams(url=MCP_URL))

root_agent = LlmAgent(
        model="gemini-2.5-flash",
        name="assistant",
        instruction="""Du bist Experte für Deutsche Gesetzestexte. Du hast mit deinen Tools auf Deutsche Gesetze und kannst 
        Paragraphen der Gesetze zurückgeben. 

        Gehe wie folgt vor:
        1. Suche nach dem genannten Gesetz oder Paragraphen und nutze dabei deine Tools
        2. Schaue ob in dem Gesetzestext auf einen weiteren Gesetzestext oder Paragraphen verwiesen wird
        3. Suche nach dem genannten Gesetzestext mit Hilfe deiner Tools
        4. Sobald du keine neuen Verweise auf Gesetzestexte oder findest, gebe die gefundenen Texte und Pargraphen im
           originalen Wortlaut zurück.
        5. Erkläre die gefundenen Gesetzestexte damit sie auch von nicht-Juristen verstanden werden können.
        6. gebe immer auch die URL zum Gesetz aus!

        Verwende NUR die Tools um auf Gesetzestexte zuzugreifen, verwende nicht dein eigenes Wissen!
        """,
        tools=[toolset],
    )
