"""
Citation Parser Module - Main Application

This is the main entry point for the Citation Parser Module of the Citation Checker project.
It provides command-line functionality to parse citations from text or files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.parsers.apa_parser import APACitationParser
from src.models.citation import Citation

def parse_file(file_path: str, parser_name: str = "apa") -> List[Citation]:
    """Parse citations from a file.
    
    Args:
        file_path: Path to the file containing citations
        parser_name: Name of the parser to use (default: "apa")
        
    Returns:
        List of Citation objects found in the file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return parse_text(content, parser_name)

def parse_text(text: str, parser_name: str = "apa") -> List[Citation]:
    """Parse citations from text.
    
    Args:
        text: Text containing citations
        parser_name: Name of the parser to use (default: "apa")
        
    Returns:
        List of Citation objects found in the text
    """
    parser = get_parser(parser_name)
    if not parser:
        print(f"Error: Parser '{parser_name}' not found.")
        return []
    
    return parser.extract_citations(text)

def get_parser(parser_name: str):
    """Get a parser instance by name.
    
    Args:
        parser_name: Name of the parser to get
        
    Returns:
        Parser instance or None if not found
    """
    if parser_name.lower() == "apa":
        return APACitationParser()
    # Add more parsers here as they are implemented
    return None

def format_citation_output(citations: List[Citation], output_format: str = "text") -> str:
    """Format citations for output.
    
    Args:
        citations: List of Citation objects
        output_format: Format to use ("text", "json", "csv")
        
    Returns:
        Formatted string
    """
    if output_format == "json":
        # Convert to dictionary and dump to JSON
        return json.dumps({
            "citations": [citation.to_dict() for citation in citations],
            "count": len(citations)
        }, indent=2)
    
    elif output_format == "csv":
        # Create CSV header and rows
        header = "authors,year,title,source,citation_type,confidence_score,doi,url,volume,issue,pages"
        rows = []
        for citation in citations:
            authors_str = "|".join(citation.authors)
            row = f'"{authors_str}",{citation.year},"{citation.title}","{citation.source}",{citation.citation_type},{citation.confidence_score},{citation.doi or ""},{citation.url or ""},{citation.volume or ""},{citation.issue or ""},{citation.pages or ""}'
            rows.append(row)
        
        return header + "\n" + "\n".join(rows)
    
    else:  # Default to text format
        if not citations:
            return "No citations found."
        
        output = f"Found {len(citations)} citations:\n\n"
        for i, citation in enumerate(citations, 1):
            output += f"Citation {i}:\n"
            output += f"  Authors: {', '.join(citation.authors)}\n"
            output += f"  Year: {citation.year}\n"
            output += f"  Title: {citation.title}\n"
            output += f"  Source: {citation.source}\n"
            if citation.doi:
                output += f"  DOI: {citation.doi}\n"
            if citation.url:
                output += f"  URL: {citation.url}\n"
            if citation.volume:
                output += f"  Volume: {citation.volume}\n"
            if citation.issue:
                output += f"  Issue: {citation.issue}\n"
            if citation.pages:
                output += f"  Pages: {citation.pages}\n"
            output += f"  Type: {citation.citation_type}\n"
            output += f"  Confidence: {citation.confidence_score:.2f}\n"
            output += "\n"
        
        return output

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Citation Parser Module")
    parser.add_argument("-f", "--file", help="Path to file containing citations")
    parser.add_argument("-t", "--text", help="Text containing citations")
    parser.add_argument("-p", "--parser", default="apa", help="Parser to use (default: apa)")
    parser.add_argument("-o", "--output", default="text", choices=["text", "json", "csv"], 
                        help="Output format (default: text)")
    parser.add_argument("--output-file", help="Path to output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Validate input
    if not args.file and not args.text:
        parser.print_help()
        sys.exit(1)
    
    # Parse citations
    citations = []
    if args.file:
        citations = parse_file(args.file, args.parser)
    elif args.text:
        citations = parse_text(args.text, args.parser)
    
    # Format output
    output = format_citation_output(citations, args.output)
    
    # Write output
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)

if __name__ == "__main__":
    main()