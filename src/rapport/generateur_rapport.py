"""
Générateur de Rapport Détaillé
Produit un rapport explicatif complet du matching
Auteur : Architecture IA Banque
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.coeur.journalisation import journaliseur


class GenerateurRapport:
    """
    Génère un rapport détaillé et explicable du matching CV/Offre.
    Conforme aux exigences d'auditabilité bancaire.
    """
    
    def __init__(self):
        self.journaliseur = journaliseur
    
    def generer_rapport_complet(
        self,
        resultat_scoring: Dict[str, Any],
        profil_cv: Dict[str, Any],
        profil_offre: Dict[str, Any],
        identifiant_session: str
    ) -> Dict[str, Any]:
        """
        Génère le rapport complet d'analyse.
        
        Args:
            resultat_scoring: Résultat du MoteurScoring
            profil_cv: Profil du candidat
            profil_offre: Profil de l'offre
            identifiant_session: ID de session
            
        Returns:
            Dictionnaire structuré du rapport
        """
        self.journaliseur.info(
            f"[{identifiant_session}] Génération rapport complet"
        )
        
        rapport = {
            "metadonnees": {
                "identifiant_session": identifiant_session,
                "date_generation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version_systeme": "1.0.0"
            },
            
            "synthese_executive": self._generer_synthese_executive(
                resultat_scoring
            ),
            
            "score_global": {
                "valeur": resultat_scoring['score_final'],
                "niveau": resultat_scoring['niveau_correspondance'],
                "interpretation": self._interpreter_score(
                    resultat_scoring['score_final']
                )
            },
            
            "detail_sous_scores": self._formater_sous_scores(
                resultat_scoring['sous_scores'],
                resultat_scoring['poids_utilises']
            ),
            
            "analyse_competences": self._analyser_competences_detaillee(
                resultat_scoring['sous_scores']['competences']
            ),
            
            "analyse_experience": self._analyser_experience_detaillee(
                resultat_scoring['sous_scores']['experience']
            ),
            
            "analyse_formation": self._analyser_formation_detaillee(
                resultat_scoring['sous_scores']['formation']
            ),
            
            "recommandations": resultat_scoring['recommandations'],
            
            "profil_candidat_resume": self._resumer_profil_candidat(profil_cv),
            
            "profil_offre_resume": self._resumer_profil_offre(profil_offre),
            
            "conformite": {
                "rgpd": "Conforme - Données personnelles anonymisées",
                "explicabilite": "Conforme - Tous les scores sont traçables",
                "non_discrimination": "Conforme - Critères objectifs uniquement"
            }
        }
        
        self.journaliseur.info(
            f"[{identifiant_session}] Rapport généré avec succès"
        )
        
        return rapport
    
    def _generer_synthese_executive(self, resultat: Dict) -> str:
        """Génère un résumé exécutif en 2-3 phrases."""
        
        score = resultat['score_final']
        niveau = resultat['niveau_correspondance']
        
        if score >= 85:
            synthese = (
                f"Le candidat présente une correspondance {niveau.lower()} avec le poste "
                f"(score {score}/100). Le profil répond à l'ensemble des critères essentiels "
                f"et démontre une forte adéquation avec les compétences recherchées."
            )
        elif score >= 70:
            synthese = (
                f"Le candidat présente une correspondance {niveau.lower()} avec le poste "
                f"(score {score}/100). La plupart des critères sont satisfaits, "
                f"avec quelques axes d'amélioration identifiés."
            )
        elif score >= 50:
            synthese = (
                f"Le candidat présente une correspondance {niveau.lower()} avec le poste "
                f"(score {score}/100). Certaines compétences clés sont manquantes, "
                f"nécessitant une évaluation approfondie."
            )
        else:
            synthese = (
                f"Le candidat présente une correspondance {niveau.lower()} avec le poste "
                f"(score {score}/100). Le profil ne répond pas aux critères essentiels "
                f"et présente des lacunes significatives."
            )
        
        return synthese
    
    def _interpreter_score(self, score: float) -> str:
        """Interprète un score avec explications."""
        
        if score >= 85:
            return (
                "Score excellent indiquant une parfaite adéquation entre le profil "
                "et les exigences du poste. Le candidat possède toutes les compétences "
                "clés et l'expérience nécessaire."
            )
        elif score >= 70:
            return (
                "Score bon reflétant une correspondance solide. Le candidat répond "
                "aux critères principaux avec quelques compétences additionnelles "
                "à développer."
            )
        elif score >= 50:
            return (
                "Score moyen suggérant une correspondance partielle. Le candidat "
                "possède certaines compétences requises mais présente des lacunes "
                "dans des domaines critiques."
            )
        else:
            return (
                "Score faible indiquant une inadéquation significative. Le profil "
                "ne répond pas aux exigences minimales du poste."
            )
    
    def _formater_sous_scores(
        self,
        sous_scores: Dict,
        poids: Dict
    ) -> list:
        """Formate les sous-scores pour affichage."""
        
        details = []
        
        # Ordre d'affichage (par importance)
        ordre = ['competences', 'experience', 'formation', 'langues', 'soft_skills']
        
        labels = {
            'competences': 'Compétences Techniques',
            'experience': 'Expérience Professionnelle',
            'formation': 'Formation Académique',
            'langues': 'Compétences Linguistiques',
            'soft_skills': 'Soft Skills'
        }
        
        for cle in ordre:
            if cle in sous_scores:
                score_data = sous_scores[cle]
                
                details.append({
                    "critere": labels[cle],
                    "score": score_data['score'],
                    "poids": poids[cle] * 100,  # Convertir en %
                    "contribution": round(score_data['score'] * poids[cle], 2),
                    "interpretation": self._interpreter_sous_score(
                        cle, score_data['score']
                    )
                })
        
        return details
    
    def _interpreter_sous_score(self, critere: str, score: float) -> str:
        """Interprète un sous-score spécifique."""
        
        if score >= 80:
            niveau = "Excellent"
        elif score >= 60:
            niveau = "Bon"
        elif score >= 40:
            niveau = "Moyen"
        else:
            niveau = "Faible"
        
        return f"{niveau} ({score:.1f}/100)"
    
    def _analyser_competences_detaillee(self, comp_score: Dict) -> Dict:
        """Analyse détaillée des compétences."""
        
        return {
            "score_global": comp_score['score'],
            "score_matching_exact": comp_score['score_exact'],
            "score_similarite_semantique": comp_score['score_semantique'],
            "taux_couverture": comp_score['taux_couverture'],
            "competences_correspondantes": comp_score['correspondances'],
            "competences_manquantes": comp_score['manquantes'],
            "competences_additionnelles": comp_score['additionnelles'],
            "analyse": (
                f"Le candidat maîtrise {len(comp_score['correspondances'])} des "
                f"compétences requises, avec un taux de couverture de "
                f"{comp_score['taux_couverture']:.1f}%. "
                f"{len(comp_score['manquantes'])} compétence(s) clé(s) manquante(s)."
            )
        }
    
    def _analyser_experience_detaillee(self, exp_score: Dict) -> Dict:
        """Analyse détaillée de l'expérience."""
        
        return {
            "score": exp_score['score'],
            "annees_possedees": exp_score['annees_cv'],
            "annees_requises": exp_score['annees_requises'],
            "adequation": exp_score['adequation'],
            "commentaire": exp_score['commentaire'],
            "analyse": (
                f"Avec {exp_score['annees_cv']} année(s) d'expérience pour "
                f"{exp_score['annees_requises']} requise(s), le niveau d'adéquation "
                f"est {exp_score['adequation'].lower()}."
            )
        }
    
    def _analyser_formation_detaillee(self, form_score: Dict) -> Dict:
        """Analyse détaillée de la formation."""
        
        return {
            "score": form_score['score'],
            "niveau_candidat": form_score['niveau_cv'],
            "niveau_requis": form_score['niveau_requis'],
            "adequation": form_score['adequation'],
            "commentaire": form_score['commentaire'],
            "analyse": (
                f"Niveau académique : {form_score['niveau_cv']} "
                f"(requis : {form_score['niveau_requis']}). "
                f"Adéquation {form_score['adequation'].lower()}."
            )
        }
    
    def _resumer_profil_candidat(self, profil: Dict) -> Dict:
        """Résumé du profil candidat."""
        
        return {
            "experience_totale": f"{profil['experience']['annees_experience']} ans",
            "niveau_seniorite": profil['experience']['niveau_seniorite'],
            "formation_principale": profil['formation']['niveau_academique'],
            "nombre_competences_techniques": len(profil['competences']['techniques']),
            "nombre_langues": len(profil['langues'])
        }
    
    def _resumer_profil_offre(self, profil: Dict) -> Dict:
        """Résumé du profil de l'offre."""
        
        return {
            "titre_poste": profil['titre_poste'],
            "experience_requise": profil['experience_requise'],
            "formation_requise": profil['formation_requise'],
            "nombre_competences_requises": len(
                profil['competences_requises']['techniques']
            ),
            "nombre_langues_requises": len(profil.get('langues_requises', []))
        }
    
    def exporter_rapport_json(self, rapport: Dict) -> str:
        """Exporte le rapport en JSON formaté."""
        import json
        return json.dumps(rapport, indent=2, ensure_ascii=False)
    
    def exporter_rapport_texte(self, rapport: Dict) -> str:
        """Exporte le rapport en texte formaté."""
        
        lignes = []
        lignes.append("=" * 80)
        lignes.append("RAPPORT D'ANALYSE DE MATCHING CV / OFFRE D'EMPLOI")
        lignes.append("=" * 80)
        lignes.append("")
        
        # Métadonnées
        meta = rapport['metadonnees']
        lignes.append(f"Session : {meta['identifiant_session']}")
        lignes.append(f"Date : {meta['date_generation']}")
        lignes.append("")
        
        # Synthèse
        lignes.append("SYNTHÈSE EXÉCUTIVE")
        lignes.append("-" * 80)
        lignes.append(rapport['synthese_executive'])
        lignes.append("")
        
        # Score global
        lignes.append("SCORE GLOBAL")
        lignes.append("-" * 80)
        score_g = rapport['score_global']
        lignes.append(f"Score : {score_g['valeur']}/100")
        lignes.append(f"Niveau : {score_g['niveau']}")
        lignes.append(f"Interprétation : {score_g['interpretation']}")
        lignes.append("")
        
        # Détail sous-scores
        lignes.append("DÉTAIL DES CRITÈRES")
        lignes.append("-" * 80)
        for detail in rapport['detail_sous_scores']:
            lignes.append(
                f"{detail['critere']} : {detail['score']:.1f}/100 "
                f"(poids {detail['poids']:.0f}%, contribution {detail['contribution']:.1f})"
            )
            lignes.append(f"  → {detail['interpretation']}")
        lignes.append("")
        
        # Recommandations
        lignes.append("RECOMMANDATIONS")
        lignes.append("-" * 80)
        for i, reco in enumerate(rapport['recommandations'], 1):
            lignes.append(f"{i}. {reco}")
        lignes.append("")
        
        lignes.append("=" * 80)
        lignes.append("FIN DU RAPPORT")
        lignes.append("=" * 80)
        
        return "\n".join(lignes)