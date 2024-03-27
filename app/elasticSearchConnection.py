from typing import List
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever, SentenceTransformersRanker
from haystack.nodes import EmbeddingRetriever
from haystack import Pipeline

from app.mapper import PostType

ELASTIC_PASSWORD = "<password>"

document_store = ElasticsearchDocumentStore(
    host = "174.129.61.40",
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
    def updateEmbeddingNewData(filterParam, updateExistingEmbedding):
        AutoMatching.document_store.update_embeddings(
        retriever=AutoMatching.embeddingRetriever, 
        filters=filterParam, 
        update_existing_embeddings= updateExistingEmbedding
    )

    @staticmethod
    def getDocumentById(postId, postType:PostType):
        document = None

        postId = int(postId)
        document = AutoMatching.document_store.get_document_by_id("{0}_{1}".format(postType.name, postId))

        return document
    
    @staticmethod
    def searchDocuments(inputQuery, contextQuery, filterParam):
        userInput = inputQuery
        fullContextQuery = userInput + contextQuery

        # keywordRetriever = BM25Retriever(document_store)
        # keywordRetrieverPipeline = Pipeline()
        # keywordRetrieverPipeline.add_node(component=keywordRetriever, name="Retriever", inputs=["Query"])
        # keywordRetrieverPipelineOutput = keywordRetrieverPipeline.run(
        #     query=userInput,
        #     params={
        #         "Retriever": {
        #             "top_k": 3
        #         }
        #     }
        # )

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
                },
                "filters": filterParam
            }
        )

        # retrieverOutputWithDuplicate = [document for document in keywordRetrieverPipelineOutput["documents"]] + [document for document in embeddingRetrieverPipelineOutput["documents"] if document.score > 0.4]
        
        # retrieverOutput = []
        retrieverOutput = embeddingRetrieverPipelineOutput['documents'] if embeddingRetrieverPipelineOutput['documents'] is not None else []
        # retrieverOutput = [document for document in retrieverOutput if document.score > 0.6]
        # countList = []
        # for document in retrieverOutputWithDuplicate:
        #     if  document.meta['id'] not in countList:
        #         countList.append(document.meta['id'])
        #         retrieverOutput.append(document)

        # print("combination", retrieverOutput)

        if len(retrieverOutput) == 0:
            return None

        ranker = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2")
        retrieverRankerPipeline = Pipeline()
        retrieverRankerPipeline.add_node(component=ranker, name="Ranker", inputs=["Query"])
        result = retrieverRankerPipeline.run(
            query= fullContextQuery,
            documents=retrieverOutput
        )

        print(result)
        return result
    
    def searchRelatedDocuments(inputQuery, filterParam):
        userInput = inputQuery

        embeddingRetriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model="sentence-transformers/all-mpnet-base-v2",
            model_format="sentence_transformers",
            scale_score= False
        )
        embeddingRetrieverPipeline = Pipeline()
        embeddingRetrieverPipeline.add_node(component=embeddingRetriever, name="Retriever", inputs=["Query"])
        result = embeddingRetrieverPipeline.run(
            query=userInput,
            params={
                "Retriever": {
                    "top_k": 10
                },
                "filters": filterParam
            }
        )

        # print(result)
        # retrieverOutput = [document for document in retrieverOutput if document.score > 0.6]
        return result

    @staticmethod
    def deleteDocument(postResponseDto):
        
        postTypeName = PostType(str(postResponseDto["postType"])).name if "postType" in postResponseDto else PostType.project.name
        postId = "{0}_{1}".format(postTypeName,postResponseDto["id"])

        indexName = "document",
        ids= [postId]
        document_store.delete_documents(index=indexName,ids=ids)