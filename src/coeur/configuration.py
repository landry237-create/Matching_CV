"""
Module de Configuration du Système de Matching
========================================================

Ce module centralise toutes les configurations du système,
incluant les pondérations de scoring, les paramètres IA,
et les constantes de sécurité.

Conforme aux standards de configuration.
"""

from typing import Dict, List
from typing import Dict, Optional, Any
from dataclasses import dataclass
import os


@dataclass
class ConfigurationScoring:
    """
    Configuration des pondérations pour le calcul du score de matching.
    
    Les pondérations reflètent l'importance relative de chaque critère
    dans le processus de recrutement.
    """
    poids_competences_techniques: float = 0.45  # 45%
    poids_experience: float = 0.25              # 25%
    poids_formation: float = 0.15               # 15%
    poids_langues: float = 0.10                 # 10%
    poids_soft_skills: float = 0.05             # 5%
    
    def valider(self) -> bool:
        """Vérifie que la somme des poids égale 1.0"""
        total = (
            self.poids_competences_techniques +
            self.poids_experience +
            self.poids_formation +
            self.poids_langues +
            self.poids_soft_skills
        )
        return abs(total - 1.0) < 0.001


@dataclass
class ConfigurationIA:
    """
    Configuration des paramètres d'intelligence artificielle.
    """
    modele_embeddings: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    seuil_similarite_minimum: float = 0.3
    taille_batch_embeddings: int = 32
    utiliser_cache: bool = True


@dataclass
class ConfigurationSecurite:
    """
    Paramètres de sécurité et conformité RGPD.
    """
    activer_journalisation: bool = True
    niveau_journalisation: str = "INFO"
    anonymiser_donnees_sensibles: bool = True
    duree_conservation_logs_jours: int = 90
    taille_max_fichier_mo: int = 10


class GestionnaireConfiguration:
    """
    Gestionnaire centralisé de configuration du système.
    
    Permet un accès unifié et validé à toutes les configurations.
    """
    
    def __init__(self):
        self.scoring = ConfigurationScoring()
        self.ia = ConfigurationIA()
        self.securite = ConfigurationSecurite()
        
        # Dictionnaires métiers pour extraction rule-based
        self.competences_techniques_banque = self._charger_competences_techniques()
        self.soft_skills_valorises = self._charger_soft_skills()
        self.niveaux_langues = ["A1", "A2", "B1", "B2", "C1", "C2", 
                               "débutant", "intermédiaire", "avancé", "courant", "bilingue"]
        
    def _charger_competences_techniques(self) -> List[str]:
        """
        Charge le référentiel des compétences techniques du secteur bancaire.
        """
        return [
            # Langages programmation
            "python", "java", "scala", "r", "sql", "c++", "javascript", "typescript",
            "c#", ".net", "go", "kotlin", "swift",
            
            # Data Science & IA
            "machine learning", "deep learning", "nlp", "data science", "big data",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
            "spark", "hadoop", "airflow", "mlflow",
            
            # Finance & Risque
            "risk management", "gestion des risques", "bâle iii", "bâle iv", "solvabilité",
            "var", "value at risk", "stress testing", "backtesting", "credit scoring",
            "kyc", "aml", "lutte anti-blanchiment", "compliance", "réglementation",
            "mifid", "ifrs", "sox", "gdpr", "rgpd",
            
            # Technologies
            "cloud", "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "gitlab", "ci/cd", "microservices", "api rest", "graphql",
            "kafka", "rabbitmq", "elasticsearch", "mongodb", "postgresql",
            "oracle", "cassandra", "redis",
            
            # Méthodes
            "agile", "scrum", "devops", "safe", "kanban", "lean",
            
            # Sécurité
            "cybersécurité", "sécurité informatique", "pki", "cryptographie",
            "authentification", "oauth", "saml", "pentest",
            
            # Business Intelligence
            "power bi", "tableau", "qlik", "sas", "alteryx", "talend",
            
            # Core Banking
            "swift", "sepa", "t2s", "payments", "paiements", "clearing",
            "settlement", "core banking", "temenos", "finastra"
        ]
    
    def _charger_soft_skills(self) -> List[str]:
        """
        Charge le référentiel des soft skills valorisées.
        """
        return [
            "leadership", "communication", "travail d'équipe", "collaboration",
            "autonomie", "rigueur", "analyse", "esprit d'analyse",
            "résolution de problèmes", "créativité", "innovation",
            "adaptabilité", "gestion du stress", "organisation",
            "sens du service", "orientation client", "pédagogie",
            "négociation", "persuasion", "esprit critique",
            "proactivité", "résilience", "éthique", "intégrité"
        ]
    
    def valider_configuration(self) -> Dict[str, bool]:
        """
        Valide l'ensemble de la configuration.
        
        Returns:
            Dictionnaire de validation par composant
        """
        resultats = {
            "scoring_valide": self.scoring.valider(),
            "ia_valide": len(self.ia.modele_embeddings) > 0,
            "securite_valide": self.securite.duree_conservation_logs_jours > 0
        }
        return resultats
    
    def obtenir_configuration_scoring(self) -> Dict[str, float]:
        """
        Retourne les poids de scoring sous forme de dictionnaire.
        """
        return {
            'competences': self.scoring.poids_competences_techniques,
            'experience': self.scoring.poids_experience,
            'formation': self.scoring.poids_formation,
            'langues': self.scoring.poids_langues,
            'soft_skills': self.scoring.poids_soft_skills
        }
    
    def obtenir_resume(self) -> str:
        """
        Génère un résumé de la configuration active.
        """
        return f"""
╔══════════════════════════════════════════════════════════════╗
║         CONFIGURATION SYSTÈME MATCHING                       ║
╚══════════════════════════════════════════════════════════════╝

📊 PONDÉRATIONS SCORING:
   • Compétences techniques : {self.scoring.poids_competences_techniques*100:.0f}%
   • Expérience            : {self.scoring.poids_experience*100:.0f}%
   • Formation             : {self.scoring.poids_formation*100:.0f}%
   • Langues               : {self.scoring.poids_langues*100:.0f}%
   • Soft skills           : {self.scoring.poids_soft_skills*100:.0f}%

🤖 PARAMÈTRES IA:
   • Modèle embeddings     : {self.ia.modele_embeddings.split('/')[-1]}
   • Seuil similarité min  : {self.ia.seuil_similarite_minimum}
   
🔒 SÉCURITÉ:
   • Anonymisation         : {'Activée' if self.securite.anonymiser_donnees_sensibles else 'Désactivée'}
   • Conservation logs     : {self.securite.duree_conservation_logs_jours} jours
   • Taille max fichier    : {self.securite.taille_max_fichier_mo} Mo

✓ Configuration validée et opérationnelle
        """


class Configuration:
    """
    Classe Configuration pour compatibilité rétroactive.
    Expose les attributs et méthodes attendus par le code existant.
    """
    
    # Constantes de seuils de scoring
    SEUIL_EXCELLENT = 0.80
    SEUIL_BON = 0.65
    SEUIL_MOYEN = 0.50
    
    # Modèle d'embeddings
    MODELE_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    DIMENSION_EMBEDDING = 384
    
    # Diplômes reconnus
    DIPLOMES_RECONNUS = [
        # Niveaux Bac+X
        "bac+2", "bac+3", "bac+4", "bac+5", "bac+6",
        "deug", "deust", "licence", "licence pro", "master", "mastère", "doctorat", "dut", "dts",
        # Diplômes français
        "diplôme d'ingénieur", "ingénieur", "école d'ingénieur",
        "diplôme de commerce", "école de commerce",
        "bts", "dut", "iut",
        # Internationaux
        "bachelor", "bsc", "ba", "bs",
        "master of science", "msc", "ma", "ms", "mba",
        "phd", "doctorate"
    ]
    
    # Langues reconnues
    LANGUES_RECONNUES = [
        "français", "anglais", "allemand", "espagnol", "italien",
        "portugais", "néerlandais", "belge", "suisse",
        "chinois", "japonais", "coréen", "arabe", "russe",
        "hindi", "bengali", "thaï", "vietnamien"
    ]
    
    # Niveaux de langues
    NIVEAUX_LANGUES = [
        "A1", "A2", "B1", "B2", "C1", "C2",
        "débutant", "intermédiaire", "avancé", "courant", "bilingue", "natif"
    ]
    
    @staticmethod
    def obtenir_configuration_scoring() -> Dict[str, float]:
        """
        Retourne les poids de scoring.
        """
        return config.obtenir_configuration_scoring()
    
    @staticmethod
    def valider_configuration() -> Dict[str, bool]:
        """
        Valide la configuration complète.
        """
        return config.valider_configuration()


# Instance globale de configuration (singleton pattern)
config = GestionnaireConfiguration()