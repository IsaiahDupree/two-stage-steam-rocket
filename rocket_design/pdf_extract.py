#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF Text Extraction Utility for Rocket Design
This script extracts text from PDF files related to multistage rocket design 
to help incorporate realistic physical constraints into our models.
"""

import os
import sys
import re
import argparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_extract.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    import PyPDF2
    logger.info("PyPDF2 successfully imported")
except ImportError:
    logger.error("PyPDF2 not installed. Installing it now...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2
        logger.info("PyPDF2 successfully installed and imported")
    except Exception as e:
        logger.error(f"Failed to install PyPDF2: {e}")
        logger.info("Trying alternative extraction method...")


def extract_text_with_pypdf(pdf_path):
    """Extract text from PDF using PyPDF2."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            logger.info(f"PDF has {num_pages} pages")
            
            # Extract text from each page
            all_text = []
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                all_text.append(f"--- PAGE {page_num + 1} ---\n{text}")
            
            return "\n\n".join(all_text)
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2: {e}")
        return None


def extract_rocket_parameters(text):
    """Extract key rocket design parameters from the text."""
    parameters = {
        "thrust": [],
        "mass": [],
        "specific_impulse": [],
        "nozzle": [],
        "stages": [],
        "velocity": [],
        "altitude": [],
        "equations": []
    }
    
    # Find all mentions of thrust with units and values
    thrust_pattern = r'(\d+(?:\.\d+)?)\s*(?:kN|N|lbf|tonnes?-force)'
    parameters["thrust"] = re.findall(thrust_pattern, text)
    
    # Find all mentions of specific impulse
    isp_pattern = r'(specific impulse|Isp)[^\n,.]*?(\d+(?:\.\d+)?)\s*(?:s|sec)'
    parameters["specific_impulse"] = re.findall(isp_pattern, text)
    
    # Find all mentions of mass
    mass_pattern = r'(\d+(?:\.\d+)?)\s*(?:kg|tons?|tonnes?|lbs)'
    parameters["mass"] = re.findall(mass_pattern, text)
    
    # Find all mentions of nozzle
    nozzle_pattern = r'nozzle[^\n,.]*?(\d+(?:\.\d+)?)\s*(?:m|cm|mm|in)'
    parameters["nozzle"] = re.findall(nozzle_pattern, text)
    
    # Find all mentions of stages
    stage_pattern = r'(\d+)[- ]stage'
    parameters["stages"] = re.findall(stage_pattern, text)
    
    # Find all mentions of velocity
    velocity_pattern = r'(\d+(?:\.\d+)?)\s*(?:m/s|km/s|mph|fps)'
    parameters["velocity"] = re.findall(velocity_pattern, text)
    
    # Find all mentions of altitude
    altitude_pattern = r'(\d+(?:\.\d+)?)\s*(?:m|km|mi|ft)'
    parameters["altitude"] = re.findall(altitude_pattern, text)
    
    # Find equations (lines with multiple mathematical symbols)
    equation_pattern = r'([^.\n]+?(?:=|\+|-|\*|/|÷|×|√|\^)[^.\n]+)'
    parameters["equations"] = re.findall(equation_pattern, text)
    
    return parameters


def find_key_sections(text):
    """Find key sections related to multistage rocket design."""
    sections = {
        "nozzle_design": [],
        "stage_separation": [],
        "propellant": [],
        "aerodynamics": [],
        "structural": []
    }
    
    # Look for paragraphs containing key terms
    paragraphs = re.split(r'\n\s*\n', text)
    
    for para in paragraphs:
        if re.search(r'nozzle|throat|expansion|ratio|bell|conical', para, re.I):
            sections["nozzle_design"].append(para)
        if re.search(r'stage separation|staging|jettison', para, re.I):
            sections["stage_separation"].append(para)
        if re.search(r'propellant|fuel|oxidizer|combustion|burn', para, re.I):
            sections["propellant"].append(para)
        if re.search(r'aerodynamic|drag|lift|stability|center of pressure', para, re.I):
            sections["aerodynamics"].append(para)
        if re.search(r'structural|stress|strain|load|material|strength', para, re.I):
            sections["structural"].append(para)
    
    return sections


def extract_pdf_for_rocket_design(pdf_path, output_file=None):
    """Process PDF to extract rocket design information."""
    logger.info(f"Processing PDF: {pdf_path}")
    
    pdf_text = extract_text_with_pypdf(pdf_path)
    
    if not pdf_text:
        logger.error("Failed to extract text from PDF")
        return False
    
    # Get basic statistics
    word_count = len(pdf_text.split())
    logger.info(f"Extracted approximately {word_count} words from the PDF")
    
    # Extract design parameters
    parameters = extract_rocket_parameters(pdf_text)
    
    # Find key sections
    sections = find_key_sections(pdf_text)
    
    # Prepare output
    output = []
    output.append("# Rocket Design Parameters Extracted from PDF")
    output.append(f"\nSource: {os.path.basename(pdf_path)}")
    output.append(f"Word Count: {word_count}")
    
    # Add parameters section
    output.append("\n## Design Parameters")
    for param_type, values in parameters.items():
        if values:
            output.append(f"\n### {param_type.replace('_', ' ').title()}")
            output.append(f"Found {len(values)} references")
            output.append("Examples:")
            for i, value in enumerate(values[:5]):  # Show up to 5 examples
                output.append(f"- {value}")
    
    # Add key sections
    output.append("\n## Key Design Sections")
    for section_type, paragraphs in sections.items():
        if paragraphs:
            output.append(f"\n### {section_type.replace('_', ' ').title()}")
            output.append(f"Found {len(paragraphs)} relevant paragraphs")
            output.append("Excerpt:")
            # Take the first paragraph and truncate if needed
            excerpt = paragraphs[0]
            if len(excerpt) > 500:
                excerpt = excerpt[:497] + "..."
            output.append(excerpt)
    
    # Full text section (optional and often too large)
    # output.append("\n## Full Extracted Text (First 1000 characters)")
    # output.append(pdf_text[:1000] + "...")
    
    # Save or display results
    output_text = "\n".join(output)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_text)
        logger.info(f"Results saved to {output_file}")
    
    return output_text


def main():
    parser = argparse.ArgumentParser(description="Extract rocket design information from PDFs")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    if len(sys.argv) > 1:
        args = parser.parse_args()
        extract_pdf_for_rocket_design(args.pdf_path, args.output)
    else:
        # If no arguments, try to find PDFs in the current folder
        current_dir = Path(".")
        pdf_files = list(current_dir.glob("*.pdf"))
        
        if not pdf_files:
            parent_dir = current_dir.parent
            pdf_files = list(parent_dir.glob("*.pdf"))
        
        if pdf_files:
            for pdf_file in pdf_files:
                output_file = pdf_file.stem + "_extract.txt"
                extract_pdf_for_rocket_design(str(pdf_file), output_file)
        else:
            logger.error("No PDF files found in the current or parent directory")


if __name__ == "__main__":
    main()
