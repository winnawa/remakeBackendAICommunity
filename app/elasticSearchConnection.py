# from typing import List
# from haystack.document_stores import ElasticsearchDocumentStore
# from haystack.nodes import EmbeddingRetriever

# ELASTIC_PASSWORD = "<password>"

# document_store = ElasticsearchDocumentStore(
#     host = "52.202.163.171",
#     port = 9200,
#     username="elasticsearch",
#     password= ELASTIC_PASSWORD,
# )

# class AutoMatching:
#     document_store = document_store
#     embeddingRetriever = EmbeddingRetriever(
#         document_store=document_store,
#         embedding_model="sentence-transformers/all-mpnet-base-v2",
#         model_format="sentence_transformers",
#         scale_score= False
#     )

#     @staticmethod
#     def indexNewData(documents: List[any]):
#         AutoMatching.document_store.write_documents(documents)
        
#     @staticmethod
#     def updateEmbeddingNewData():
#         AutoMatching.document_store.update_embeddings(
#         retriever=AutoMatching.embeddingRetriever, 
#         filters={}, 
#         update_existing_embeddings=False
#     )

