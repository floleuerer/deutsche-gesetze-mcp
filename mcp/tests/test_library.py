from parser import LawLibrary
from unittest.mock import patch
import json

def test_library_load(sample_law_markdown):
    with patch('parser.settings') as mock_settings:
        mock_settings.min_paragraphs = 1
        lib = LawLibrary()
        lib._load_law_from_markdown(sample_law_markdown)
        
        assert "testg" in lib.laws
        assert len(lib.laws) == 1
        assert lib.laws["testg"].full_title == "Test Law"

def test_library_search(sample_law_markdown):
    with patch('parser.settings') as mock_settings:
        mock_settings.min_paragraphs = 1
        lib = LawLibrary()
        lib._load_law_from_markdown(sample_law_markdown)
        
        # Test search
        results = lib.search("Scope")
        assert len(results) > 0
        assert results[0]["law"] == "testg"
        assert results[0]["paragraph"] == "1"
        assert results[0]["title"] == "Scope"

def test_get_available_laws(sample_law_markdown):
    with patch('parser.settings') as mock_settings:
        mock_settings.min_paragraphs = 1
        lib = LawLibrary()
        lib._load_law_from_markdown(sample_law_markdown)
        
        laws = lib.get_available_laws()
        assert len(laws) == 1
        assert laws[0]["code"] == "testg"
        assert laws[0]["title"] == "Test Law"

def test_get_json(sample_law_markdown):
    with patch('parser.settings') as mock_settings:
        mock_settings.min_paragraphs = 1
        lib = LawLibrary()
        lib._load_law_from_markdown(sample_law_markdown)
        
        json_str = lib.get_json("TestG", "1")
        data = json.loads(json_str)
        assert data["law"] == "TestG"
        assert data["paragraph"] == "1"
        assert "Scope" in data["name"]
