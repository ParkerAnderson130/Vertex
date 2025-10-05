import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
import re

def extract_text_from_xml(xml_string, pmc_id):
    paragraphs = []
    
    try:
        root = ET.fromstring(xml_string)
        
        # Look for <body> section with <p> tags
        body = root.find('.//body')
        if body is not None:
            for p in body.iter('p'):
                text = get_element_text(p)
                if text:
                    paragraphs.append(text)
        
        # If it has no <body> tag, try <abstract> tags
        if not paragraphs:
            abstract = root.find('.//abstract')
            if abstract is not None:
                for p in abstract.iter('p'):
                    text = get_element_text(p)
                    if text:
                        paragraphs.append(text)
        
        # If it has no <abstract> tag, try <sec> tags 
        if not paragraphs:
            for sec in root.iter('sec'):
                for p in sec.iter('p'):
                    text = get_element_text(p)
                    if text:
                        paragraphs.append(text)
        
        # Find all <p> tags
        if not paragraphs:
            for p in root.iter('p'):
                text = get_element_text(p)
                if text:
                    paragraphs.append(text)
        
        return paragraphs
        
    except ET.ParseError:
        return extract_from_broken_xml(xml_string, pmc_id)
    except Exception as e:
        print(f"  Error processing {pmc_id}: {e}")
        return []

# Extract all text from an element including nested elements
def get_element_text(element):
    text_parts = [element.text or '']
    for child in element:
        text_parts.append(get_element_text(child))
        text_parts.append(child.tail or '')
    return ''.join(text_parts).strip()

# Try to extract paragraphs from malformed XML using regex
def extract_from_broken_xml(xml_string, pmc_id):
    paragraphs = []
    
    p_pattern = r'<p[^>]*>(.*?)</p>'
    matches = re.findall(p_pattern, xml_string, re.DOTALL)
    
    for match in matches:
        
        text = re.sub(r'<[^>]+>', '', match)
        text = text.strip()
        if text and len(text) > 20:
            paragraphs.append(text)
    
    return paragraphs

# Read CSV file
csv_file = 'SB_publication_PMC_with_bioc.csv'
df = pd.read_csv(csv_file)

print(f"Processing {len(df)} articles with enhanced extraction...\n")

# Generate output directory
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

successful = 0
still_failed = 0
failed_ids = []

for idx, row in df.iterrows():
    pmc_id = row['PMC_ID']
    xml_string = row['BioC_XML']
    
    if idx % 100 == 0:
        print(f"{idx+1}/{len(df)} | Processing XML file")
    
    txt_file = data_dir / f"{pmc_id}.txt"
    if txt_file.exists():
        successful += 1
        continue
    
    if pd.isna(xml_string) or not xml_string.strip():
        still_failed += 1
        failed_ids.append(pmc_id)
        continue
    
    paragraphs = extract_text_from_xml(xml_string, pmc_id)
    if paragraphs:
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))
        successful += 1
    else:
        still_failed += 1
        failed_ids.append(pmc_id)

print(f"{successful}/{len(df)} | Successfully extracted")
print(f"{still_failed}/{len(df)} | Failed to be extracted")

if failed_ids:
    with open('still_failed_ids.txt', 'w') as f:
        f.write('\n'.join(failed_ids))
    print(f"Saved {len(failed_ids)} failed IDs to: still_failed_ids.txt")