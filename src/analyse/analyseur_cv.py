"""
Analyseur de CV Complet
Orchestre tous les extracteurs pour produire une analyse structurée
Auteur : Architecture IA Banque
"""

import re
from typing import List, Optional
from typing import Dict, Any
from src.coeur.journalisation import journaliseur
from src.analyse.extracteur_competences import ExtracteurCompetences
from src.analyse.extracteur_experience import ExtracteurExperience
from src.analyse.extracteur_formation import ExtracteurFormation


class AnalyseurCV:
    """
    Analyse complète d'un CV en extrayant toutes les informations pertinentes.
    Coordonne les différents extracteurs spécialisés.
    """
    
    def __init__(self):
        self.journaliseur = journaliseur
        self.extracteur_competences = ExtracteurCompetences()
        self.extracteur_experience = ExtracteurExperience()
        self.extracteur_formation = ExtracteurFormation()
    
    def analyser(self, texte_cv: str, identifiant_session: str) -> Dict[str, Any]:
        """
        Analyse complète d'un CV.
        
        Args:
            texte_cv: Contenu textuel du CV
            identifiant_session: ID de session pour traçabilité
            
        Returns:
            Dictionnaire structuré avec toutes les informations extraites
        """
        self.journaliseur.info(f"[{identifiant_session}] Début analyse CV")
        
        try:
            # Prétraitement du texte
            texte_nettoye = self._pretraiter_texte(texte_cv)
            
            # ═══════════════════════════════════════════════════════════
            # EXTRACTION DES INFORMATIONS
            # ═══════════════════════════════════════════════════════════
            
            # 1. Informations personnelles (nom, contact)
            infos_personnelles = self._extraire_infos_personnelles(texte_nettoye)
            
            # 2. Compétences (techniques + soft skills)
            competences = self.extracteur_competences.extraire_toutes_competences(texte_nettoye)
            
            # 3. Expérience professionnelle
            experience = self.extracteur_experience.extraire_experience(texte_nettoye)
            
            # 4. Formation académique
            formation = self.extracteur_formation.extraire_formation(texte_nettoye)
            
            # 5. Langues
            langues = self._extraire_langues(texte_nettoye)
            
            # ═══════════════════════════════════════════════════════════
            # CONSTRUCTION DU PROFIL STRUCTURÉ
            # ═══════════════════════════════════════════════════════════
            
            profil_cv = {
                "informations_personnelles": infos_personnelles,
                "competences": competences,
                "experience": experience,
                "formation": formation,
                "langues": langues,
                "texte_complet": texte_nettoye,
                "longueur_caracteres": len(texte_nettoye)
            }
            
            self.journaliseur.info(
                f"[{identifiant_session}] Analyse CV terminée avec succès - "
                f"{len(competences['techniques'])} compétences techniques, "
                f"{experience['annees_experience']} ans d'exp, "
                f"{len(langues)} langues"
            )
            
            return profil_cv
        
        except Exception as e:
            self.journaliseur.erreur(
                f"[{identifiant_session}] Erreur lors de l'analyse CV : {str(e)}",
                exc_info=True
            )
            raise
    
    def _pretraiter_texte(self, texte: str) -> str:
        """
        Nettoie et normalise le texte du CV.
        
        Args:
            texte: Texte brut
            
        Returns:
            Texte nettoyé
        """
        # Suppression caractères spéciaux excessifs
        texte = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', texte)
        
        # Normalisation espaces multiples
        texte = re.sub(r'\s+', ' ', texte)
        
        # Normalisation sauts de ligne
        texte = re.sub(r'\n\s*\n', '\n', texte)
        
        return texte.strip()
    
    def _extraire_infos_personnelles(self, texte: str) -> Dict[str, Any]:
        """
        Extrait les informations personnelles (nom, email, téléphone).
        
        Note RGPD : Ces informations sont anonymisées dans les logs.
        
        Args:
            texte: Texte du CV
            
        Returns:
            Dictionnaire avec infos personnelles (partiellement masquées)
        """
        infos = {}
        
        # Email (pattern simple)
        pattern_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match_email = re.search(pattern_email, texte)
        if match_email:
            email = match_email.group(0)
            # Masquage partiel pour RGPD
            infos['email'] = self._masquer_email(email)
        
        # Téléphone (formats français + international)
        patterns_telephone = [
            r'\b0[1-9](?:[\s\.-]?\d{2}){4}\b',  # FR : 06 12 34 56 78
            r'\+33[\s\.]?[1-9](?:[\s\.-]?\d{2}){4}\b',  # FR international
            r'\+\d{1,3}[\s\.-]?\d{9,12}\b'  # International général
        ]
        
        for pattern in patterns_telephone:
            match_tel = re.search(pattern, texte)
            if match_tel:
                telephone = match_tel.group(0)
                # Masquage partiel
                infos['telephone'] = self._masquer_telephone(telephone)
                break
        
        # Nom (heuristique : premières lignes souvent nom/prénom)
        # Pas d'extraction robuste ici pour éviter erreurs
        # En production : utiliser NER (Named Entity Recognition)
        
        return infos
    
    def _masquer_email(self, email: str) -> str:
        """Masque partiellement un email pour RGPD."""
        partie_locale, domaine = email.split('@')
        if len(partie_locale) > 2:
            masque = partie_locale[0] + '*' * (len(partie_locale) - 2) + partie_locale[-1]
        else:
            masque = partie_locale[0] + '*'
        return f"{masque}@{domaine}"
    
    def _masquer_telephone(self, telephone: str) -> str:
        """Masque partiellement un téléphone pour RGPD."""
        chiffres_seuls = re.sub(r'\D', '', telephone)
        if len(chiffres_seuls) >= 4:
            return chiffres_seuls[:2] + '*' * (len(chiffres_seuls) - 4) + chiffres_seuls[-2:]
        return '*' * len(chiffres_seuls)
    
    def _extraire_langues(self, texte: str) -> List[Dict[str, str]]:
        """
        Extrait les langues parlées et leur niveau.
        
        Args:
            texte: Texte du CV
            
        Returns:
            Liste de dictionnaires {langue, niveau}
        """
        from src.coeur.configuration import Configuration
        
        langues_trouvees = []
        texte_minuscule = texte.lower()
        
        langues_ref = Configuration.LANGUES_RECONNUES
        niveaux_ref = Configuration.NIVEAUX_LANGUES
        
        for langue in langues_ref:
            # Recherche de la langue
            pattern_langue = r'\b' + re.escape(langue) + r'\b'
            match_langue = re.search(pattern_langue, texte_minuscule)
            
            if match_langue:
                # Recherche d'un niveau à proximité (50 caractères)
                debut = max(0, match_langue.start() - 50)
                fin = min(len(texte_minuscule), match_langue.end() + 50)
                contexte = texte_minuscule[debut:fin]
                
                niveau_trouve = None
                for niveau in niveaux_ref:
                    if niveau in contexte:
                        niveau_trouve = niveau
                        break
                
                if not niveau_trouve:
                    niveau_trouve = "non spécifié"
                
                langues_trouvees.append({
                    "langue": langue.capitalize(),
                    "niveau": niveau_trouve.capitalize()
                })
        
        return langues_trouvees