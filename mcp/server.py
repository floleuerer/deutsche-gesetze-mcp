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

@mcp.tool()
def search_laws(query: str, laws: list[str] | None = None) -> str:
    """Fulltext search over all laws or a specific list of laws.
    
    Args:
        query: The search query (e.g. "Schadensersatz", "Kündigung").
        laws: Optional list of law codes to filter by (e.g. ["BGB", "HGB"]).
    """
    normalized_laws = None
    if laws:
        normalized_laws = []
        for law in laws:
            law_lower = law.strip().lower()
            if law_lower not in library.laws:
                available = library.get_available_laws_json(law)
                return f"Law '{law}' not available. Available laws: {available}"
            normalized_laws.append(law_lower)
            
    results = library.search(query, normalized_laws)
    return json.dumps(results, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")