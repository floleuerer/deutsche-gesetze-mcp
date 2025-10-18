import re
import json
from typing import List, Optional, Dict, Any, Union
import urllib.request
from pathlib import Path

from typing import List, Dict, Optional
from rapidfuzz import process, fuzz
from config import settings

class LawNode:
    def __init__(
        self,
        node_type: str,
        id: Optional[str],
        name: Optional[str]
    ):
        self.node_type = node_type        # 'root', 'paragraph'
        self.id = id                      # e.g. '1', '7'
        self.name = name                  # title/name after number
        self.content_lines: List[str] = []

    def add_content_line(self, line: str):
        self.content_lines.append(line)

    def __repr__(self):
        return f"LawNode(type={self.node_type!r}, id={self.id!r}, name={self.name!r})"

class LawParser:
    """
    Simplified parser for German law texts in Markdown.
    
    - Extracts front-matter fields 'Title' and 'jurabk' into root.full_title and root.short_title
    - Focuses only on paragraph (§) parsing and absatz retrieval
    - Preserves paragraph names for better context
    - Maintains original text formatting including line breaks
    """
    HEADLINE_RE = re.compile(r'^(#{1,6})\s*(.+)$')
    PARAGRAPH_RE = re.compile(r'^§\s*(?P<number>[0-9A-Za-z]+[a-z]?)\s*(?P<name>.*)$')
    FRONTMATTER_BOUNDARY = re.compile(r'^---')
    FRONT_KEYVAL = re.compile(r'^(?P<key>\w+):\s*(?P<value>.+)$')
    ABSATZ_RE = re.compile(r'^$$(?P<number>\d+)$$')

    def __init__(self, markdown: str):
        # split lines
        lines = markdown.splitlines()
        fm_active = False
        fm_lines: List[str] = []
        body_start = 0
        
        # extract front-matter
        for i, line in enumerate(lines):
            if self.FRONTMATTER_BOUNDARY.match(line):
                if not fm_active:
                    fm_active = True
                else:
                    body_start = i + 1
                    break
            elif fm_active:
                fm_lines.append(line)
                
        # parse front-matter
        self.full_title = None
        self.short_title = None
        title_lines: List[str] = []
        current_key = None
        
        for line in fm_lines:
            m = self.FRONT_KEYVAL.match(line)
            if m:
                key = m.group('key').lower()
                val = m.group('value').strip()
                current_key = key
                if key == 'title':
                    title_lines = [val]
                elif key == 'jurabk':
                    self.short_title = val
            else:
                if current_key == 'title':
                    title_lines.append(line.strip())
        
        if title_lines:
            self.full_title = ' '.join(title_lines)
            
        # setup root and paragraphs dict
        self.root = LawNode('root', None, None)
        self.paragraphs: Dict[str, LawNode] = {}
        
        # parse body
        self._parse('\n'.join(lines[body_start:]))

    def _parse(self, text: str):
        current_para: Optional[LawNode] = None
        
        for line in text.splitlines():
            line = line.rstrip()
            if not line:
                # Preserve empty lines
                if current_para:
                    current_para.add_content_line("")
                continue
                
            m_head = self.HEADLINE_RE.match(line)
            if m_head:
                headline = m_head.group(2)
                
                # Check if it's a paragraph
                m_para = self.PARAGRAPH_RE.match(headline)
                if m_para:
                    num = m_para.group('number')
                    nam = m_para.group('name').strip() or None
                    node = LawNode('paragraph', num, nam)
                    self.paragraphs[num] = node
                    current_para = node
                    continue
                    
                # Skip other headings - we only care about paragraphs
                current_para = None
                continue
                
            # Add content to current paragraph if we have one
            if current_para:
                current_para.add_content_line(line)

    def get_paragraph(self, paragraph_id: str, absatz_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve paragraph content, optionally filtered to a specific absatz.
        
        Args:
            paragraph_id: The paragraph number as string
            absatz_id: Optional absatz number as string
            
        Returns:
            Dict containing paragraph info and content
        """
        if paragraph_id not in self.paragraphs:
            raise KeyError(f"Paragraph § {paragraph_id} not found")
            
        node = self.paragraphs[paragraph_id]
        result = {
            "paragraph": paragraph_id,
            "name": node.name,
        }
        
        # If no absatz specified, return the whole paragraph
        if not absatz_id:
            result["text"] = "\n".join(node.content_lines)
            return result
        
        # Extract the specific absatz
        result["absatz"] = absatz_id
        lines = node.content_lines
        found = False
        absatz_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this line starts with the target absatz
            if line.strip().startswith(f"({absatz_id})"):
                found = True
                # Extract text after the absatz marker
                marker_end = line.find(f"({absatz_id})") + len(f"({absatz_id})")
                first_line = line[marker_end:]
                absatz_lines.append(first_line)
                
                # Continue to collect lines until next absatz or end
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    # Check if we've reached the next absatz
                    if self.ABSATZ_RE.match(next_line.strip()):
                        break
                    absatz_lines.append(next_line)
                    j += 1
                break
            i += 1
        
        if not found:
            # Show what absatz markers are actually in the text
            detected_absatze = []
            for line in lines:
                m = self.ABSATZ_RE.match(line.strip())
                if m:
                    detected_absatze.append(m.group('number'))
            
            available = ", ".join(sorted(detected_absatze)) if detected_absatze else "none"
            raise KeyError(f"Absatz {absatz_id} not found in § {paragraph_id}. Available: {available}")
            
        # Preserve the original formatting with newlines
        result["text"] = "\n".join(absatz_lines)
        return result

class LawLibrary:
    """
    Manages multiple German law texts.
    
    Provides:
    - Loading laws from GitHub or URLs
    - Listing available laws as JSON
    - Retrieving paragraphs/absätze from specific laws in JSON format
    """
    
    def __init__(self):
        self.laws: Dict[str, LawParser] = {}
        

    def load_laws_from_folder(self, folder_path: Path):
        laws = list(Path(folder_path).glob('**/index.md'))
        for law in laws:
            loaded = self.load_law_from_file(law)

            if loaded:
                print(f'{loaded} - {len(self.laws[loaded.lower()].paragraphs)}')
            
        print(self.laws.keys())

    def _load_law_from_markdown(self, md_text: str) -> str:
        parser = LawParser(md_text)

        if len(parser.paragraphs) <= settings.min_paragraphs:
            return None
        
        if not parser.short_title:
            raise ValueError(f"Could not determine short title")
            
        self.laws[parser.short_title.lower()] = parser
        return parser.short_title

    def load_law_from_file(self, file_path: Path) -> str:
        """
        Load a law from a URL and return its short title.
        
        Args:
            url: URL to the law markdown file
            
        Returns:
            Short title (abbreviation) of the loaded law
        """
        md_text = file_path.read_text()
            
        return self._load_law_from_markdown(md_text)

    def load_law_from_url(self, url: str) -> str:
        """
        Load a law from a URL and return its short title.
        
        Args:
            url: URL to the law markdown file
            
        Returns:
            Short title (abbreviation) of the loaded law
        """
        with urllib.request.urlopen(url) as f:
            md_text = f.read().decode("utf-8")
            
        return self._load_law_from_markdown(md_text)
        
    def load_laws_from_github(self, codes: List[str]) -> List[str]:
        """
        Load multiple laws from the German Bundestag GitHub repository.
        
        Args:
            codes: List of law codes (e.g., ['bgb', 'hgb'])
            
        Returns:
            List of successfully loaded law codes
        """
        base_url = "https://raw.githubusercontent.com/bundestag/gesetze/refs/heads/master"
        loaded = []
        
        for code in codes:
            try:
                url = f"{base_url}/{code[0].lower()}/{code.lower()}/index.md"
                self.load_law_from_url(url)
                loaded.append(code)
            except Exception as e:
                print(f"Failed to load {code}: {str(e)}")
                
        return loaded
        
    def get_available_laws(self, search_string: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Return all available laws with their full titles in JSON format.
        If search_string is provided, returns only those laws whose titles closely match the search string.

        Args:
            search_string: Optional string to fuzzy-match against law titles.

        Returns:
            List of dicts containing law codes and full titles
        """
        # Prepare list of all laws
        all_laws = [
            {"code": code, "title": parser.full_title}
            for code, parser in self.laws.items()
        ]

        # If no search string is given, return all
        if not search_string:
            return all_laws

        # Use rapidfuzz to extract matches above a threshold

        # Extract matches
        matches = process.extract(
            search_string,
            self.laws.keys(),
            scorer=fuzz.QRatio,
            processor=lambda s: s.lower(),
            limit=50,
            score_cutoff=60
        )

        # Sort matches by descending score
        sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
        
        # Map to list of dicts
        matched_laws = [
            {
                "code": code,
                "title": self.laws[code].full_title,
                "similarity": score
            }
            for code, score, *_ in sorted_matches
        ]
        
        return matched_laws

    def get(self, law_code: str, paragraph_id: str, absatz_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve paragraph or absatz from a specific law in JSON format.
        
        Args:
            law_code: The abbreviation of the law (e.g., 'BGB', 'HGB')
            paragraph_id: The paragraph number
            absatz_id: Optional absatz number
            
        Returns:
            Dict containing law, paragraph info and text content
        """
        # Normalize the law code (uppercase) for consistency
        #law_code = law_code.upper()
        
        law_code_lower = law_code.lower()
        if law_code_lower not in self.laws:
            available = self.get_available_laws_json(law_code)
            raise KeyError(f"Law '{law_code}' not available. Available laws: {available}")
        
        law = self.laws[law_code_lower]
        result = law.get_paragraph(paragraph_id, absatz_id)
        result["law"] = law.short_title
        result["law_title"] = law.full_title
        result["url"] = f'https://www.gesetze-im-internet.de/{law.short_title.lower()}/__{paragraph_id}.html'
        
        return result
        
    def get_json(self, law_code: str, paragraph_id: str, absatz_id: Optional[str] = None) -> str:
        """
        Same as get() but returns a JSON string instead of a dict.
        
        Args:
            law_code: The abbreviation of the law
            paragraph_id: The paragraph number
            absatz_id: Optional absatz number
            
        Returns:
            JSON string representation of the result
        """
        return json.dumps(self.get(law_code, paragraph_id, absatz_id), ensure_ascii=False, indent=2)
        
    def get_available_laws_json(self, search_string: Optional[str] = None) -> str:
        """
        Return all available laws as a JSON string.
        
        Returns:
            JSON string representation of available laws
        """
        return json.dumps(self.get_available_laws(search_string=search_string), ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    # Create a law library
    library = LawLibrary()
    
    # Load multiple laws
    library.load_laws_from_github(['bgb', 'hgb', 'stgb'])
    
    # Display available laws in JSON format
    print("Available laws (JSON):")
    print(library.get_available_laws_json())
    
    # Example: Get paragraph from BGB in JSON format
    try:
        print("\nBGB § 1 (JSON):")
        print(library.get_json('BGB', '1'))
    except KeyError as e:
        print(f"Error: {str(e)}")
    
    # Example: Get specific absatz from HGB in JSON format
    try:
        print("\nHGB § 9b Absatz 4 (JSON):")
        print(library.get_json('HGB', '9b', '4'))
    except KeyError as e:
        print(f"Error: {str(e)}")
