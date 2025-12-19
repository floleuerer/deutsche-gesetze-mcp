from parser import LawParser

def test_parser_init(sample_law_markdown):
    parser = LawParser(sample_law_markdown)
    assert parser.short_title == "TestG"
    assert parser.full_title == "Test Law"
    assert len(parser.paragraphs) == 2
    assert "1" in parser.paragraphs
    assert "2" in parser.paragraphs

def test_get_paragraph_whole(sample_law_markdown):
    parser = LawParser(sample_law_markdown)
    result = parser.get_paragraph("1")
    assert result["paragraph"] == "1"
    assert result["name"] == "Scope"
    assert "This is the first paragraph." in result["text"]
    assert "It has multiple lines." in result["text"]

def test_get_paragraph_not_found(sample_law_markdown):
    parser = LawParser(sample_law_markdown)
    try:
        parser.get_paragraph("999")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass