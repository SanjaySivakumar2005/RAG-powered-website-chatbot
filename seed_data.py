import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

def seed_claysys_data():
    print("🌱 Seeding high-quality ClaySys data into the vector store...")
    
    # Combined search results and industry/service lists
    data = [
        {
            "title": "ClaySys Overview",
            "url": "https://www.claysys.com/about-us",
            "content": "ClaySys serves a diverse range of industries, leveraging its expertise in custom software development and IT consulting. They have experience working with Fortune 50 to Fortune 500 companies, as well as smaller organizations. Their services include custom software development, IT consulting, digital marketing, and business process automation."
        },
        {
            "title": "Industries Served by ClaySys",
            "url": "https://www.claysys.com/industries",
            "content": "ClaySys serves various industries including Retail, Manufacturing, Financial Services (Banking), Healthcare, Professional Services, Transportation and Logistics, Contact Centers, and Energy. They provide specialized solutions like SAAS and custom CRM for these sectors."
        },
        {
            "title": "ClaySys Services",
            "url": "https://www.claysys.com/services",
            "content": "ClaySys provides a wide range of services: Custom Software Development, Mobile App Development, Cloud Computing Services, UI/UX Design, Digital Marketing, Artificial Intelligence and Machine Learning solutions, and Business Intelligence. They also offer the ClaySys AppForms platform for low-code application development."
        },
        {
            "title": "ClaySys AppForms",
            "url": "https://www.claysys.com/appforms",
            "content": "ClaySys AppForms is a low-code application development platform that allows users to create complex forms and applications without writing extensive code. It integrates deeply with SharePoint and other enterprise systems to automate business processes."
        }
    ]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create documents
    documents = []
    for item in data:
        doc = Document(
            page_content=item["content"],
            metadata={"title": item["title"], "url": item["url"]}
        )
        documents.append(doc)
    
    # Create and save FAISS index
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local("faiss_index")
    
    # Create metadata file (required by the current system)
    metadata = {
        'docstore': vector_store.docstore,
        'index_to_docstore_id': vector_store.index_to_docstore_id
    }
    with open("faiss_metadata.pkl", 'wb') as f:
        pickle.dump(metadata, f)
        
    print("✅ Successfully seeded ClaySys data! The bot will now answer correctly.")

if __name__ == "__main__":
    seed_claysys_data()
