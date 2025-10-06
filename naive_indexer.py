#This program implements the following:
#    Subproject 1: Naive Indexer Implementation
#    Subproject 2: Simgle and AND query Implementation

import re
import time
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
        self.document_process_time = 0
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
        start_time = time.time()
        for document in tqdm(self.parser.documents):
            self.document_count += 1
            
            # Tokenize the document content
            tokens = self.tokenize(document.get_content())
            
            # Create term-document pairs
            for token in tokens:
                self.term_doc_pairs.append(TermDocumentPair(token, document.doc_id))
            
            if(self.document_count == 10000):
                self.document_process_time = time.time() - start_time
                print(f"Processed {self.document_count} documents in {self.document_process_time:.2f} seconds")

    def remove_duplicates_sort(self):
        unique_pairs = list(set(self.term_doc_pairs))
        self.term_doc_pairs = sorted(unique_pairs)

    def build_postings_lists(self):        
        for pair in tqdm(self.term_doc_pairs):
            if pair.term not in self.postings_list:
                self.postings_list[pair.term] = []
            self.postings_list[pair.term].append(pair.doc_id)
    
    #Single Term Querying
    def search_term(self, term):
        term = term.lower().strip()
        return self.postings_list.get(term, [])
    
    #Single and AND Querying
    def search_and_query(self, terms):
        result = self.search_term(terms[0])

        for term in terms[1:]:
            term_postings = self.search_term(term)
            result = self.intersect_postings(result, term_postings)
            if not result:
                break 

        return result

    def intersect_postings(self, list1, list2):
        result = []
        i, j = 0, 0

        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                result.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                i += 1
            else:
                j += 1

        return result

    def validate_queries(self):
        test_terms = ["movie", "samsung", "apple"]
        print("\nValidating Single Term Queries:")
        for term in test_terms:
            docs = self.search_term(term)
            print(f"'{term}': {len(docs)} documents : {docs}")

        test_and_queries = [
            ["movie", "oppenheimer", "viacom"],
            ["gold", "stock"],
            ["trade", "market", "oil"],
            ["movie", "barbie"]
        ]

        print("\nValidating AND Queries:")
        for terms in test_and_queries:
            docs = self.search_and_query(terms)
            print(f"'{' AND '.join(terms)}': {len(docs)} documents : {docs}")

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

    #Validating 3 single and 3 AND queries
    indexer.validate_queries()
    
    # Test the search
    while True:
        term = input("\nEnter a term to search (or '0' to quit): ")

        if term == '0':
            break

        if term:
            if(len(re.split("AND", term))>1):
                terms = re.split("AND", term)
                docs = indexer.search_and_query(terms)
                if docs:
                    print(f"\n\n'{' AND '.join(terms)}': {len(docs)} documents : {docs}")
                else:
                    print(f"The terms '{' AND '.join(terms)}' were not found together in any document.")    
            else:
                docs = indexer.search_term(term)
                if docs:
                    print(f"\n\n'{term}': {len(docs)} documents : {docs}")
                else:
                    print(f"The term '{term}' was not found.")