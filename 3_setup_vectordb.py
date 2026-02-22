import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
import agri_config as config

class AgricultureVectorDB:
    """Setup vector database for agriculture documents"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        print("📦 Loading embedding model...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        print("   ✅ Model loaded\n")
        
        try:
            self.collection = self.client.get_collection("agriculture_docs")
            print("📚 Using existing collection 'agriculture_docs'")
        except:
            self.collection = self.client.create_collection(
                name="agriculture_docs",
                metadata={"description": "Agriculture knowledge base documents"}
            )
            print("📚 Created new collection 'agriculture_docs'")
    
    def load_chunks_from_json(self, json_path: str):
        """Load chunks from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_chunks_to_db(self, chunks: list, batch_size: int = 100):
        """Add chunks to database in batches"""
        print(f"\n📄 Processing {len(chunks)} chunks in batches of {batch_size}...")
        
        total_chunks = len(chunks)
        total_batches = (total_chunks + batch_size - 1) // batch_size
        
        for batch_num in range(0, total_chunks, batch_size):
            batch_end = min(batch_num + batch_size, total_chunks)
            batch_chunks = chunks[batch_num:batch_end]
            
            current_batch = (batch_num // batch_size) + 1
            print(f"\n   📦 Batch {current_batch}/{total_batches} (chunks {batch_num+1}-{batch_end})")
            
            documents = []
            metadatas = []
            ids = []
            
            for idx, chunk in enumerate(batch_chunks):
                actual_idx = batch_num + idx
                chunk_id = f"{chunk['metadata'].get('source_file', 'unknown')}_{chunk['metadata'].get('page_num', 0)}_{chunk['metadata'].get('chunk_id', actual_idx)}"
                documents.append(chunk['text'])
                
                # Filter out None values from metadata
                clean_metadata = {k: str(v) if v is not None else 'N/A' 
                                for k, v in chunk['metadata'].items()}
                metadatas.append(clean_metadata)
                ids.append(chunk_id)
            
            # Generate embeddings
            print(f"      🧮 Generating embeddings for {len(documents)} chunks...")
            embeddings = self.embedding_model.encode(documents, show_progress_bar=False)
            
            # Add to database
            print(f"      💾 Adding to vector database...")
            try:
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"      ✅ Successfully added batch {current_batch}")
            except Exception as e:
                print(f"      ❌ Error adding batch {current_batch}: {e}")
                raise
        
        print(f"\n   ✅ Successfully added all {total_chunks} chunks to database")
    
    def get_collection_stats(self):
        """Get database statistics"""
        count = self.collection.count()
        print(f"\n📊 Database Statistics:")
        print(f"   Total chunks in database: {count}")
        return count

def main():
    print("🚀 Setting up Agriculture Vector Database\n")
    print("="*60)
    
    db_setup = AgricultureVectorDB()
    chunk_files = list(config.CHUNKS_DIR.glob("*.json"))
    
    if not chunk_files:
        print("⚠️  No chunk files found!")
        print(f"   Please run 1_extract_agriculture_docs.py first")
        print(f"   Or add agriculture documents to: {config.DATA_DIR}")
        return
    
    print(f"\nFound {len(chunk_files)} chunk file(s):\n")
    for f in chunk_files:
        print(f"   - {f.name}")
    
    print("\n" + "="*60)
    print("Loading chunks...")
    
    combined_file = config.CHUNKS_DIR / "all_agriculture_chunks.json"
    target_file = combined_file if combined_file.exists() else chunk_files[0]
    
    print(f"📂 Loading: {target_file.name}\n")
    chunks = db_setup.load_chunks_from_json(str(target_file))
    print(f"   Loaded {len(chunks)} chunks from file")
    
    # Add chunks in batches
    db_setup.add_chunks_to_db(chunks, batch_size=100)
    db_setup.get_collection_stats()
    
    print("\n" + "="*60)
    print("✅ Vector Database Setup Complete!")
    print(f"   Database location: {config.VECTOR_DB_PATH}")
    print("="*60)

if __name__ == "__main__":
    main()
