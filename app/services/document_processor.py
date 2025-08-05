import fitz  # PyMuPDF (imported as fitz)
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from app.utils.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process insurance documents and extract clauses"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        
    def extract_text_from_pdf(self, pdf_content: bytes) -> List[Dict[str, Any]]:
        """Extract text from PDF content"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            pages = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    pages.append({
                        "page_number": page_num + 1,
                        "content": text.strip(),
                        "page_content": text.strip()
                    })
            
            doc.close()
            logger.info(f"Extracted text from {len(pages)} pages")
            return pages
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    def detect_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Detect insurance clauses in text"""
        clauses = []
        
        # Common clause patterns
        clause_patterns = [
            r'(?:Clause|Section|Article)\s*(\d+(?:\.\d+)*)[:\s]*(.*?)(?=(?:Clause|Section|Article)\s*\d|$)',
            r'(\d+\.\d+)[:\s]*(.*?)(?=\d+\.\d+|$)',
            r'(?:Coverage|Exclusion|Limitation|Waiting Period)[:\s]*(.*?)(?=(?:Coverage|Exclusion|Limitation|Waiting Period)|$)',
        ]
        
        for pattern in clause_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clause_id = match.group(1) if match.groups() else f"clause_{len(clauses) + 1}"
                clause_content = match.group(2) if len(match.groups()) > 1 else match.group(0)
                
                if clause_content.strip():
                    clauses.append({
                        "clause_id": clause_id,
                        "clause_title": f"Clause {clause_id}",
                        "clause_content": clause_content.strip(),
                        "content": clause_content.strip()
                    })
        
        # If no structured clauses found, create chunks
        if not clauses:
            chunks = self.create_text_chunks(text)
            for i, chunk in enumerate(chunks):
                clauses.append({
                    "clause_id": f"chunk_{i + 1}",
                    "clause_title": f"Document Section {i + 1}",
                    "clause_content": chunk,
                    "content": chunk
                })
        
        return clauses
    
    def create_text_chunks(self, text: str) -> List[str]:
        """Create overlapping text chunks for processing"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks
    
    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process a document and extract all relevant information"""
        try:
            # Extract text from PDF
            pages = self.extract_text_from_pdf(file_content)
            
            # Combine all text
            full_text = "\n\n".join([page["content"] for page in pages])
            
            # Detect clauses
            clauses = self.detect_clauses(full_text)
            
            # Create chunks for embedding
            chunks = self.create_text_chunks(full_text)
            
            return {
                "filename": filename,
                "pages": pages,
                "clauses": clauses,
                "chunks": chunks,
                "full_text": full_text,
                "total_pages": len(pages),
                "total_clauses": len(clauses)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise ValueError(f"Failed to process document: {str(e)}")
    
    def extract_entities_from_query(self, query: str) -> Dict[str, Any]:
        """Extract key entities from insurance query"""
        entities = {}
        
        # Age extraction
        age_pattern = r'(\d+)[\s-]*(?:year|yr)s?[\s-]*old'
        age_match = re.search(age_pattern, query, re.IGNORECASE)
        if age_match:
            entities["age"] = int(age_match.group(1))
        
        # Gender extraction
        gender_pattern = r'\b(male|female|man|woman)\b'
        gender_match = re.search(gender_pattern, query, re.IGNORECASE)
        if gender_match:
            entities["gender"] = gender_match.group(1).lower()
        
        # Medical condition/procedure
        medical_keywords = [
            r'\b(surgery|operation|procedure|treatment|therapy)\b',
            r'\b(knee|hip|heart|brain|spine|joint)\b',
            r'\b(cancer|diabetes|hypertension|asthma)\b'
        ]
        
        for pattern in medical_keywords:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities["condition"] = match.group(0)
                break
        
        # Location extraction
        location_pattern = r'\b(Mumbai|Delhi|Bangalore|Chennai|Kolkata|Pune|Hyderabad|Ahmedabad|Jaipur|Lucknow)\b'
        location_match = re.search(location_pattern, query, re.IGNORECASE)
        if location_match:
            entities["location"] = location_match.group(1)
        
        # Policy duration
        duration_pattern = r'(\d+)[\s-]*(?:month|year|yr)s?[\s-]*(?:old|policy)'
        duration_match = re.search(duration_pattern, query, re.IGNORECASE)
        if duration_match:
            entities["policy_duration"] = duration_match.group(1)
        
        return entities
