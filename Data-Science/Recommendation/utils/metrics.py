import numpy as np

def precision_at_k(recommended, relevant, k=10):
    if not recommended:
        return 0.0
    rec = [i for i,_ in recommended[:k]]
    hits = sum(1 for i in rec if i in relevant)
    return hits / float(k)

def recall_at_k(recommended, relevant, k=10):
    if not relevant:
        return 0.0
    rec = [i for i,_ in recommended[:k]]
    hits = sum(1 for i in rec if i in relevant)
    return hits / float(len(relevant))

def average_precision(recommended, relevant, k=10):
    rec = [i for i,_ in recommended[:k]]
    score = 0.0
    hits = 0
    for idx, item in enumerate(rec, start=1):
        if item in relevant:
            hits += 1
            score += hits / idx
    if hits == 0:
        return 0.0
    return score / hits

def dcg(recommended, relevant, k=10):
    rec = [i for i,_ in recommended[:k]]
    score = 0.0
    for idx, item in enumerate(rec, start=1):
        rel = 1.0 if item in relevant else 0.0
        score += rel / np.log2(idx + 1)
    return score

def ndcg(recommended, relevant, k=10):
    ideal_recs = list(relevant)[:k]  # ideal DCG with all hits front-loaded
    ideal = dcg([(i,1.0) for i in ideal_recs], set(relevant), k=k)
    if ideal == 0:
        return 0.0
    actual = dcg(recommended, set(relevant), k=k)
    return actual / ideal