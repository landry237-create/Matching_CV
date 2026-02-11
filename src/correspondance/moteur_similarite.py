"""
Moteur de similarité cosinus.
"""

import numpy as np
from numpy.linalg import norm
from typing import List, Dict, Optional, Any

def similarite_cosinus(vec1, vec2) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs.
    Retourne un score entre 0 et 1.
    """
    if norm(vec1) == 0 or norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm(vec1) * norm(vec2)))
