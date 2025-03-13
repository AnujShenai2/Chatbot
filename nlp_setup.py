import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from entity_fetch import makers_list, models_list, variants_list, years_list, fuel_type_list, category_list, sub_category_list

# NLP setup
documents = makers_list + models_list + variants_list + years_list + fuel_type_list + category_list + sub_category_list
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
document_embeddings = np.array(embedding_model.encode(documents, convert_to_numpy=True))
embedding_dim = document_embeddings.shape[1]

faiss_index = faiss.IndexFlatL2(embedding_dim)
faiss_index.add(document_embeddings)

bm25 = BM25Okapi([doc.split() for doc in documents])