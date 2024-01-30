from typing import List
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever, SentenceTransformersRanker
from haystack.nodes import EmbeddingRetriever
from haystack import Pipeline

ELASTIC_PASSWORD = "<password>"

document_store = ElasticsearchDocumentStore(
    host = "54.224.142.171",
    port = 9200,
    username="elasticsearch",
    password= ELASTIC_PASSWORD,
)

class AutoMatching:
    document_store = document_store
    embeddingRetriever = EmbeddingRetriever(
        document_store=document_store,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        model_format="sentence_transformers",
        scale_score= False
    )

    @staticmethod
    def indexNewData(documents: List[any]):
        AutoMatching.document_store.write_documents(documents)
        
    @staticmethod
    def updateEmbeddingNewData():
        AutoMatching.document_store.update_embeddings(
        retriever=AutoMatching.embeddingRetriever, 
        filters={}, 
        update_existing_embeddings=False
    )

    @staticmethod
    def searchDocuments(inputQuery, contextQuery):
        userInput = inputQuery
        fullContextQuery = userInput + contextQuery

        keywordRetriever = BM25Retriever(document_store)
        keywordRetrieverPipeline = Pipeline()
        keywordRetrieverPipeline.add_node(component=keywordRetriever, name="Retriever", inputs=["Query"])
        keywordRetrieverPipelineOutput = keywordRetrieverPipeline.run(
            query=userInput,
            params={
                "Retriever": {
                    "top_k": 3
                }
            }
        )

        embeddingRetriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model="sentence-transformers/all-mpnet-base-v2",
            model_format="sentence_transformers",
            scale_score= False
        )
        embeddingRetrieverPipeline = Pipeline()
        embeddingRetrieverPipeline.add_node(component=embeddingRetriever, name="Retriever", inputs=["Query"])
        embeddingRetrieverPipelineOutput = embeddingRetrieverPipeline.run(
            query=userInput,
            params={
                "Retriever": {
                    "top_k": 5
                }
            }
        )

        retrieverOutputWithDuplicate = [document for document in keywordRetrieverPipelineOutput["documents"]] + [document for document in embeddingRetrieverPipelineOutput["documents"] if document.score > 0.4]
        retrieverOutput = []
        countList = []
        for document in retrieverOutputWithDuplicate:
            if  document.meta['id'] not in countList:
                countList.append(document.meta['id'])
                retrieverOutput.append(document)

        print("combination", retrieverOutput)

        ranker = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2")
        retrieverRankerPipeline = Pipeline()
        retrieverRankerPipeline.add_node(component=ranker, name="Ranker", inputs=["Query"])
        result = retrieverRankerPipeline.run(
            query= fullContextQuery,
            documents=retrieverOutput
        )

        print(result)
        return result
