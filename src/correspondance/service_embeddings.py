"""
Service d'Embeddings Sémantiques
Utilise Sentence Transformers pour encoder les textes
Auteur : Architecture IA Banque
"""

import numpy as np
from typing import List, Union, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
from src.coeur.configuration import Configuration, config
from src.coeur.journalisation import journaliseur


class ServiceEmbeddings:
    """
    Service centralisé pour générer des embeddings sémantiques.
    Utilise un modèle multilingue pré-entraîné.
    """
    
    # Singleton pour éviter recharges multiples du modèle
    _instance = None
    _modele = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceEmbeddings, cls).__new__(cls)
            cls._instance._initialiser()
        return cls._instance
    
    def _initialiser(self):
        """Initialise le modèle au premier appel."""
        self.journaliseur = journaliseur
        
        if self._modele is None:
            self.journaliseur.info(
                f"Chargement du modèle d'embeddings : {Configuration.MODELE_EMBEDDING}"
            )
            
            try:
                self._modele = SentenceTransformer(Configuration.MODELE_EMBEDDING)
                self.journaliseur.info("Modèle chargé avec succès")
            
            except Exception as e:
                self.journaliseur.critique(
                    f"Échec du chargement du modèle : {str(e)}",
                    exc_info=True
                )
                raise
    
    def encoder_texte(self, texte: Union[str, List[str]]) -> np.ndarray:
        """
        Encode un ou plusieurs textes en vecteurs d'embeddings.
        
        Args:
            texte: Texte unique (str) ou liste de textes (List[str])
            
        Returns:
            Vecteur(s) d'embeddings (numpy array)
            - Si texte unique : shape (dimension,)
            - Si liste : shape (n_textes, dimension)
        """
        if isinstance(texte, str):
            texte = [texte]
            return_unique = True
        else:
            return_unique = False
        
        try:
            # Génération des embeddings
            embeddings = self._modele.encode(
                texte,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # Normalisation L2 pour similarité cosinus
            )
            
            self.journaliseur.debug(
                f"Encodage réussi : {len(texte)} texte(s) → "
                f"embeddings shape {embeddings.shape}"
            )
            
            if return_unique:
                return embeddings[0]
            return embeddings
        
        except Exception as e:
            self.journaliseur.erreur(
                f"Erreur lors de l'encodage : {str(e)}",
                exc_info=True
            )
            raise
    
    def encoder_liste_competences(self, competences: List[str]) -> np.ndarray:
        """
        Encode une liste de compétences et retourne la moyenne.
        
        Utile pour créer une représentation vectorielle d'un profil complet.
        
        Args:
            competences: Liste de compétences
            
        Returns:
            Vecteur moyen des embeddings
        """
        if not competences:
            # Retourner un vecteur zéro si liste vide
            return np.zeros(Configuration.DIMENSION_EMBEDDING)
        
        # Encoder toutes les compétences
        embeddings = self.encoder_texte(competences)
        
        # Calculer la moyenne
        embedding_moyen = np.mean(embeddings, axis=0)
        
        # Renormaliser
        norme = np.linalg.norm(embedding_moyen)
        if norme > 0:
            embedding_moyen = embedding_moyen / norme
        
        return embedding_moyen
    
    def calculer_similarite_cosinus(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.
        
        Formule : cos(θ) = (A · B) / (||A|| × ||B||)
        Avec embeddings normalisés : cos(θ) = A · B
        
        Args:
            embedding1: Premier vecteur
            embedding2: Deuxième vecteur
            
        Returns:
            Similarité dans [0, 1] (0 = différent, 1 = identique)
        """
        # Produit scalaire (embeddings déjà normalisés)
        similarite = np.dot(embedding1, embedding2)
        
        # Assurer intervalle [0, 1]
        # (En théorie déjà le cas, mais sécurité numérique)
        similarite = np.clip(similarite, 0.0, 1.0)
        
        return float(similarite)
    
    def obtenir_top_k_similaires(
        self,
        query_embedding: np.ndarray,
        candidats_embeddings: List[np.ndarray],
        candidats_labels: List[str],
        k: int = 5
    ) -> List[tuple]:
        """
        Retourne les k candidats les plus similaires à la query.
        
        Args:
            query_embedding: Embedding de la requête
            candidats_embeddings: Liste d'embeddings candidats
            candidats_labels: Labels correspondants (noms des candidats)
            k: Nombre de résultats à retourner
            
        Returns:
            Liste de tuples (label, score_similarité) triée par score décroissant
        """
        if len(candidats_embeddings) != len(candidats_labels):
            raise ValueError("Nombre d'embeddings ≠ nombre de labels")
        
        # Calcul similarités
        similarites = [
            self.calculer_similarite_cosinus(query_embedding, emb)
            for emb in candidats_embeddings
        ]
        
        # Tri par score décroissant
        resultats = list(zip(candidats_labels, similarites))
        resultats.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner top-k
        return resultats[:k]