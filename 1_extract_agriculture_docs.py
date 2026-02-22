import fitz
import re
import json
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
import agri_config as config

class AgricultureDocProcessor:
    """Process agriculture-related documents: reports, guides, research papers"""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF documents"""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages_data.append({'page_num': page_num + 1, 'text': text})
        
        doc.close()
        return pages_data
    
    def detect_agriculture_structure(self, text: str) -> Dict:
        """Detect agriculture-specific content structures"""
        structure = {
            'has_crop_data': bool(re.search(r'\b(yield|production|cultivation|harvest)\b', text, re.IGNORECASE)),
            'has_pricing': bool(re.search(r'(price|rate|msp|market)', text, re.IGNORECASE)),
            'has_weather': bool(re.search(r'(rainfall|temperature|climate|monsoon)', text, re.IGNORECASE)),
            'has_scheme': bool(re.search(r'(scheme|subsidy|loan|insurance)', text, re.IGNORECASE)),
            'has_pest': bool(re.search(r'(pest|disease|insect|fungus)', text, re.IGNORECASE)),
            'has_technique': bool(re.search(r'(technique|method|practice|technology)', text, re.IGNORECASE))
        }
        return structure
    
    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """Extract agriculture metadata from filename"""
        metadata = {
            'document_type': 'Agriculture Report',
            'crop': 'General',
            'state': 'India',
            'season': 'All',
            'year': 'Unknown'
        }
        
        # Detect crop type
        for crop in config.CROP_CATEGORIES:
            if crop.lower() in filename.lower():
                metadata['crop'] = crop
                break
        
        # Detect state
        for state in config.STATES:
            if state.lower() in filename.lower():
                metadata['state'] = state
                break
        
        # Detect season
        for season in config.SEASONS:
            if season.lower() in filename.lower():
                metadata['season'] = season
                break
        
        # Extract year
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            metadata['year'] = year_match.group()
        
        # Detect document type
        if 'price' in filename.lower() or 'market' in filename.lower():
            metadata['document_type'] = 'Market Price Report'
        elif 'weather' in filename.lower() or 'climate' in filename.lower():
            metadata['document_type'] = 'Weather Report'
        elif 'scheme' in filename.lower() or 'policy' in filename.lower():
            metadata['document_type'] = 'Government Scheme'
        elif 'pest' in filename.lower() or 'disease' in filename.lower():
            metadata['document_type'] = 'Pest Management Guide'
        elif 'guide' in filename.lower() or 'manual' in filename.lower():
            metadata['document_type'] = 'Farming Guide'
        
        return metadata
    
    def smart_chunk_text(self, text: str, page_num: int, base_metadata: Dict) -> List[Dict]:
        """Chunk text with agriculture-specific separators"""
        splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\nCHAPTER ", "\nSECTION ", "\nTOPIC ",
                "\n\n\n", "\n\n", "\n", ". ", " ", ""
            ],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        
        chunks = splitter.split_text(text)
        chunk_objects = []
        
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) < config.MIN_CHUNK_SIZE:
                continue
            
            structure = self.detect_agriculture_structure(chunk_text)
            
            # Extract topic from chunk
            topic = 'General'
            topic_match = re.search(r'(?:TOPIC|SECTION|CHAPTER)\s*:?\s*([A-Z][^\n]+)', chunk_text)
            if topic_match:
                topic = topic_match.group(1).strip()[:100]
            
            chunk_metadata = {
                **base_metadata,
                'page_num': page_num,
                'chunk_id': i,
                'topic': topic,
                'has_crop_data': structure['has_crop_data'],
                'has_pricing': structure['has_pricing'],
                'has_weather': structure['has_weather'],
                'has_scheme': structure['has_scheme'],
                'has_pest': structure['has_pest'],
                'has_technique': structure['has_technique'],
                'char_count': len(chunk_text)
            }
            
            chunk_objects.append({
                'text': chunk_text.strip(),
                'metadata': chunk_metadata
            })
        
        return chunk_objects
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Process a single PDF document"""
        print(f"\n📄 Processing: {Path(pdf_path).name}")
        
        base_metadata = self.extract_metadata_from_filename(Path(pdf_path).name)
        base_metadata['source_file'] = Path(pdf_path).name
        
        print(f"   Type: {base_metadata['document_type']}")
        print(f"   Crop: {base_metadata['crop']}")
        print(f"   State: {base_metadata['state']}")
        print(f"   Season: {base_metadata['season']}")
        print(f"   Year: {base_metadata['year']}")
        
        pages_data = self.extract_text_from_pdf(pdf_path)
        print(f"   Pages extracted: {len(pages_data)}")
        
        all_chunks = []
        for page_data in pages_data:
            page_chunks = self.smart_chunk_text(
                page_data['text'],
                page_data['page_num'],
                base_metadata
            )
            all_chunks.extend(page_chunks)
        
        print(f"   ✅ Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], output_name: str):
        """Save chunks to JSON file"""
        output_path = config.CHUNKS_DIR / f"{output_name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved to: {output_path}")

def main():
    print("🚀 Agriculture Document Processing\n")
    print("="*60)
    
    processor = AgricultureDocProcessor()
    pdf_files = list(config.DATA_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDF files found!")
        print(f"   Please add agriculture PDF files to: {config.DATA_DIR}")
        print("\n   Sample document types:")
        print("   - Crop cultivation guides")
        print("   - Market price reports")
        print("   - Weather and climate reports")
        print("   - Government scheme documents")
        print("   - Pest management guides")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)\n")
    all_processed_chunks = []
    
    for pdf_path in pdf_files:
        try:
            chunks = processor.process_pdf(str(pdf_path))
            all_processed_chunks.extend(chunks)
            output_name = Path(pdf_path).stem
            processor.save_chunks(chunks, output_name)
        except Exception as e:
            print(f"   ❌ Error processing {pdf_path.name}: {e}")
            continue
    
    if all_processed_chunks:
        processor.save_chunks(all_processed_chunks, "all_agriculture_chunks")
        print("\n" + "="*60)
        print(f"✅ COMPLETED!")
        print(f"   Total chunks: {len(all_processed_chunks)}")
        print(f"   Output directory: {config.CHUNKS_DIR}")
        print("="*60)

if __name__ == "__main__":
    main()
