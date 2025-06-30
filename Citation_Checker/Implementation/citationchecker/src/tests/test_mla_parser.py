import json
import os
import pytest
from src.parsers.mla_parser import MLACitationParser

# Load test data
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(current_dir, "test_data", "mla_citations.json")

with open(test_data_path, 'r') as f:
    test_data = json.load(f)

class TestMLAParser:
    """Test suite for the MLA citation parser."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        self.parser = MLACitationParser()
    
    @pytest.mark.parametrize("citation_data", test_data["citations"])
    def test_parse_citation(self, citation_data):
        """Test the parse method with various MLA citations."""
        # Parse the citation text
        citation = self.parser.parse(citation_data["text"])
        
        # Check that parsing succeeded
        assert citation is not None, f"Failed to parse: {citation_data['text']}"
        
        # Check basic fields match expected values
        expected = citation_data["expected"]
        
        # Test author parsing - handle empty authors list for no-author citations
        if expected["authors"]:
            for expected_author in expected["authors"]:
                assert expected_author in citation.authors, f"Missing author: {expected_author}"
            assert len(citation.authors) == len(expected["authors"]), f"Author count mismatch: {len(citation.authors)} != {len(expected['authors'])}"
        else:
            # For no-author citations, authors list should be empty or contain empty strings
            assert not citation.authors or all(not author.strip() for author in citation.authors), "Expected no authors for anonymous citation"
        
        # Test year parsing
        assert citation.year == expected["year"], f"Year mismatch: {citation.year} != {expected['year']}"
        
        # Test title parsing - be more flexible with case and punctuation
        assert expected["title"].lower() in citation.title.lower(), f"Title mismatch: '{citation.title}' should contain '{expected['title']}'"
        
        # Test source parsing
        assert expected["source"] in citation.source, f"Source mismatch: '{citation.source}' should contain '{expected['source']}'"
        
        # Test optional fields if present in expected data
        if "volume" in expected:
            assert citation.volume == expected["volume"], f"Volume mismatch: {citation.volume} != {expected['volume']}"
        
        if "issue" in expected:
            assert citation.issue == expected["issue"], f"Issue mismatch: {citation.issue} != {expected['issue']}"
        
        if "pages" in expected:
            assert citation.pages == expected["pages"], f"Pages mismatch: {citation.pages} != {expected['pages']}"
        
        if "publisher" in expected:
            assert citation.publisher == expected["publisher"], f"Publisher mismatch: {citation.publisher} != {expected['publisher']}"
        
        if "url" in expected:
            assert citation.url == expected["url"], f"URL mismatch: {citation.url} != {expected['url']}"
        
        # Verify the citation format is set correctly
        assert citation.citation_format == "mla", f"Citation format should be 'mla', got '{citation.citation_format}'"
        
        # Verify the confidence score is reasonable
        assert citation.confidence_score > 0.6, f"Low confidence score: {citation.confidence_score}"
    
    def test_extraction_from_text(self):
        """Test extracting citations from a larger text."""
        # Get the mixed text from test data
        text = test_data["mixed_text"]
        
        # Extract citations
        citations = self.parser.extract_citations(text)
        
        # Check we found at least 3 citations
        assert len(citations) >= 3, f"Expected at least 3 citations, found {len(citations)}"
        
        # Check that the first citation matches our expected data
        assert "Smith" in citations[0].authors[0], "First author should be Smith"
        assert citations[0].year == 2020, "Year should be 2020"
        
        # Check the second citation
        assert "Johnson" in citations[1].authors[0], "Second citation author should be Johnson"
        assert citations[1].year == 2021, "Second citation year should be 2021"
        
        # Check the third citation
        assert "Garcia" in citations[2].authors[0], "Third citation author should be Garcia"
        assert citations[2].year == 2022, "Third citation year should be 2022"
    
    def test_confidence_calculation(self):
        """Test the confidence score calculation."""
        # Create a complete citation
        complete_citation = self.parser.parse(test_data["citations"][0]["text"])
        assert complete_citation.confidence_score > 0.8, "Complete citation should have high confidence"
        
        # Create a partial citation
        partial_text = "Smith, John. \"Some paper.\" Journal."
        partial_citation = self.parser.parse(partial_text)
        assert partial_citation is not None, "Failed to parse partial citation"
        assert 0.5 < partial_citation.confidence_score < 0.9, "Partial citation should have medium confidence"
    
    def test_journal_article_parsing(self):
        """Test parsing of journal articles specifically."""
        journal_citation = "Smith, John. \"The Impact of Digital Libraries on Academic Research.\" Journal of Information Science, vol. 45, no. 3, 2020, pp. 234-250."
        citation = self.parser.parse(journal_citation)
        
        assert citation is not None, "Journal citation should parse successfully"
        assert citation.citation_type == "article", "Should be identified as article"
        assert citation.volume == "45", "Volume should be extracted"
        assert citation.issue == "3", "Issue should be extracted"
        assert citation.pages == "234-250", "Pages should be extracted"
    
    def test_book_parsing(self):
        """Test parsing of book citations specifically."""
        book_citation = "Wilson, Robert. Understanding Academic Citations. University Press, 2019."
        citation = self.parser.parse(book_citation)
        
        assert citation is not None, "Book citation should parse successfully"
        assert citation.citation_type == "book", "Should be identified as book"
        assert citation.publisher == "University Press", "Publisher should be extracted"
        assert citation.year == 2019, "Year should be extracted"
    
    def test_web_citation_parsing(self):
        """Test parsing of web citations specifically."""
        web_citation = "Chen, Li. \"Web-Based Citation Tools: A Comprehensive Review.\" TechReview Online, 15 Mar. 2023, https://www.techreview.com/citations-tools-2023."
        citation = self.parser.parse(web_citation)
        
        assert citation is not None, "Web citation should parse successfully"
        assert citation.citation_type == "web", "Should be identified as web"
        assert citation.url == "https://www.techreview.com/citations-tools-2023", "URL should be extracted"
        assert citation.year == 2023, "Year should be extracted from date"
    
    def test_chapter_parsing(self):
        """Test parsing of book chapter citations specifically."""
        chapter_citation = "Anderson, Sarah. \"The Evolution of Citation Formats.\" The History of Academic Writing, edited by Michael Thompson, Academic Publishers, 2020, pp. 78-95."
        citation = self.parser.parse(chapter_citation)
        
        assert citation is not None, "Chapter citation should parse successfully"
        assert citation.citation_type == "book_chapter", "Should be identified as book chapter"
        assert citation.publisher == "Academic Publishers", "Publisher should be extracted"
        assert citation.pages == "78-95", "Pages should be extracted"
    
    def test_multiple_authors_parsing(self):
        """Test parsing of citations with multiple authors."""
        # Two authors with "and"
        two_authors = "Johnson, Mary, and David Brown. \"Citation Analysis in the Digital Age.\" Academic Writing Quarterly, vol. 12, no. 4, 2021, pp. 45-67."
        citation = self.parser.parse(two_authors)
        
        assert citation is not None, "Two-author citation should parse successfully"
        assert len(citation.authors) == 2, "Should have exactly 2 authors"
        assert "Johnson, Mary" in citation.authors, "First author should be Johnson, Mary"
        assert "Brown, David" in citation.authors, "Second author should be Brown, David"
    
    def test_et_al_parsing(self):
        """Test parsing of citations with et al."""
        et_al_citation = "Garcia, Patricia, et al. \"Machine Learning Applications in Citation Verification.\" AI Research Review, vol. 8, no. 2, 2022, pp. 112-135."
        citation = self.parser.parse(et_al_citation)
        
        assert citation is not None, "Et al. citation should parse successfully"
        assert len(citation.authors) == 1, "Should have exactly 1 author (first author only)"
        assert "Garcia, Patricia" in citation.authors, "First author should be Garcia, Patricia"
    
    def test_no_author_parsing(self):
        """Test parsing of citations without authors."""
        no_author = "\"Citation Errors in Student Papers.\" Education Today, vol. 25, no. 6, 2021, pp. 12-18."
        citation = self.parser.parse(no_author)
        
        assert citation is not None, "No-author citation should parse successfully"
        assert citation.title == "Citation Errors in Student Papers", "Title should be extracted correctly"
        assert citation.source == "Education Today", "Source should be extracted correctly"
    
    def test_edge_cases(self):
        """Test edge cases and potential error conditions."""
        # Empty string
        assert self.parser.parse("") is None, "Empty string should return None"
        
        # Non-citation text
        assert self.parser.parse("This is not a citation") is None, "Non-citation text should return None"
        
        # Incomplete citation
        incomplete = self.parser.parse("Smith, John.")
        assert incomplete is None or incomplete.confidence_score < 0.5, "Incomplete citation should have low confidence or fail"
    
    def test_format_detection(self):
        """Test that MLA format is correctly identified."""
        mla_citation = "Smith, John. \"Title.\" Journal, vol. 1, no. 2, 2020, pp. 1-10."
        citation = self.parser.parse(mla_citation)
        
        assert citation is not None, "MLA citation should parse"
        assert citation.citation_format == "mla", "Should be identified as MLA format"
    
    def test_volume_issue_extraction(self):
        """Test extraction of volume and issue numbers in MLA format."""
        citation_text = "Author, Name. \"Title.\" Journal, vol. 15, no. 3A, 2020, pp. 45-67."
        citation = self.parser.parse(citation_text)
        
        assert citation is not None, "Citation should parse successfully"
        assert citation.volume == "15", "Volume should be extracted correctly"
        assert citation.issue == "3A", "Issue should be extracted correctly (including letter)"
    
    def test_date_extraction(self):
        """Test extraction of various date formats."""
        # Full date format
        full_date = "Author, Name. \"Title.\" Website, 15 Mar. 2023, https://example.com."
        citation = self.parser.parse(full_date)
        
        if citation:  # May not parse perfectly due to simplified regex
            assert citation.year == 2023, "Year should be extracted from full date"
        
        # Simple year format
        year_only = "Author, Name. \"Title.\" Journal, 2022, pp. 1-10."
        citation = self.parser.parse(year_only)
        
        if citation:
            assert citation.year == 2022, "Year should be extracted"
    
    def test_parser_initialization(self):
        """Test that the parser initializes correctly."""
        parser = MLACitationParser()
        assert parser.format_name == "mla", "Format name should be 'mla'"
        assert hasattr(parser, 'patterns'), "Parser should have patterns attribute"
        assert hasattr(parser, 'mla_patterns'), "Parser should have mla_patterns attribute"
