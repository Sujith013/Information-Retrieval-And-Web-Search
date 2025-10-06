#This program implements a naive indexing algorithm by following these steps:
#    1. Process documents and create term-document pairs
#    2. Sort the pairs
#    3. Remove duplicates
#    4. Build postings lists for each term

import re
import argparse
from tqdm import tqdm
from document_parser import ReutersParser

class TermDocumentPair:
    def __init__(self, term, doc_id):
        self.term = term
        self.doc_id = doc_id
    
    def __lt__(self, other):
        # For sorting: first by term, then by doc_id.
        if self.term != other.term:
            return self.term < other.term
        return self.doc_id < other.doc_id
    
    def __eq__(self, other):
        # For duplicate removal.
        return self.term == other.term and self.doc_id == other.doc_id
       
    def __hash__(self):
        # For using in sets.
        return hash((self.term, self.doc_id))

class NaiveIndexer:    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.parser = ReutersParser(dataset_path)
        self.term_doc_pairs = []
        self.postings_list = {}
        self.document_count = 0
        self.build_index()
    
    def build_index(self):
        print("Starting Naive Indexer")
        
        # Process documents and create term-document pairs, sort and remove duplicates 
        self.create_term_doc_pairs()
        self.remove_duplicates_sort()

        # Build postings lists
        self.build_postings_lists()

    def tokenize(self, text):
        if not text:
            return []
        
        text = text.lower()
        text = re.sub(r'[\d]', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split(" ")
    
    def create_term_doc_pairs(self):        
        for document in tqdm(self.parser.documents):
            self.document_count += 1
            
            # Tokenize the document content
            tokens = self.tokenize(document.get_content())
            
            # Create term-document pairs
            for token in tokens:
                self.term_doc_pairs.append(TermDocumentPair(token, document.doc_id))
    
    def remove_duplicates_sort(self):
        unique_pairs = list(set(self.term_doc_pairs))
        self.term_doc_pairs = sorted(unique_pairs)

    def build_postings_lists(self):        
        for pair in tqdm(self.term_doc_pairs):
            if pair.term not in self.postings_list:
                self.postings_list[pair.term] = []
            self.postings_list[pair.term].append(pair.doc_id)
    
    def search_term(self, term):
        term = term.lower()
        return self.postings_list.get(term)
    
    def get_statistics(self):
        vocabulary_size = len(self.postings_list)
        
        return {
            'document_count': self.document_count,
            'vocabulary_size': vocabulary_size,
            'total_term_document_pairs': len(self.term_doc_pairs),
            'average_postings_length': len(self.term_doc_pairs) / vocabulary_size if vocabulary_size > 0 else 0
        }
    
    def save_index(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Naive Indexer Results\n")
            f.write(f"{self.get_statistics()}\n")
            
            for term in sorted(self.postings_list.keys()):
                f.write(f"{term} -> {self.postings_list[term]}\n")

        print(f"Index saved to {filename}")

if __name__ == "__main__":
    # Test the naive indexer
    indexer = NaiveIndexer(dataset_path="./reuters21578")
    
    # Show statistics
    print("\nIndexing Statistics:")
    print(indexer.get_statistics())
    
    # Save the index
    indexer.save_index("naive_index.txt")
    
    # Test the search
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--term', type=str)
    args = arg_parser.parse_args()
    
    if(args.term):
        docs = indexer.search_term(args.term)
        print(f"\n\n'{args.term}': {len(docs)} documents")
        print(f"'{args.term}': {docs} documents")