from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchParams, FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

env = {
    "host": "localhost",
    "port": 6333,
    "collection": "aparts"
}

client = QdrantClient(env["host"], port=env["port"])
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def add_vector(id: int, vector: list, meta: dict = None, collection: str = env["collection"]):
    client.upsert(
        collection_name=collection,
        points=[PointStruct(
            id = id, 
            vector = vector,
            payload=meta
        )]
    )

def search(query, top_k: int = 5, search_filter = {}, truth: int = 128, exact: bool = False, collection: str = env["collection"]):
    if isinstance(query, dict):
        query = encode(query)

    qdrant_filter = None
    if search_filter:
        conditions = []
        for key, value in search_filter.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value.lower())
                )
            )
        qdrant_filter = Filter(must=conditions)

    res = client.search(
        collection_name=collection,
        query_vector=query,
        limit=top_k,
        search_params=SearchParams(hnsw_ef=truth, exact=exact),
        query_filter=qdrant_filter
    )
    return [(point.id, point.score) for point in res]

def encode(feature: dict):
    text = " ".join([f"{key}: {value}" for key, value in feature.items()])
    vector = model.encode(text).tolist()
    return vector
# нужно ЕЩЕ КОЛЛЕКЦИЮ СОЗДАТЬ