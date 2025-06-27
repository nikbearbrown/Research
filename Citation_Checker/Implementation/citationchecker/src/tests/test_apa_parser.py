import json
import os
import pytest
from src.parsers.apa_parser import APACitationParser

# Load test data
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(current_dir, "test_data", "apa_citations.json")

with open(test_data_path, 'r') as f:
    test_data = json.load(f)

class TestAPAParser:
    """Test suite for the APA citation parser."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        self.parser = APACitationParser()
    
    @pytest.mark.parametrize("citation_data", test_data["citations"])
    def test_parse_citation(self, citation_data):
        """Test the parse method with various APA citations."""
        # Parse the citation text
        citation = self.parser.parse(citation_data["text"])
        
        # Check that parsing succeeded
        assert citation is not None, f"Failed to parse: {citation_data['text']}"
        
        # Check basic fields match expected values
        expected = citation_data["expected"]
        
        # Test author parsing - check that all expected authors are present
        for expected_author in expected["authors"]:
            assert expected_author in citation.authors, f"Missing author: {expected_author}"
        assert len(citation.authors) == len(expected["authors"]), f"Author count mismatch: {len(citation.authors)} != {len(expected['authors'])}"
        
        # Test year parsing
        assert citation.year == expected["year"], f"Year mismatch: {citation.year} != {expected['year']}"
        
        # Test title parsing - be more flexible with case and punctuation
        assert expected["title"].lower() in citation.title.lower(), f"Title mismatch: {citation.title}"
        
        # Test source parsing
        assert expected["source"] in citation.source, f"Source mismatch: {citation.source}"
        
        # Test optional fields if present in expected data
        if "volume" in expected:
            assert citation.volume == expected["volume"], f"Volume mismatch: {citation.volume}"
        
        if "issue" in expected:
            assert citation.issue == expected["issue"], f"Issue mismatch: {citation.issue}"
        
        if "pages" in expected:
            assert citation.pages == expected["pages"], f"Pages mismatch: {citation.pages}"
        
        if "doi" in expected:
            assert citation.doi == expected["doi"], f"DOI mismatch: {citation.doi}"
        
        # Verify the confidence score is reasonable
        assert citation.confidence_score > 0.7, f"Low confidence score: {citation.confidence_score}"
    
    def test_extraction_from_text(self):
        """Test extracting citations from a larger text."""
        # Get the mixed text from test data
        text = test_data["mixed_text"]
        
        # Extract citations
        citations = self.parser.extract_citations(text)
        
        # Check we found at least 2 citations
        assert len(citations) >= 2, f"Expected at least 2 citations, found {len(citations)}"
        
        # Check that the first citation matches our expected data
        assert "Smith" in citations[0].authors[0], "First author should be Smith"
        assert citations[0].year == 2020, "Year should be 2020"
        
        # Check the second citation
        assert "Brown" in citations[1].authors[0], "Second citation author should be Brown"
        assert citations[1].year == 2019, "Second citation year should be 2019"
        
    def test_confidence_calculation(self):
        """Test the confidence score calculation."""
        # Create a complete citation
        complete_citation = self.parser.parse(test_data["citations"][0]["text"])
        assert complete_citation.confidence_score > 0.9, "Complete citation should have high confidence"
        
        # Create a partial citation
        partial_text = "Smith, J. (2020). Some paper. Journal."
        partial_citation = self.parser.parse(partial_text)
        assert partial_citation is not None, "Failed to parse partial citation"
        assert 0.5 < partial_citation.confidence_score < 0.9, "Partial citation should have medium confidence"
        
    def test_edge_cases(self):
        """Test edge cases and potential error conditions."""
        # Empty string
        assert self.parser.parse("") is None, "Empty string should return None"
        
        # Non-citation text
        assert self.parser.parse("This is not a citation") is None, "Non-citation text should return None"
        
        # Incomplete citation
        incomplete = self.parser.parse("Smith, J. (2020).")
        assert incomplete is None or incomplete.confidence_score < 0.5, "Incomplete citation should have low confidence"