import re
import os
from tqdm import tqdm
from xml.sax.saxutils import unescape

class ReutersDocument:    
    # To store individual document details and extract the content with ease
    def __init__(self, doc_id, title, body, date_loc, author):
        self.doc_id = doc_id
        self.title = title
        self.body = body
        self.date_loc = date_loc
        self.author = author
    
    def get_content(self):
        content = []
        if self.title:
            content.append(self.title)
        if self.date_loc:
            content.append(self.date_loc)
        if self.author:
            content.append(self.author)
        if self.body:
            content.append(self.body)
        return " ".join(content)
    
    def __str__(self):
        return f"Document {self.doc_id}: {len(self.get_content())} characters"


class ReutersParser:    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.documents = []
        self.parse_all_files()
    
    def clean_text(self, text):
        if not text:
            return ""
        
        # Replace all HTML/XML entities with original characters
        text = unescape(text)
        
        # Remove control characters and extra whitespace
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_text_content(self, text_element):
        # Extract title, body, date_loc, and author from text element.
        title = ""
        body = ""
        date_loc = ""
        author = ""
        
        title_match = re.search(r'<TITLE>(.*?)</TITLE>', text_element, re.DOTALL)
        if title_match:
            title = self.clean_text(title_match.group(1))
        
        body_match = re.search(r'<BODY>(.*?)</BODY>', text_element, re.DOTALL)
        if body_match:
            body = self.clean_text(body_match.group(1))
        
        dateline_match = re.search(r'<DATELINE>(.*?)</DATELINE>', text_element, re.DOTALL)
        if dateline_match:
            date_loc = self.clean_text(dateline_match.group(1))
        
        author_match = re.search(r'<AUTHOR>(.*?)</AUTHOR>', text_element, re.DOTALL)
        if author_match:
            author = self.clean_text(author_match.group(1))
        
        return title, body, date_loc, author
    
    def parse_file(self, filename):
        documents = []
        filepath = os.path.join(self.dataset_path, filename)
    
        with open(filepath, 'r', encoding='latin-1') as file:
                content = file.read()
        
        # Find all Reuters elements
        reuters_pattern = r'<REUTERS[^>]*?NEWID="(\d+)"[^>]*?>(.*?)</REUTERS>'
        
        for match in re.finditer(reuters_pattern, content, re.DOTALL):
            newid = match.group(1)
            reuters_content = match.group(2)
            
            # Extract the text element
            text_match = re.search(r'<TEXT[^>]*?>(.*?)</TEXT>', reuters_content, re.DOTALL)
            
            if text_match:
                text_content = text_match.group(1)
                title, body, date_loc, author = self.extract_text_content(text_content)                
                
            documents.append(ReutersDocument(newid, title, body, date_loc, author))

        return documents

    def parse_all_files(self):
        # Get all .sgm files
        sgm_files = [f for f in os.listdir(self.dataset_path) if f.endswith('.sgm')]
        
        print(f"Processing files")
        for file in tqdm(sgm_files):
            self.documents.extend(self.parse_file(file))

if __name__ == "__main__":
    # Test the parser
    parser = ReutersParser(dataset_path="./reuters21578")

    print(f"\nTotal documents: {len(parser.documents)}")

    while True:
        try:
            doc_id = int(input(f"\nEnter a document ID between 1 and {len(parser.documents)} (0 to exit): "))
            if doc_id == 0:
                break
            if 1 <= doc_id <= len(parser.documents):
                print(f"\nDocument {doc_id} content:\n")
                print(parser.documents[doc_id - 1].get_content())
            else:
                print("Invalid document ID. Please try again.")
        except ValueError:
            print("Please enter a valid integer.")