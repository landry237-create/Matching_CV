"""
Extracteur de Compétences
==========================

Module d'extraction des compétences techniques et soft skills
depuis un CV ou une offre d'emploi.

Utilise une approche hybride: rule-based + NLP.
"""

import re
from typing import Optional, Any
from typing import List, Set, Dict, Tuple
from collections import Counter
from src.coeur.configuration import config
from src.coeur.journalisation import journaliseur


class ExtracteurCompetences:
    """
    Extracteur de compétences techniques et soft skills.
    
    Méthodes:
    - Correspondance exacte avec dictionnaire
    - Extraction par patterns
    - Normalisation et déduplication
    """
    
    def __init__(self):
        """Initialise l'extracteur avec les référentiels de compétences."""
        self.competences_techniques_ref = set(
            comp.lower() for comp in config.competences_techniques_banque
        )
        self.soft_skills_ref = set(
            skill.lower() for skill in config.soft_skills_valorises
        )
        
        journaliseur.debug(
            f"Extracteur initialisé: {len(self.competences_techniques_ref)} "
            f"compétences techniques, {len(self.soft_skills_ref)} soft skills"
        )
    
    def extraire_competences_techniques(self, texte: str) -> List[Dict[str, any]]:
        """
        Extrait les compétences techniques d'un texte.
        
        Args:
            texte: Texte du CV ou de l'offre
            
        Returns:
            Liste de dictionnaires {competence, confiance, mentions}
        """
        texte_normalise = texte.lower()
        competences_trouvees = []
        
        # Recherche par correspondance exacte
        for competence in self.competences_techniques_ref:
            # Pattern pour détecter la compétence (avec délimiteurs de mot)
            pattern = r'\b' + re.escape(competence) + r'\b'
            matches = re.findall(pattern, texte_normalise)
            
            if matches:
                # Calcul du nombre de mentions
                nb_mentions = len(matches)
                
                # Score de confiance basé sur le nombre de mentions
                confiance = min(1.0, 0.6 + (nb_mentions - 1) * 0.1)
                
                competences_trouvees.append({
                    'competence': competence,
                    'confiance': confiance,
                    'mentions': nb_mentions,
                    'type': 'technique'
                })
        
        # Tri par confiance décroissante
        competences_trouvees.sort(key=lambda x: x['confiance'], reverse=True)
        
        journaliseur.info(
            f"Extraction compétences techniques: {len(competences_trouvees)} trouvées"
        )
        
        return competences_trouvees
    
    def extraire_soft_skills(self, texte: str) -> List[Dict[str, any]]:
        """
        Extrait les soft skills d'un texte.
        
        Args:
            texte: Texte du CV ou de l'offre
            
        Returns:
            Liste de dictionnaires {competence, confiance, mentions}
        """
        texte_normalise = texte.lower()
        soft_skills_trouvees = []
        
        for skill in self.soft_skills_ref:
            pattern = r'\b' + re.escape(skill) + r'\b'
            matches = re.findall(pattern, texte_normalise)
            
            if matches:
                nb_mentions = len(matches)
                confiance = min(1.0, 0.5 + (nb_mentions - 1) * 0.15)
                
                soft_skills_trouvees.append({
                    'competence': skill,
                    'confiance': confiance,
                    'mentions': nb_mentions,
                    'type': 'soft_skill'
                })
        
        soft_skills_trouvees.sort(key=lambda x: x['confiance'], reverse=True)
        
        journaliseur.info(
            f"Extraction soft skills: {len(soft_skills_trouvees)} trouvées"
        )
        
        return soft_skills_trouvees
    
    def extraire_toutes_competences(self, texte: str) -> Dict[str, List[Dict]]:
        """
        Extrait toutes les compétences (techniques + soft skills).
        
        Args:
            texte: Texte à analyser
            
        Returns:
            Dictionnaire avec clés 'techniques' et 'soft_skills'
        """
        return {
            'techniques': self.extraire_competences_techniques(texte),
            'soft_skills': self.extraire_soft_skills(texte)
        }
    
    def calculer_correspondance(
        self,
        competences_cv: List[Dict],
        competences_offre: List[Dict]
    ) -> Dict[str, float]:
        """
        Calcule le taux de correspondance entre compétences CV et offre.
        
        Args:
            competences_cv: Liste des compétences du CV
            competences_offre: Liste des compétences requises
            
        Returns:
            Dictionnaire avec taux_couverture et détails
        """
        if not competences_offre:
            return {'taux_couverture': 100.0, 'correspondantes': [], 'manquantes': [], 'additionnelles': []}
        
        # Extraire les noms de compétences
        noms_cv = set(c['competence'].lower() for c in competences_cv)
        noms_offre = set(c['competence'].lower() for c in competences_offre)
        
        # Trouver les correspondances exactes
        correspondances = noms_cv & noms_offre
        
        # Calculer le taux de couverture
        taux_couverture = (len(correspondances) / len(noms_offre)) * 100 if noms_offre else 0
        
        return {
            'taux_couverture': min(100, taux_couverture),
            'correspondantes': list(correspondances),
            'manquantes': list(noms_offre - correspondances),
            'additionnelles': list(noms_cv - noms_offre)
        }
    
    def obtenir_competences_principales(
        self,
        competences: List[Dict],
        top_n: int = 10
    ) -> List[str]:
        """
        Retourne les N compétences principales.
        
        Args:
            competences: Liste de compétences extraites
            top_n: Nombre de compétences à retourner
            
        Returns:
            Liste des noms de compétences
        """
        return [comp['competence'] for comp in competences[:top_n]]