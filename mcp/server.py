from mcp.server.fastmcp import FastMCP
from parser import LawLibrary
import json
from config import settings

mcp = FastMCP("deutsche-gesetze-mcp", stateless_http=True, host='0.0.0.0', port=8001, debug=True)

LAWS = []

library = LawLibrary()

# Load multiple laws
if settings.load_from_folder:
    library.load_laws_from_folder(settings.load_from_folder)
elif settings.load_from_github:
    library.load_laws_from_github(settings.load_from_github)
else:
    ValueError('No law source provided')


@mcp.tool()
def get_lawlibrary(law: str | None = None) -> str:
    """Get a list of available german laws. If `law` is provided, list 
    all laws with similar names."""
    if len(library.laws) > 50:
        return 'Es sind mehr als 50 Gesetze in der Datenbank. Um nach einem Gesetz zu suchen' \
                'übergebe ein Gesetzeskürzel (EStG, HGB, etc ...) als `law` Parameter.'
    
    laws = library.get_available_laws_json(law)
    laws = json.dumps(laws)
    return laws

@mcp.tool()
def get_paragraph(law: str, paragraph: str) -> str:
    """Get the content of a paragraph of a german law. 
    Example values:
    - law: BGB, HGB, SGB 5, etc ...
    - paragraph: 2, 14a, etc ...
    """
    text = library.get_json(law, paragraph)
    return text

print(mcp.__dict__)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")