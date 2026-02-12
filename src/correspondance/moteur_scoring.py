"""
Moteur de Scoring CV ↔ Offre
Calcule le score final pondéré et explicable
Auteur : Architecture IA Banque
"""

from typing import Dict, Any, List, Optional
import numpy as np
from src.coeur.configuration import Configuration
from src.coeur.journalisation import journaliseur
from src.correspondance.service_embeddings import ServiceEmbeddings
from src.analyse.extracteur_competences import ExtracteurCompetences
from src.analyse.extracteur_experience import ExtracteurExperience
from src.analyse.extracteur_formation import ExtracteurFormation


class MoteurScoring:
    """
    Moteur principal de calcul du score de correspondance CV/Offre.
    Combine approches rule-based et ML (embeddings) avec pondération explicable.
    """
    
    def __init__(self):
        self.journaliseur = journaliseur
        self.service_embeddings = ServiceEmbeddings()
        self.extracteur_competences = ExtracteurCompetences()
        self.extracteur_experience = ExtracteurExperience()
        self.extracteur_formation = ExtracteurFormation()
        
        # Chargement des poids depuis configuration
        self.poids = Configuration.obtenir_configuration_scoring()
    
    def calculer_score_global(
        self,
        profil_cv: Dict[str, Any],
        profil_offre: Dict[str, Any],
        identifiant_session: str
    ) -> Dict[str, Any]:
        """
        Calcule le score global de correspondance CV ↔ Offre.
        
        Args:
            profil_cv: Dictionnaire retourné par AnalyseurCV
            profil_offre: Dictionnaire retourné par AnalyseurOffre
            identifiant_session: ID de session pour traçabilité
            
        Returns:
            Dictionnaire avec score final et détails de chaque composante
        """
        self.journaliseur.info(
            f"[{identifiant_session}] Début calcul scoring"
        )
        
        try:
            # ═══════════════════════════════════════════════════════════
            # CALCUL DES SOUS-SCORES
            # ═══════════════════════════════════════════════════════════
            
            # 1. Score Compétences (45%)
            score_competences = self._calculer_score_competences(
                profil_cv, profil_offre
            )
            
            # 2. Score Expérience (25%)
            score_experience = self._calculer_score_experience(
                profil_cv, profil_offre
            )
            
            # 3. Score Formation (15%)
            score_formation = self._calculer_score_formation(
                profil_cv, profil_offre
            )
            
            # 4. Score Langues (10%)
            score_langues = self._calculer_score_langues(
                profil_cv, profil_offre
            )
            
            # 5. Score Soft Skills (5%)
            score_soft_skills = self._calculer_score_soft_skills(
                profil_cv, profil_offre
            )
            
            # ═══════════════════════════════════════════════════════════
            # CALCUL SCORE FINAL PONDÉRÉ
            # ═══════════════════════════════════════════════════════════
            
            score_final = (
                score_competences['score'] * self.poids['competences'] +
                score_experience['score'] * self.poids['experience'] +
                score_formation['score'] * self.poids['formation'] +
                score_langues['score'] * self.poids['langues'] +
                score_soft_skills['score'] * self.poids['soft_skills']
            )
            
            score_final = round(score_final, 2)
            
            # ═══════════════════════════════════════════════════════════
            # DÉTERMINATION NIVEAU CORRESPONDANCE
            # ═══════════════════════════════════════════════════════════
            
            if score_final >= Configuration.SEUIL_EXCELLENT:
                niveau = "Excellent"
                couleur = "#28a745"  # Vert
            elif score_final >= Configuration.SEUIL_BON:
                niveau = "Bon"
                couleur = "#17a2b8"  # Bleu clair
            elif score_final >= Configuration.SEUIL_MOYEN:
                niveau = "Moyen"
                couleur = "#ffc107"  # Jaune/Orange
            else:
                niveau = "Faible"
                couleur = "#dc3545"  # Rouge
            
            # ═══════════════════════════════════════════════════════════
            # CONSTRUCTION DU RÉSULTAT COMPLET
            # ═══════════════════════════════════════════════════════════
            
            resultat = {
                "score_final": score_final,
                "niveau_correspondance": niveau,
                "couleur_affichage": couleur,
                "sous_scores": {
                    "competences": score_competences,
                    "experience": score_experience,
                    "formation": score_formation,
                    "langues": score_langues,
                    "soft_skills": score_soft_skills
                },
                "poids_utilises": self.poids,
                "recommandations": self._generer_recommandations(
                    score_final,
                    score_competences,
                    score_experience,
                    score_formation
                )
            }
            
            # Journalisation du résultat
            self.journaliseur.info(
                f"[{identifiant_session}] Scoring terminé : {score_final}/100 ({niveau})"
            )
            
            return resultat
        
        except Exception as e:
            self.journaliseur.erreur(
                f"[{identifiant_session}] Erreur lors du scoring : {str(e)}",
                exc_info=True
            )
            raise
    
    def _calculer_score_competences(
        self,
        profil_cv: Dict,
        profil_offre: Dict
    ) -> Dict[str, Any]:
        """
        Calcule le score de correspondance des compétences techniques.
        
        Méthode hybride :
        1. Matching exact (70%) : ratio compétences communes / requises
        2. Similarité sémantique (30%) : embeddings
        """
        comp_cv = profil_cv['competences']['techniques']
        comp_offre = profil_offre['competences_requises']['techniques']
        
        # ─────────────────────────────────────────────────────────
        # PARTIE 1 : Matching exact (70%)
        # ─────────────────────────────────────────────────────────
        
        correspondance = self.extracteur_competences.calculer_correspondance(
            comp_cv, comp_offre
        )
        
        taux_couverture = correspondance['taux_couverture']
        score_exact = min(100, taux_couverture)  # Plafonner à 100
        
        # ─────────────────────────────────────────────────────────
        # PARTIE 2 : Similarité sémantique (30%)
        # ─────────────────────────────────────────────────────────
        
        if comp_cv and comp_offre:
            # Encoder listes de compétences
            emb_cv = self.service_embeddings.encoder_liste_competences(comp_cv)
            emb_offre = self.service_embeddings.encoder_liste_competences(comp_offre)
            
            # Similarité cosinus
            similarite = self.service_embeddings.calculer_similarite_cosinus(
                emb_cv, emb_offre
            )
            score_semantique = similarite * 100
        else:
            score_semantique = 0.0
        
        # ─────────────────────────────────────────────────────────
        # SCORE FINAL HYBRIDE
        # ─────────────────────────────────────────────────────────
        
        score_final = score_exact * 0.7 + score_semantique * 0.3
        
        return {
            "score": round(score_final, 2),
            "score_exact": round(score_exact, 2),
            "score_semantique": round(score_semantique, 2),
            "correspondances": correspondance['correspondantes'],
            "manquantes": correspondance['manquantes'],
            "additionnelles": correspondance['additionnelles'][:10],  # Limiter
            "taux_couverture": correspondance['taux_couverture']
        }
    
    def _calculer_score_experience(
        self,
        profil_cv: Dict,
        profil_offre: Dict
    ) -> Dict[str, Any]:
        """Calcule le score d'expérience professionnelle."""
        
        experience_cv = profil_cv['experience']
        experience_requise = profil_offre['experience_requise']
        
        adequation = self.extracteur_experience.calculer_adequation_experience(
            experience_cv,
            experience_requise
        )
        
        return {
            "score": adequation['score'],
            "annees_cv": adequation['annees_cv'],
            "annees_requises": adequation['annees_requises'],
            "adequation": adequation['adequation'],
            "commentaire": adequation['commentaire']
        }
    
    def _calculer_score_formation(
        self,
        profil_cv: Dict,
        profil_offre: Dict
    ) -> Dict[str, Any]:
        """Calcule le score de formation académique."""
        
        formation_cv = profil_cv['formation']
        formation_requise = profil_offre['formation_requise']
        
        adequation = self.extracteur_formation.calculer_adequation_formation(
            formation_cv,
            formation_requise
        )
        
        return {
            "score": adequation['score'],
            "niveau_cv": adequation['niveau_cv'],
            "niveau_requis": adequation['niveau_requis'],
            "adequation": adequation['adequation'],
            "commentaire": adequation['commentaire']
        }
    
    def _calculer_score_langues(
        self,
        profil_cv: Dict,
        profil_offre: Dict
    ) -> Dict[str, Any]:
        """Calcule le score de correspondance des langues."""
        
        langues_cv = profil_cv.get('langues', [])
        langues_requises = profil_offre.get('langues_requises', [])
        
        if not langues_requises:
            # Si pas d'exigence linguistique, score neutre
            return {
                "score": 100.0,
                "langues_cv": [l['langue'] for l in langues_cv],
                "langues_requises": [],
                "commentaire": "Aucune exigence linguistique spécifiée"
            }
        
        # Vérifier couverture des langues requises
        langues_cv_set = set(l['langue'].lower() for l in langues_cv)
        langues_req_set = set(l['langue'].lower() for l in langues_requises)
        
        intersection = langues_cv_set & langues_req_set
        
        if len(langues_req_set) > 0:
            taux_couverture = len(intersection) / len(langues_req_set) * 100
        else:
            taux_couverture = 100
        
        # Bonus si langues supplémentaires
        langues_bonus = langues_cv_set - langues_req_set
        bonus = min(10, len(langues_bonus) * 5)  # Max +10 pts
        
        score = min(100, taux_couverture + bonus)
        
        return {
            "score": round(score, 2),
            "langues_cv": [l['langue'] for l in langues_cv],
            "langues_requises": [l['langue'] for l in langues_requises],
            "langues_correspondantes": list(intersection),
            "langues_manquantes": list(langues_req_set - langues_cv_set),
            "commentaire": f"{len(intersection)}/{len(langues_req_set)} langue(s) requise(s) maîtrisée(s)"
        }
    
    def _calculer_score_soft_skills(
        self,
        profil_cv: Dict,
        profil_offre: Dict
    ) -> Dict[str, Any]:
        """Calcule le score des soft skills."""
        
        soft_cv = profil_cv['competences']['soft_skills']
        soft_offre = profil_offre['competences_requises']['soft_skills']
        
        if not soft_offre:
            # Pas d'exigence = score neutre
            return {
                "score": 100.0,
                "soft_skills_cv": [s['competence'] if isinstance(s, dict) else s for s in soft_cv],
                "soft_skills_requises": [],
                "commentaire": "Aucune soft skill spécifiée dans l'offre"
            }
        
        # Correspondance - extraire le nom de chaque soft skill
        set_cv = set(s['competence'].lower() if isinstance(s, dict) else s.lower() for s in soft_cv)
        set_offre = set(s['competence'].lower() if isinstance(s, dict) else s.lower() for s in soft_offre)
        
        intersection = set_cv & set_offre
        
        if len(set_offre) > 0:
            taux = len(intersection) / len(set_offre) * 100
        else:
            taux = 100
        
        return {
            "score": round(taux, 2),
            "soft_skills_cv": [s['competence'] if isinstance(s, dict) else s for s in soft_cv],
            "soft_skills_requises": [s['competence'] if isinstance(s, dict) else s for s in soft_offre],
            "correspondantes": list(intersection),
            "manquantes": list(set_offre - set_cv),
            "commentaire": f"{len(intersection)}/{len(set_offre)} soft skill(s) identifiée(s)"
        }
    
    def _generer_recommandations(
        self,
        score_final: float,
        score_competences: Dict,
        score_experience: Dict,
        score_formation: Dict
    ) -> list:
        """
        Génère des recommandations basées sur les scores.
        
        Returns:
            Liste de recommandations actionnables
        """
        recommandations = []
        
        # Analyse globale
        if score_final >= 85:
            recommandations.append(
                "✅ Excellente correspondance ! Le candidat répond à tous les critères principaux."
            )
        elif score_final >= 70:
            recommandations.append(
                "✓ Bonne correspondance. Le candidat est qualifié pour le poste."
            )
        elif score_final >= 50:
            recommandations.append(
                "⚠ Correspondance moyenne. Certaines lacunes à combler."
            )
        else:
            recommandations.append(
                "❌ Correspondance faible. Profil peu adapté au poste."
            )
        
        # Recommandations spécifiques
        if score_competences['score'] < 60:
            nb_manquantes = len(score_competences['manquantes'])
            recommandations.append(
                f"🔧 {nb_manquantes} compétence(s) technique(s) manquante(s) critique(s). "
                f"Formation recommandée."
            )
        
        if score_experience['score'] < 60:
            recommandations.append(
                f"📅 Expérience insuffisante ({score_experience['annees_cv']} ans vs "
                f"{score_experience['annees_requises']} requis). Considérer comme profil junior."
            )
        
        if score_formation['score'] < 60:
            recommandations.append(
                f"🎓 Niveau de formation en dessous des attentes. "
                f"Évaluer les compétences acquises sur le terrain."
            )
        
        return recommandations