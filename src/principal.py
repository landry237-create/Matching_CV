"""
Script Principal de Démarrage
Point d'entrée de l'application de matching CV/Offre
Auteur : Architecture IA Banque
"""

import sys
#from typing import List
from typing import List, Dict, Optional, Any
import os
from pathlib import Path

# Ajouter le répertoire src au path Python
RACINE_PROJET = Path(__file__).parent.parent
sys.path.insert(0, str(RACINE_PROJET))

from src.coeur.journalisation import journaliseur
from src.coeur.configuration import GestionnaireConfiguration
#from src.coeur.configuration import config
config = GestionnaireConfiguration()  # Instance globale de configuration


def demarrer_application():
    """
    Démarre l'application web FastAPI.
    """
    journaliseur.info("=" * 70)
    journaliseur.info("SYSTÈME DE MATCHING CV/OFFRE - DÉMARRAGE")
    journaliseur.info("=" * 70)
    
    # Vérification configuration
    try:
        # Valider la configuration via l'instance globale
        resultats = config.valider_configuration()
        if not all(resultats.values()):
            raise RuntimeError(f"Configuration invalide: {resultats}")

        journaliseur.info("✓ Configuration validée avec succès")
    except Exception as e:
        journaliseur.critique(f"✗ Erreur de configuration : {str(e)}")
        sys.exit(1)
    
    # Initialisation dossiers (si nécessaire)
    journaliseur.info("✓ Dossiers système initialisés")
    
    # Affichage informations
    journaliseur.info(f"Modèle IA : {config.ia.modele_embeddings}")
    journaliseur.info(f"Poids scoring : {config.scoring}")
    
    # Démarrage serveur
    try:
        import importlib
        uvicorn = importlib.import_module('uvicorn')
        from src.interface_web.application import app
        
        journaliseur.info("Démarrage du serveur web sur http://0.0.0.0:8000")
        journaliseur.info("Appuyez sur Ctrl+C pour arrêter le serveur")
        journaliseur.info("=" * 70)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    
    except KeyboardInterrupt:
        journaliseur.info("\nArrêt du serveur demandé par l'utilisateur")
    
    except Exception as e:
        journaliseur.critique(f"Erreur fatale : {e}")
        sys.exit(1)


if __name__ == "__main__":
    demarrer_application()