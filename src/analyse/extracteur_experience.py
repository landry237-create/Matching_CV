"""
Extracteur d'Expérience Professionnelle
========================================

Module d'extraction et d'analyse de l'expérience professionnelle
depuis un CV ou une offre d'emploi.
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.coeur.journalisation import journaliseur


class ExtracteurExperience:
    """
    Extracteur d'expérience professionnelle.
    
    Capacités:
    - Détection des années d'expérience
    - Identification des postes occupés
    - Extraction des durées
    - Analyse du niveau de séniorité
    """
    
    # Patterns de détection
    PATTERN_ANNEES_EXP = r"(\d+)\s*(?:ans?|années?)\s*(?:d['’])?(?:expérience|exp)"
    PATTERN_DUREE = r"(\d{4})\s*[-–]\s*(\d{4}|présent|aujourd'hui|actuel)"
    
    # Niveaux de séniorité
    NIVEAUX_SENIORITE = {
        'junior': 1,
        'confirmé': 2,
        'senior': 3,
        'expert': 4,
        'lead': 4,
        'principal': 4,
        'chef': 4,
        'manager': 4,
        'directeur': 5
    }
    
    def __init__(self):
        """Initialise l'extracteur d'expérience."""
        journaliseur.debug("Extracteur d'expérience initialisé")

    def _normaliser_texte(self, texte) -> str:
        """
        Assure que la variable passée est bien une chaîne.
        Accepte un dict (ex. profil) et tente d'en extraire le texte pertinent.
        """
        if isinstance(texte, str):
            return texte
        if isinstance(texte, dict):
            # Priorité aux clés courantes
            for cle in ('texte_complet', 'texte', 'description'):
                if cle in texte and isinstance(texte[cle], str):
                    return texte[cle]
            # Si contient années directement, retourner représentation
            return ' '.join(str(v) for v in texte.values())
        return str(texte)
    
    def extraire_annees_experience(self, texte: str) -> Optional[int]:
        """
        Extrait le nombre d'années d'expérience mentionné.
        
        Args:
            texte: Texte du CV ou de l'offre
            
        Returns:
            Nombre d'années d'expérience ou None
        """
        texte = self._normaliser_texte(texte)
        texte_normalise = texte.lower()
        
        # Recherche du pattern d'années d'expérience
        matches = re.findall(self.PATTERN_ANNEES_EXP, texte_normalise)
        
        if matches:
            # Prend la première ou la plus grande valeur trouvée
            annees = [int(m) for m in matches]
            annees_max = max(annees)
            
            journaliseur.info(f"Années d'expérience détectées: {annees_max}")
            return annees_max
        
        # Tentative de calcul à partir des périodes
        annees_calculees = self._calculer_experience_depuis_periodes(texte)
        if annees_calculees:
            journaliseur.info(
                f"Années d'expérience calculées depuis périodes: {annees_calculees}"
            )
            return annees_calculees
        
        journaliseur.avertissement("Aucune année d'expérience trouvée")
        return None
    
    def _calculer_experience_depuis_periodes(self, texte: str) -> Optional[int]:
        """
        Calcule l'expérience totale à partir des périodes détectées.
        
        Args:
            texte: Texte contenant potentiellement des périodes
            
        Returns:
            Nombre d'années total ou None
        """
        texte = self._normaliser_texte(texte)
        matches = re.findall(self.PATTERN_DUREE, texte)
        
        if not matches:
            return None
        
        annee_actuelle = datetime.now().year
        total_annees = 0
        
        for debut, fin in matches:
            annee_debut = int(debut)
            
            # Gestion de "présent", "aujourd'hui", etc.
            if fin.isdigit():
                annee_fin = int(fin)
            else:
                annee_fin = annee_actuelle
            
            # Validation
            if annee_debut <= annee_fin <= annee_actuelle:
                duree = annee_fin - annee_debut
                total_annees += duree
        
        return total_annees if total_annees > 0 else None
    
    def extraire_experience(self, texte: str) -> Dict[str, any]:
        """
        Extrait toutes les informations d'expérience du texte.
        
        Args:
            texte: Texte du CV ou de l'offre
            
        Returns:
            Dictionnaire avec années et niveau de séniorité
        """
        texte = self._normaliser_texte(texte)
        annees = self.extraire_annees_experience(texte)
        seniorite = self.detecter_niveau_seniorite(texte)
        
        return {
            'annees_experience': annees or 0,
            'niveau_seniorite': seniorite,
            'postes_detectes': []  # À enrichir si nécessaire
        }
    
    def calculer_adequation_experience(
        self,
        experience_cv: Dict,
        experience_requise: str
    ) -> Dict[str, Any]:
        """
        Calcule l'adéquation entre l'expérience du CV et celle requise.
        
        Args:
            experience_cv: Dictionnaire d'expérience du CV
            experience_requise: String décrivant l'expérience requise
            
        Returns:
            Dictionnaire avec score et détails
        """
        annees_cv = experience_cv.get('annees_experience', 0)
        
        # Extraire années requises du texte
        experience_requise = self._normaliser_texte(experience_requise)
        match = re.search(r'(\d+)\s*(?:\+|à|a)\s*(\d+)?', experience_requise)
        if match:
            annees_min = int(match.group(1))
            annees_max = int(match.group(2)) if match.group(2) else annees_min + 5
        else:
            annees_min = 0
            annees_max = 5
        
        # Calculer score
        if annees_cv >= annees_max:
            score = 100
            adequation = "Surqualifié"
        elif annees_cv >= annees_min:
            score = 80 + (annees_cv - annees_min) * 20 / (annees_max - annees_min)
            adequation = "Adéquat"
        elif annees_cv >= annees_min * 0.5:
            score = 50 + (annees_cv - annees_min * 0.5) * 30 / (annees_min * 0.5)
            adequation = "Légèrement en-dessous"
        else:
            score = max(0, annees_cv * 50 / (annees_min * 0.5))
            adequation = "Insuffisant"
        
        return {
            'score': min(100, round(score, 2)),
            'annees_cv': annees_cv,
            'annees_requises': f"{annees_min}-{annees_max}",
            'adequation': adequation,
            'commentaire': f"{annees_cv} ans - Requis: {annees_min}-{annees_max} ans"
        }
    
    def detecter_niveau_seniorite(self, texte: str) -> Dict[str, any]:
        """
        Détecte le niveau de séniorité mentionné.

        Args:
            texte: Texte à analyser

        Returns:
            Dictionnaire avec niveau et score
        """
        texte = self._normaliser_texte(texte)
        texte_normalise = texte.lower()

        # Recherche de tous les indicateurs de séniorité
        niveaux_trouves = []
        for niveau, score in self.NIVEAUX_SENIORITE.items():
            pattern = r'\\b' + re.escape(niveau) + r'\\b'
            if re.search(pattern, texte_normalise):
                niveaux_trouves.append((niveau, score))

        if niveaux_trouves:
            # Prend le niveau le plus élevé
            niveau_max = max(niveaux_trouves, key=lambda x: x[1])

            journaliseur.info(f"Niveau de séniorité détecté: {niveau_max[0]}")

            return {
                'niveau': niveau_max[0],
                'score': niveau_max[1],
                'tous_niveaux': [n[0] for n in niveaux_trouves]
            }

        journaliseur.debug("Aucun niveau de séniorité explicite détecté")
        return {
            'niveau': 'non_specifie',
            'score': 0,
            'tous_niveaux': []
        }
    
    def analyser_experience(self, texte: str) -> Dict[str, any]:
        """
        Analyse complète de l'expérience professionnelle.
        
        Args:
            texte: Texte du CV ou de l'offre
            
        Returns:
            Dictionnaire complet d'analyse
        """
        annees_experience = self.extraire_annees_experience(texte)
        seniorite = self.detecter_niveau_seniorite(texte)
        
        # Score d'expérience normalisé (0-100)
        score_experience = self._calculer_score_experience(
            annees_experience,
            seniorite['score']
        )
        
        resultat = {
            'annees_experience': annees_experience,
            'niveau_seniorite': seniorite,
            'score_experience': score_experience,
            'niveau_adequation': self._determiner_niveau_adequation(annees_experience)
        }
        
        journaliseur.info(
            f"Analyse expérience terminée: {annees_experience} ans, "
            f"niveau {seniorite['niveau']}, score {score_experience:.1f}"
        )
        
        return resultat
    
    def _calculer_score_experience(
        self,
        annees: Optional[int],
        score_seniorite: int
    ) -> float:
        """
        Calcule un score normalisé d'expérience.
        
        Args:
            annees: Nombre d'années d'expérience
            score_seniorite: Score de séniorité (0-5)
            
        Returns:
            Score entre 0 et 100
        """
        if annees is None:
            return 50.0  # Score neutre par défaut
        
        # Score basé sur les années (plafonné à 15 ans = 100%)
        score_annees = min(100, (annees / 15) * 100)
        
        # Bonus de séniorité (max +20%)
        bonus_seniorite = (score_seniorite / 5) * 20
        
        score_total = min(100, score_annees + bonus_seniorite)
        
        return round(score_total, 2)
    
    def _determiner_niveau_adequation(self, annees: Optional[int]) -> str:
        """
        Détermine le niveau d'adéquation basé sur l'expérience.
        
        Args:
            annees: Nombre d'années d'expérience
            
        Returns:
            Niveau: 'debutant', 'intermediaire', 'experimente', 'expert'
        """
        if annees is None:
            return 'non_specifie'
        
        if annees < 2:
            return 'debutant'
        elif annees < 5:
            return 'intermediaire'
        elif annees < 10:
            return 'experimente'
        else:
            return 'expert'