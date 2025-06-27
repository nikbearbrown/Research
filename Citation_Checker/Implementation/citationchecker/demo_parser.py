"""
Demo script for the Citation Parser Module.
This script demonstrates basic usage of the APA citation parser.
"""

import sys
import os

# Add the current directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.parsers.apa_parser import APACitationParser

def demo_single_citation():
    """Demo parsing a single citation."""
    parser = APACitationParser()
    
    # Sample citation from the paper
    citation_text = "Garfield, E. (1955). Citation indexes for science: A new dimension in documentation through association of ideas. Science, 122(3159), 108-111. DOI: 10.1126/science.122.3159.108"
    
    print("\n=== DEMO: Parsing a Single Citation ===")
    print(f"Input: {citation_text}\n")
    
    # Parse the citation
    citation = parser.parse(citation_text)
    
    if citation:
        print("Successfully parsed citation:")
        print(f"  Authors: {', '.join(citation.authors)}")
        print(f"  Year: {citation.year}")
        print(f"  Title: {citation.title}")
        print(f"  Source: {citation.source}")
        print(f"  Volume: {citation.volume}")
        print(f"  Issue: {citation.issue}")
        print(f"  Pages: {citation.pages}")
        print(f"  DOI: {citation.doi}")
        print(f"  Confidence Score: {citation.confidence_score:.2f}")
    else:
        print("Failed to parse citation.")

def demo_extract_citations():
    """Demo extracting citations from text."""
    parser = APACitationParser()
    
    # Sample text with multiple citations
    text = """
    The integrity of academic discourse fundamentally depends on the accuracy of citations. As Garfield (1955) noted, citations serve as the connective tissue of scholarly knowledge, allowing readers to trace the development of ideas and verify claims. However, citation errors have been documented across disciplines at concerning rates, with studies showing error rates ranging from 10% to over 40% depending on the field and error type (Luo et al., 2014; Awais et al., 2015).
    
    References:
    
    Garfield, E. (1955). Citation indexes for science: A new dimension in documentation through association of ideas. Science, 122(3159), 108-111.
    
    Luo, M., Li, C. C., Molina, D., Andersen, J. P., & Paget, M. (2014). Accuracy of citation data in Web of Science and Scopus. Journal of Informetrics, 8(4), 824-830.
    
    Awais, R., Singh, N., Weizman, A., & Sharma, A. (2015). Citation errors in the master's theses of the Library and Information Science Department, at the University of the Punjab. Library Philosophy and Practice, 1223, 1-15.
    """
    
    print("\n=== DEMO: Extracting Citations from Text ===")
    
    # Extract citations
    citations = parser.extract_citations(text)
    
    print(f"Found {len(citations)} citations:")
    
    for i, citation in enumerate(citations, 1):
        print(f"\nCitation {i}:")
        print(f"  Authors: {', '.join(citation.authors)}")
        print(f"  Year: {citation.year}")
        print(f"  Title: {citation.title}")
        print(f"  Source: {citation.source}")
        print(f"  Confidence Score: {citation.confidence_score:.2f}")

def main():
    """Main function."""
    print("Citation Parser Module Demo")
    print("==========================")
    
    demo_single_citation()
    demo_extract_citations()
    
    print("\nDemo complete!")

if __name__ == "__main__":
    main()