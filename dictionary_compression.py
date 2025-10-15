#This program implements the following:
#    Subproject III: Dictionary compression table

from naive_indexer import NaiveIndexer

class DictionaryCompression:
    def __init__(self):
        # 30 stop words
        self.stop_words_30 = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should'
        }
        
        # 150 stop words
        self.stop_words_150 = self.stop_words_30.union({
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're',
            've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven',
            'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'
        })
    
    def apply_no_numbers(self, tokens):
        return [token for token in tokens if not token.isdigit()]
    
    def apply_case_folding(self, tokens):
        return [token.lower() for token in tokens]
    
    def apply_stop_words_30(self, tokens):
        return [token for token in tokens if token.lower() not in self.stop_words_30]
    
    def apply_stop_words_150(self, tokens):
        return [token for token in tokens if token.lower() not in self.stop_words_150]
    
    def apply_stemming(self, tokens):
        stemmed = []
        for token in tokens:
            stemmed_token = self.simple_stem(token)
            stemmed.append(stemmed_token)
        return stemmed
    
    def simple_stem(self, word):
        if len(word) <= 3:
            return word
            
        # Remove common suffixes
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion', 'ness', 'ment', 'able', 'ible']
        
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        if word.endswith('s') and len(word) > 3 and not word.endswith('ss'):
            return word[:-1]
            
        return word

class CompressedIndexer:
    def __init__(self, indexer, compression_type="unfiltered"):
        self.original_indexer = indexer
        self.compression_type = compression_type
        self.compression = DictionaryCompression()
        self.postings_list = {}
        self.vocabulary_stats = {}
        
        self.apply_compression()
    
    def apply_compression(self):        
        original_pairs = []
        for term, doc_ids in self.original_indexer.postings_list.items():
            for doc_id in doc_ids:
                original_pairs.append((term, doc_id))
        
        compressed_pairs = []
        for term, doc_id in original_pairs:
            compressed_terms = self.compress_term(term)
            for compressed_term in compressed_terms:
                if compressed_term:
                    compressed_pairs.append((compressed_term, doc_id))
        
        for term, doc_id in compressed_pairs:
            if term not in self.postings_list:
                self.postings_list[term] = []
            if doc_id not in self.postings_list[term]:
                self.postings_list[term].append(doc_id)
        
        for term in self.postings_list:
            self.postings_list[term].sort(key=int)
    
    def compress_term(self, term):
        tokens = [term]
        
        if self.compression_type == "no_numbers":
            tokens = self.compression.apply_no_numbers(tokens)
        elif self.compression_type == "case_folding":
            tokens = self.compression.apply_case_folding(tokens)
        elif self.compression_type == "stop_words_30":
            tokens = self.compression.apply_stop_words_30(tokens)
        elif self.compression_type == "stop_words_150":
            tokens = self.compression.apply_stop_words_150(tokens)
        elif self.compression_type == "stemming":
            tokens = self.compression.apply_stemming(tokens)
        elif self.compression_type == "all":
            tokens = self.compression.apply_no_numbers(tokens)
            tokens = self.compression.apply_case_folding(tokens)
            tokens = self.compression.apply_stop_words_150(tokens)
            tokens = self.compression.apply_stemming(tokens)
        return tokens
    
    def get_statistics(self):
        distinct_terms = len(self.postings_list)
        
        total_postings = 0
        
        for postings in self.postings_list.values():
            total_postings += len(postings)
        
        return {
            'distinct_terms': distinct_terms,
            'total_postings': total_postings
        }
    
    def search_term(self, term):
        compressed_terms = self.compress_term(term.lower().strip())
        if compressed_terms and compressed_terms[0]:
            return self.postings_list.get(compressed_terms[0], [])
        return []
    
    def search_and_query(self, terms):
        if not terms:
            return []
        
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

def generate_compression_table(naive_indexer):
    print("DICTIONARY COMPRESSION TABLE (Reuters-21578)")
    
    compression_types = [
        "unfiltered",
        "no_numbers", 
        "case_folding",
        "stop_words_30",
        "stop_words_150",
        "stemming",
        "all"
    ]
    
    results = {}
    
    unfiltered_stats = naive_indexer.get_statistics()
    baseline = {
        'distinct_terms': unfiltered_stats['vocabulary_size'],
        'total_postings': unfiltered_stats['total_term_document_pairs'],
    }
    
    results['unfiltered'] = baseline
    
    # Apply each compression technique
    for compression_type in compression_types[1:]:
        print(f"Processing {compression_type}")
        compressed_indexer = CompressedIndexer(naive_indexer, compression_type)
        results[compression_type] = compressed_indexer.get_statistics()
    
    # Print table
    print(f"{'Technique':<15} {'Terms':<12} {'Postings':<12}")
    
    for technique in compression_types:
        stats = results[technique]
        print(f"{technique:<15} {stats['distinct_terms']:<12} {stats['total_postings']:<12}")
    
    return results

def compare_query_results(naive_indexer, compression_results):
    print("QUERY RESULTS COMPARISON")
    
    # Test queries from Subproject II
    test_queries = {
        'single': ["movie", "samsung", "apple"],
        'and': [
            ["movie", "oppenheimer", "viacom"],
            ["gold", "stock"], 
            ["trade", "market", "oil"]
        ]
    }
    
    compression_types = ["no_numbers", "case_folding", "stop_words_30", "stop_words_150", "stemming"]
    
    print("\nSINGLE TERM QUERIES:")
    
    for query in test_queries['single']:
        print(f"\nQuery: '{query}'")
        original_results = naive_indexer.search_term(query)
        print(f"  Original: {len(original_results)} documents")
        
        for compression_type in compression_types:
            compressed_indexer = CompressedIndexer(naive_indexer, compression_type)
            compressed_results = compressed_indexer.search_term(query)
            print(f"  {compression_type}: {len(compressed_results)} documents")
    
    print("\nAND QUERIES:")
    
    for query_terms in test_queries['and']:
        query_str = " AND ".join(query_terms)
        print(f"\nQuery: '{query_str}'")
        original_results = naive_indexer.search_and_query(query_terms)
        print(f"  Original: {len(original_results)} documents")
        
        for compression_type in compression_types:
            compressed_indexer = CompressedIndexer(naive_indexer, compression_type)
            compressed_results = compressed_indexer.search_and_query(query_terms)
            print(f"  {compression_type}: {len(compressed_results)} documents")

if __name__ == "__main__":
    naive_indexer = NaiveIndexer(dataset_path="./reuters21578")
    
    # Generate compression table
    compression_results = generate_compression_table(naive_indexer)
    
    # Compare query results
    compare_query_results(naive_indexer, compression_results)