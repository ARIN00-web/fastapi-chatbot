import fitz  
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
import os

genai.configure(api_key='AIzaSyBSn8-QV4L6Fju4-HzjmBwhP01ghwbzSjY')

class DarwinChatbot:
    def __init__(self, pdf_path='darwin.pdf'):
        self.pdf_path = pdf_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.index = None
        self.initialize()
        
    def initialize(self):
        try:
         if os.path.exists("cache/faiss.index") and os.path.exists("cache/chunks.npy"):
            print("Loading cached index and chunks...")
            self.chunks = np.load("cache/chunks.npy", allow_pickle=True).tolist()
            self.index = faiss.read_index("cache/faiss.index")
            print(f"Loaded {len(self.chunks)} chunks and {self.index.ntotal} vectors from cache.")
         else:
            book_text = self.extract_text_from_pdf(self.pdf_path)
            print(f"PDF text length: {len(book_text)}")
            print(f"First 100 characters: {book_text[:100]}")
            
            self.chunks = self.split_text(book_text)
            print(f"Number of chunks: {len(self.chunks)}")
            if self.chunks:
                print(f"First chunk length: {len(self.chunks[0])}")

            embeddings = self.model.encode(self.chunks)
            embeddings = np.array(embeddings, dtype=np.float32)

            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            print(f"Initialized with {len(self.chunks)} chunks and {self.index.ntotal} vectors")
            
            # Save cache
            os.makedirs("cache", exist_ok=True)
            np.save("cache/chunks.npy", self.chunks)
            faiss.write_index(self.index, "cache/faiss.index")

            print("Processed and cached PDF data.")
        except Exception as e:
            print(f"Initialization error: {e}")
            raise

    def extract_text_from_pdf(self, pdf_path):
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            text = ""
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += page_text
                print(f"Page {page_num + 1}: {len(page_text)} characters")
            
            if not text.strip():
                print("WARNING: Extracted text is empty. This might be a scanned PDF without OCR.")
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise

    def split_text(self, text, chunk_size=1000):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def search(self, query, top_k=5):
        try:
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding, dtype=np.float32)

            distances, indices = self.index.search(query_embedding, top_k)
            valid_indices = [i for i in indices[0] if i < len(self.chunks)]

            if not valid_indices:
                return ["No relevant information found."]
            return [self.chunks[i] for i in valid_indices]
        except Exception as e:
            print(f"Search error: {e}")
            return ["Error searching for relevant information."]

    def generate_answer(self, question, context):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"Context from Darwin's Origin of Species:\n\n{context}\n\nQuestion: {question}\n\nAnswer based only on the provided context:"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Sorry, I couldn't generate an answer. Error: {str(e)}"

    def ask(self, question):
        relevant_chunks = self.search(question)
        context = " ".join(relevant_chunks)
        answer = self.generate_answer(question, context)
        return answer
        


       