import pytest
from app.services.search_service import cosine_similarity

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert cosine_similarity(v1, v2) == 1.0

    v3 = [0.0, 1.0, 0.0]
    assert cosine_similarity(v1, v3) == 0.0

    v4 = [1.0, 1.0, 0.0]
    # dot_product = 1, norm_v1 = 1, norm_v4 = sqrt(2) = 1.414
    # sim = 1 / 1.414 = 0.707
    sim = cosine_similarity(v1, v4)
    assert round(sim, 3) == 0.707

    assert cosine_similarity([], []) == 0.0
