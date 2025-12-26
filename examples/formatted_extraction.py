"""
Formatted Document Extraction Example

Demonstrates using FormattedDocExtractor to preserve document layout.
Similar to LLMWhisperer - maintains visual structure, tables, and spacing.
"""

import sys
import os
from strutex import FormattedDocExtractor, PDFExtractor


def extract_formatted(file_path: str, output_path: str = None) -> str:
    """
    Extract text from a document while preserving layout.
    
    Args:
        file_path: Path to the PDF document
        output_path: Optional path to save extracted text
        
    Returns:
        Text with preserved layout and formatted tables
    """
    extractor = FormattedDocExtractor(
        preserve_tables=True,
        layout_mode=True,
    )
    text = extractor.extract(file_path)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Output saved to: {output_path}")
    
    return text


def extract_formatted_dense(file_path: str, output_path: str = None) -> str:
    """
    Extract from dense documents with tighter margins.
    """
    extractor = FormattedDocExtractor(
        preserve_tables=True,
        layout_mode=True,
        line_margin=0.3,
        char_margin=1.5,
    )
    text = extractor.extract(file_path)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    return text


def compare_extractors(file_path: str, output_path: str = None):
    """
    Compare standard vs formatted extraction.
    """
    output_lines = []
    
    output_lines.append("=" * 70)
    output_lines.append("STANDARD EXTRACTION (PDFExtractor)")
    output_lines.append("=" * 70)
    
    standard = PDFExtractor()
    standard_text = standard.extract(file_path)
    output_lines.append(standard_text)
    
    output_lines.append("\n" + "=" * 70)
    output_lines.append("FORMATTED EXTRACTION (FormattedDocExtractor)")
    output_lines.append("=" * 70)
    
    formatted = FormattedDocExtractor()
    formatted_text = formatted.extract(file_path)
    output_lines.append(formatted_text)
    
    result = "\n".join(output_lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Comparison saved to: {output_path}")
    else:
        print(result)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python formatted_extraction.py <pdf_file> [output_file]")
        print()
        print("Examples:")
        print("  python formatted_extraction.py invoice.pdf")
        print("  python formatted_extraction.py invoice.pdf output.txt")
        print("  python formatted_extraction.py invoice.pdf --compare")
        print("  python formatted_extraction.py invoice.pdf comparison.txt --compare")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_path = None
    compare_mode = "--compare" in sys.argv
    
    # Find output path (non-flag argument after file_path)
    for arg in sys.argv[2:]:
        if not arg.startswith("--"):
            output_path = arg
            break
    
    # Auto-generate output path if not specified
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = f"{base_name}_extracted.txt"
    
    print(f"Extracting from: {file_path}")
    
    if compare_mode:
        compare_extractors(file_path, output_path)
    else:
        text = extract_formatted(file_path, output_path)
        print("=" * 70)
        print(text[:2000] + "..." if len(text) > 2000 else text)
