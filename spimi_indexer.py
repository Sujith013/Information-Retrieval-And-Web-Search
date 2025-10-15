#This program implements the following:
#    Subproject IV: SPIMI Indexer Implementation

import re
import time
from tqdm import tqdm
from document_parser import ReutersParser

class SPIMIIndexer:    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.parser = ReutersParser(dataset_path)
        self.postings_list = {}
        self.document_count = 0
        self.document_process_time = 0
        self.build_index()
    
    def build_index(self):
        print("Starting SPIMI Indexer")
        
        # Process documents and directly build postings lists
        self.create_inverted_index()

    def tokenize(self, text):
        if not text:
            return []
        
        text = text
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split(" ")
    
    def create_inverted_index(self):
        start_time = time.time()
        for document in tqdm(self.parser.documents):
            self.document_count += 1
            
            # Tokenize the document content
            tokens = self.tokenize(document.get_content())
            
            # Directly append docID to postings list for each term
            for token in tokens:
                if token.strip():
                    if token not in self.postings_list:
                        self.postings_list[token] = []
                    
                    if not self.postings_list[token] or self.postings_list[token][-1] != document.doc_id:
                        self.postings_list[token].append(document.doc_id)
            
            if(self.document_count == 10000):
                self.document_process_time = time.time() - start_time

    #Single Term Querying
    def search_term(self, term):
        term = term.strip()
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
            if int(list1[i]) == int(list2[j]):
                result.append(list1[i])
                i += 1
                j += 1
            elif int(list1[i]) < int(list2[j]):
                i += 1
            else:
                j += 1

        return result

    def validate_queries(self):
        test_terms = ["movie", "Samsung", "apple"]
        print("\nValidating Single Term Queries:")
        for term in test_terms:
            docs = self.search_term(term)
            print(f"'{term}': {len(docs)} documents : {docs}")

        #Challenge queries
        start_time = time.time()
        test_terms = ["copper", "Chrysler", "Bundesbank"]
        print("\nValidating Challenge Queries:")
        for term in test_terms:
            docs = self.search_term(term)
            print(f"'{term}': {len(docs)} documents : {docs}")
        print(f"Challenge queries processed in {time.time() - start_time:.2f} seconds")

        test_and_queries = [
            ["Movie", "Oppenheimer", "Viacom"],
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
        total_postings = sum(len(postings) for postings in self.postings_list.values())
        
        return {
            'document_count': self.document_count,
            'vocabulary_size': vocabulary_size,
            'total_postings': total_postings,
            'average_postings_length': total_postings / vocabulary_size if vocabulary_size > 0 else 0
        }
    
    def save_index(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"SPIMI Indexer Results\n")
            f.write(f"{self.get_statistics()}\n")
            
            for term in sorted(self.postings_list.keys()):
                f.write(f"{term} -> {self.postings_list[term]}\n")

        print(f"Index saved to {filename}")

if __name__ == "__main__":
    # Test the SPIMI indexer
    spimi_indexer = SPIMIIndexer(dataset_path="./reuters21578")
    
    # Show statistics
    print("\nSPIMI Indexing Statistics:")
    print(spimi_indexer.get_statistics())
    print(f"Processed {spimi_indexer.document_count} documents in {spimi_indexer.document_process_time:.2f} seconds")
   
    # Save the index
    spimi_indexer.save_index("spimi_index.txt")

    # Validating 3 single and 3 AND queries
    spimi_indexer.validate_queries()
    
    # Test the search
    while True:
        term = input("\nEnter a term to search (or '0' to quit): ")

        if term == '0':
            break

        if term:
            if(len(re.split("AND", term))>1):
                terms = re.split("AND", term)
                docs = spimi_indexer.search_and_query(terms)
                if docs:
                    print(f"\n\n'{' AND '.join(terms)}': {len(docs)} documents : {docs}")
                else:
                    print(f"The terms '{' AND '.join(terms)}' were not found together in any document.")    
            else:
                docs = spimi_indexer.search_term(term)
                if docs:
                    print(f"\n\n'{term}': {len(docs)} documents : {docs}")
                else:
                    print(f"The term '{term}' was not found.")