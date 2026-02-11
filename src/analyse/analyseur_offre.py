"""
Analyseur d'Offre d'Emploi
Extrait les critères requis d'une offre
Auteur : Architecture IA Banque
"""

import re
from typing import Dict, Any, List, Optional
from src.coeur.journalisation import journaliseur
from src.analyse.extracteur_competences import ExtracteurCompetences


class AnalyseurOffre:
    """
    Analyse une offre d'emploi pour en extraire les critères de sélection.
    """
    
    def __init__(self):
        self.journaliseur = journaliseur
        self.extracteur_competences = ExtracteurCompetences()
    
    def analyser(self, texte_offre: str, identifiant_session: str) -> Dict[str, Any]:
        """
        Analyse complète d'une offre d'emploi.
        
        Args:
            texte_offre: Contenu textuel de l'offre
            identifiant_session: ID de session pour traçabilité
            
        Returns:
            Dictionnaire structuré avec critères requis
        """
        self.journaliseur.info(f"[{identifiant_session}] Début analyse offre")
        
        try:
            # Prétraitement
            texte_nettoye = self._pretraiter_texte(texte_offre)
            
            # ═══════════════════════════════════════════════════════════
            # EXTRACTION DES CRITÈRES REQUIS
            # ═══════════════════════════════════════════════════════════
            
            # 1. Titre du poste
            titre_poste = self._extraire_titre_poste(texte_nettoye)
            
            # 2. Compétences requises
            competences = self.extracteur_competences.extraire_toutes_competences(texte_nettoye)
            
            # 3. Expérience requise
            experience_requise = self._extraire_experience_requise(texte_nettoye)
            
            # 4. Formation requise
            formation_requise = self._extraire_formation_requise(texte_nettoye)
            
            # 5. Langues requises
            langues = self._extraire_langues_requises(texte_nettoye)
            
            # 6. Type de contrat et localisation
            metadonnees = self._extraire_metadonnees(texte_nettoye)
            
            # ═══════════════════════════════════════════════════════════
            # CONSTRUCTION DU PROFIL D'OFFRE
            # ═══════════════════════════════════════════════════════════
            
            profil_offre = {
                "titre_poste": titre_poste,
                "competences_requises": competences,
                "experience_requise": experience_requise,
                "formation_requise": formation_requise,
                "langues_requises": langues,
                "metadonnees": metadonnees,
                "texte_complet": texte_nettoye
            }
            
            self.journaliseur.info(
                f"[{identifiant_session}] Analyse offre terminée - "
                f"Poste: {titre_poste}, "
                f"{len(competences['techniques'])} compétences requises"
            )
            
            return profil_offre
        
        except Exception as e:
            self.journaliseur.erreur(
                f"[{identifiant_session}] Erreur lors de l'analyse offre : {str(e)}",
                exc_info=True
            )
            raise
    
    def _pretraiter_texte(self, texte: str) -> str:
        """Nettoie et normalise le texte de l'offre."""
        # Suppression caractères spéciaux
        texte = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', texte)
        
        # Normalisation espaces
        texte = re.sub(r'\s+', ' ', texte)
        texte = re.sub(r'\n\s*\n', '\n', texte)
        
        return texte.strip()
    
    def _extraire_titre_poste(self, texte: str) -> str:
        """
        Extrait le titre du poste de l'offre.
        
        Stratégies :
        1. Recherche de patterns "Poste : XXX", "Titre : XXX"
        2. Première ligne si courte (< 100 caractères)
        3. Extraction de mots-clés métiers
        
        Args:
            texte: Texte de l'offre
            
        Returns:
            Titre du poste
        """
        lignes = texte.split('\n')
        
        # Stratégie 1 : Patterns explicites
        patterns_titre = [
            r'(?:poste|titre|intitulé)\s*[:\-]\s*(.+)',
            r'(?:nous recherchons|recrutons)\s+(?:un|une)\s+(.+)',
            r'(?:offre d[\'e]emploi)\s*[:\-]\s*(.+)'
        ]
        
        for pattern in patterns_titre:
            match = re.search(pattern, texte.lower())
            if match:
                titre = match.group(1).strip()
                # Nettoyer et capitaliser
                titre = titre[:100]  # Limiter longueur
                return titre.title()
        
        # Stratégie 2 : Première ligne si courte et significative
        if lignes and len(lignes[0]) < 100:
            premiere_ligne = lignes[0].strip()
            if len(premiere_ligne.split()) >= 2:  # Au moins 2 mots
                return premiere_ligne
        
        # Stratégie 3 : Recherche de mots-clés métiers
        mots_cles_postes = [
            'data scientist', 'analyst', 'developer', 'engineer', 'manager',
            'consultant', 'architect', 'specialist', 'analyste', 'développeur',
            'ingénieur', 'responsable', 'chargé', 'chef'
        ]
        
        texte_minuscule = texte.lower()
        for mot_cle in mots_cles_postes:
            if mot_cle in texte_minuscule:
                # Extraire contexte autour du mot-clé
                index = texte_minuscule.find(mot_cle)
                debut = max(0, index - 30)
                fin = min(len(texte), index + 50)
                contexte = texte[debut:fin].strip()
                return contexte[:100]
        
        return "Poste non spécifié"
    
    def _extraire_experience_requise(self, texte: str) -> str:
        """
        Extrait l'exigence d'expérience de l'offre.
        
        Args:
            texte: Texte de l'offre
            
        Returns:
            Description de l'expérience requise
        """
        texte_minuscule = texte.lower()
        
        # Patterns pour expérience
        patterns_exp = [
            r'(\d+)\+?\s*ans?\s+d[\'e]expérience',
            r'expérience\s+(?:de|d\')\s*(\d+)\+?\s+ans?',
            r'minimum\s+(\d+)\s+ans?',
            r'(\d+)\s+(?:à|a)\s+(\d+)\s+ans?'
        ]
        
        for pattern in patterns_exp:
            match = re.search(pattern, texte_minuscule)
            if match:
                return match.group(0)
        
        # Recherche mentions junior/senior
        if 'junior' in texte_minuscule or 'débutant' in texte_minuscule:
            return "0-2 ans (Junior)"
        elif 'senior' in texte_minuscule or 'confirmé' in texte_minuscule:
            return "5+ ans (Senior)"
        elif 'expert' in texte_minuscule:
            return "10+ ans (Expert)"
        
        return "Non spécifié"
    
    def _extraire_formation_requise(self, texte: str) -> str:
        """
        Extrait l'exigence de formation de l'offre.
        
        Args:
            texte: Texte de l'offre
            
        Returns:
            Description de la formation requise
        """
        texte_minuscule = texte.lower()
        
        # Patterns pour formation
        patterns_formation = [
            r'bac\s*\+\s*([2-8])',
            r'(master|ingénieur|doctorat|licence|bachelor|mba)',
            r'diplôme\s+(master|ingénieur|licence)',
            r'formation\s+(?:de\s+niveau\s+)?(bac\+\d|master|ingénieur)'
        ]
        
        formations_trouvees = []
        
        for pattern in patterns_formation:
            matches = re.finditer(pattern, texte_minuscule)
            for match in matches:
                formations_trouvees.append(match.group(0))
        
        if formations_trouvees:
            return ', '.join(set(formations_trouvees))
        
        return "Non spécifié"
    
    def _extraire_langues_requises(self, texte: str) -> List[Dict[str, str]]:
        """
        Extrait les langues requises et leur niveau.
        
        Args:
            texte: Texte de l'offre
            
        Returns:
            Liste de dictionnaires {langue, niveau}
        """
        from src.coeur.configuration import Configuration
        
        langues_requises = []
        texte_minuscule = texte.lower()
        
        langues_ref = Configuration.LANGUES_RECONNUES
        niveaux_ref = Configuration.NIVEAUX_LANGUES
        
        for langue in langues_ref:
            pattern_langue = r'\b' + re.escape(langue) + r'\b'
            match = re.search(pattern_langue, texte_minuscule)
            
            if match:
                # Recherche niveau à proximité
                debut = max(0, match.start() - 50)
                fin = min(len(texte_minuscule), match.end() + 50)
                contexte = texte_minuscule[debut:fin]
                
                niveau = None
                for niv in niveaux_ref:
                    if niv in contexte:
                        niveau = niv
                        break
                
                # Si pas de niveau, déduire selon contexte
                if not niveau:
                    if any(mot in contexte for mot in ['obligatoire', 'impératif', 'exigé']):
                        niveau = 'courant'
                    elif any(mot in contexte for mot in ['souhait', 'apprécié', 'plus']):
                        niveau = 'intermédiaire'
                    else:
                        niveau = 'professionnel'
                
                langues_requises.append({
                    "langue": langue.capitalize(),
                    "niveau": niveau.capitalize(),
                    "obligatoire": 'obligatoire' in contexte or 'impératif' in contexte
                })
        
        return langues_requises
    
    def _extraire_metadonnees(self, texte: str) -> Dict[str, str]:
        """
        Extrait les métadonnées (contrat, localisation, salaire).
        
        Args:
            texte: Texte de l'offre
            
        Returns:
            Dictionnaire de métadonnées
        """
        metadonnees = {}
        texte_minuscule = texte.lower()
        
        # Type de contrat
        types_contrat = {
            'cdi': 'CDI',
            'cdd': 'CDD',
            'stage': 'Stage',
            'alternance': 'Alternance',
            'freelance': 'Freelance',
            'intérim': 'Intérim'
        }
        
        for mot_cle, type_contrat in types_contrat.items():
            if mot_cle in texte_minuscule:
                metadonnees['type_contrat'] = type_contrat
                break
        
        # Localisation (villes françaises courantes + remote)
        villes = [
            'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes',
            'strasbourg', 'montpellier', 'bordeaux', 'lille', 'rennes',
            'remote', 'télétravail', 'distance'
        ]
        
        for ville in villes:
            if ville in texte_minuscule:
                metadonnees['localisation'] = ville.capitalize()
                break
        
        # Salaire (pattern basique)
        pattern_salaire = r'(\d+)\s*(?:k€|k|000)\s*(?:€|euros?)?'
        match_salaire = re.search(pattern_salaire, texte_minuscule)
        if match_salaire:
            metadonnees['salaire'] = match_salaire.group(0)
        
        return metadonnees