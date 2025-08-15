from . import RAGPreProcess
from . import LLMProcess
# Benzer parçaları bulma fonksiyonu


def retrieve_similar_chunks(query, index, chunks, model, top_k, threshold):
    query_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype('float32')
    distances, indices = index.search(query_vec, top_k)

    results = []
    for j, i in enumerate(indices[0]):
        score = distances[0][j]
        if (threshold is None) or (score >= threshold):
            results.append((chunks[i], score))

    return results


def InterProcess(query, index, all_chunks, model, top_k, threshold):
    results = retrieve_similar_chunks(query=query, index=index, chunks=all_chunks, model=model, top_k=top_k, threshold=threshold)
    print(results)

    context_texts = [chunk for chunk, score in results]

    prompt = LLMProcess.RAG_build_prompt(question=query, context_chunks=context_texts)
    return LLMProcess.generate_answer(prompt=prompt)

def sorgula(query: str, top_k = 5, threshold = 0.8):
    model, index, all_chunks = RAGPreProcess.main()
    result = InterProcess(query=query, index=index, all_chunks=all_chunks, model=model, top_k=top_k, threshold=threshold)
    print("\n\nLLM SONRASI:\n"+result)
    return result

def retrieve_context_chunks(query, index, chunks, model, top_k, threshold):
    query_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype('float32')
    distances, indices = index.search (query_vec, top_k)

    results = []
    for j, i in enumerate(indices[0]):
        score = distances[0][j]
        if (threshold is None) or (score >= threshold):
            results.append(chunks[i])

    return results


def get_context_chunks(query: str, top_k=5, threshold=0.8):
    model, index, all_chunks = RAGPreProcess.main()
    context_chunks = retrieve_context_chunks(query, index, all_chunks, model, top_k, threshold)
    return context_chunks