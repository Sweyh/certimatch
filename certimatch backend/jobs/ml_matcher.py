"""
ML-based job matcher using the TF-IDF model from job_model_1_.pkl
"""
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

_model_cache = None


def _load_model():
    global _model_cache
    if _model_cache is None:
        from django.conf import settings
        with open(settings.ML_MODEL_PATH, 'rb') as f:
            _model_cache = pickle.load(f)
    return _model_cache


def get_top_matches(user_skills: list, top_n: int = 10) -> list:
    """
    Given a list of user skills, return top_n job matches sorted by similarity.
    Returns a list of dicts: {job_title, company, skills_required, salary_lpa, score}
    """
    model       = _load_model()
    tfidf       = model['tfidf']
    tfidf_matrix = model['tfidf_matrix']
    df          = model['df']

    skills_str  = ' '.join(user_skills)
    user_vector = tfidf.transform([skills_str])
    scores      = cosine_similarity(user_vector, tfidf_matrix).flatten()

    top_indices = scores.argsort()[::-1][:top_n]
    results = []
    for idx in top_indices:
        row = df.iloc[idx]
        results.append({
            'job_title':        row['job_title'],
            'company':          row['company'],
            'skills_required':  row['skills_required'],
            'salary_lpa':       round(float(row['salary_lpa']), 2),
            'match_score':      round(float(scores[idx]) * 100, 1),
        })
    return results
