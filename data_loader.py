from langchain_community.document_loaders import PyPDFLoader 
from docx import Document 

def load_cv(file): 
    loader = PyPDFLoader(file)
    pages = loader.load() 
    page_content = ""

    for i in range(len(pages)):
        page_content += pages[i].page_content

    return page_content

def write_to_docx(text):
    print(text) 
    doc = Document()
    paragraphs = text.split("\n")
    for para in paragraphs:
        doc.add_paragraph(para)
    
    filename = "tmp/cover_letter.docx"
    doc.save(filename)
    print(f"Document saved as : {filename}")
    return filename