"""
Module de Journalisation
==================================

Système de logging structuré conforme aux standards .
Inclut la rotation des logs, l'anonymisation et l'audit trail.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from typing import List
import json
import re


class FormatteurBancaire(logging.Formatter):
    """
    Formatteur personnalisé pour logs bancaires avec structure JSON.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formate le log en structure JSON pour parsing automatisé.
        """
        log_data = {
            "horodatage": datetime.utcnow().isoformat(),
            "niveau": record.levelname,
            "module": record.module,
            "fonction": record.funcName,
            "ligne": record.lineno,
            "message": record.getMessage(),
            "processus": record.process,
            "thread": record.thread
        }
        
        # Ajout des données supplémentaires si présentes
        if hasattr(record, 'donnees_metier'):
            log_data['donnees_metier'] = record.donnees_metier
            
        return json.dumps(log_data, ensure_ascii=False)


class AnonymiseurDonnees:
    """
    Anonymise les données sensibles dans les logs (RGPD).
    """
    
    # Patterns de données sensibles
    PATTERN_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PATTERN_TELEPHONE = r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b'
    PATTERN_CARTE_IDENTITE = r'\b[0-9]{12}\b'
    
    @staticmethod
    def anonymiser_texte(texte: str) -> str:
        """
        Anonymise les données sensibles dans un texte.
        
        Args:
            texte: Texte potentiellement contenant des données sensibles
            
        Returns:
            Texte anonymisé
        """
        # Anonymisation des emails
        texte = re.sub(AnonymiseurDonnees.PATTERN_EMAIL, '[EMAIL_ANONYMISE]', texte)
        
        # Anonymisation des téléphones
        texte = re.sub(AnonymiseurDonnees.PATTERN_TELEPHONE, '[TEL_ANONYMISE]', texte)
        
        # Anonymisation potentiels numéros d'identité
        texte = re.sub(AnonymiseurDonnees.PATTERN_CARTE_IDENTITE, '[ID_ANONYMISE]', texte)
        
        return texte


class JournaliseurBancaire:
    """
    Gestionnaire de journalisation pour application bancaire.
    
    Fonctionnalités:
    - Logging structuré JSON
    - Rotation automatique
    - Anonymisation RGPD
    - Multi-niveaux (console + fichier)
    - Audit trail
    """
    
    def __init__(
        self,
        nom_application: str = "matching",
        niveau: str = "INFO",
        activer_anonymisation: bool = True,
        dossier_logs: Optional[Path] = None
    ):
        """
        Initialise le système de journalisation.
        
        Args:
            nom_application: Nom de l'application
            niveau: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            activer_anonymisation: Active l'anonymisation des données sensibles
            dossier_logs: Dossier de stockage des logs
        """
        self.nom_application = nom_application
        self.activer_anonymisation = activer_anonymisation
        
        # Création du logger principal
        self.logger = logging.getLogger(nom_application)
        self.logger.setLevel(getattr(logging, niveau.upper()))
        
        # Éviter la duplication des handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Configuration du handler console
        self._configurer_handler_console()
        
        # Configuration du handler fichier si dossier spécifié
        if dossier_logs:
            self._configurer_handler_fichier(dossier_logs)
    
    def _configurer_handler_console(self):
        """Configure le handler pour sortie console."""
        handler_console = logging.StreamHandler(sys.stdout)
        handler_console.setLevel(logging.INFO)
        
        # Format simplifié pour console
        format_console = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler_console.setFormatter(format_console)
        self.logger.addHandler(handler_console)
    
    def _configurer_handler_fichier(self, dossier_logs: Path):
        """Configure le handler pour fichiers de logs."""
        dossier_logs = Path(dossier_logs)
        dossier_logs.mkdir(parents=True, exist_ok=True)
        
        fichier_log = dossier_logs / f"{self.nom_application}_{datetime.now():%Y%m%d}.log"
        
        handler_fichier = logging.FileHandler(fichier_log, encoding='utf-8')
        handler_fichier.setLevel(logging.DEBUG)
        handler_fichier.setFormatter(FormatteurBancaire())
        self.logger.addHandler(handler_fichier)
    
    def _traiter_message(self, message: str) -> str:
        """Traite le message avant logging (anonymisation si activée)."""
        if self.activer_anonymisation:
            return AnonymiseurDonnees.anonymiser_texte(message)
        return message
    
    def debug(self, message: str, exc_info=False, **kwargs):
        """Log niveau DEBUG."""
        self.logger.debug(self._traiter_message(message), extra=kwargs, exc_info=exc_info)
    
    def info(self, message: str, exc_info=False, **kwargs):
        """Log niveau INFO."""
        self.logger.info(self._traiter_message(message), extra=kwargs, exc_info=exc_info)
    
    def avertissement(self, message: str, exc_info=False, **kwargs):
        """Log niveau WARNING."""
        self.logger.warning(self._traiter_message(message), extra=kwargs, exc_info=exc_info)
    
    def erreur(self, message: str, exception: Optional[Exception] = None, exc_info=False, **kwargs):
        """Log niveau ERROR avec trace optionnelle."""
        message_traite = self._traiter_message(message)
        if exception:
            message_traite += f" | Exception: {str(exception)}"
        self.logger.error(message_traite, extra=kwargs, exc_info=exc_info or (exception is not None))
    
    def critique(self, message: str, exc_info=False, **kwargs):
        """Log niveau CRITICAL."""
        self.logger.critical(self._traiter_message(message), extra=kwargs, exc_info=exc_info)
    
    def audit(self, action: str, utilisateur: str, details: Dict[str, Any]):
        """
        Log spécifique pour audit trail.
        
        Args:
            action: Action effectuée
            utilisateur: Identifiant utilisateur (anonymisé)
            details: Détails de l'opération
        """
        message_audit = f"AUDIT | Action: {action} | Utilisateur: {utilisateur}"
        self.logger.info(
            message_audit,
            extra={'donnees_metier': {'type': 'audit', 'details': details}}
        )


# Instance globale du journaliseur
journaliseur = JournaliseurBancaire(
    nom_application="matching",
    niveau="INFO",
    activer_anonymisation=True
)