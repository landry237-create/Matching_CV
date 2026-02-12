"""
Extracteur de Formation Académique
Détection diplômes, écoles, domaines d'études
Auteur : Architecture IA Banque
"""

import re
from typing import Optional, Any, Dict, List, Set
from src.coeur.configuration import Configuration, config
from src.coeur.journalisation import journaliseur


class ExtracteurFormation:
    """
    Extrait et analyse la formation académique d'un CV.
    Identifie diplômes, écoles prestigieuses, domaines d'études.
    """
    
    def __init__(self):
        self.journaliseur = journaliseur
        self.diplomes_ref = Configuration.DIPLOMES_RECONNUS
    
    def extraire_formation(self, texte: str) -> Dict[str, any]:
        """
        Extrait la formation académique du texte.
        
        Args:
            texte: Texte du CV
            
        Returns:
            Dictionnaire avec diplômes, niveau, écoles
        """
        texte_minuscule = texte.lower()
        
        # Extraction des diplômes
        diplomes = self._extraire_diplomes(texte_minuscule)
        
        # Extraction des écoles prestigieuses
        ecoles = self._extraire_ecoles(texte_minuscule)
        
        # Extraction des domaines d'études
        domaines = self._extraire_domaines_etudes(texte_minuscule)
        
        # Détermination du niveau académique
        niveau = self._determiner_niveau_academique(diplomes, ecoles)
        
        self.journaliseur.debug(
            f"Formation extraite : {len(diplomes)} diplômes, "
            f"{len(ecoles)} écoles, niveau {niveau}"
        )
        
        return {
            "diplomes": diplomes,
            "ecoles": ecoles,
            "domaines": domaines,
            "niveau_academique": niveau,
            "score_prestige": self._calculer_score_prestige(ecoles)
        }
    
    def calculer_adequation_formation(
        self,
        formation_cv: Dict,
        formation_requise: str
    ) -> Dict[str, Any]:
        """
        Calcule l'adéquation entre la formation du CV et celle requise.
        
        Args:
            formation_cv: Dictionnaire de formation du CV
            formation_requise: String décrivant la formation requise
            
        Returns:
            Dictionnaire avec score et détails
        """
        niveau_cv = formation_cv.get('niveau_academique', 'Bac+2')
        
        # Mapping des niveaux
        niveaux_rang = {
            'bac': 0, 'bac+2': 1, 'bac+3': 2, 'bac+4': 3, 'bac+5': 4, 'doctorat': 5,
            'licence': 2, 'master': 4, 'ingénieur': 4
        }
        
        rang_cv = niveaux_rang.get(niveau_cv.lower(), 2)
        
        # Estimer le rang requis
        if 'master' in formation_requise.lower() or 'bac+5' in formation_requise.lower():
            rang_requis = 4
        elif 'ingénieur' in formation_requise.lower():
            rang_requis = 4
        elif 'licence' in formation_requise.lower() or 'bac+3' in formation_requise.lower():
            rang_requis = 2
        else:
            rang_requis = 1
        
        # Calculer score
        if rang_cv >= rang_requis:
            score = 90 + (rang_cv - rang_requis) * 10
            adequation = "Adéquat"
        else:
            score = 50 + (rang_cv / rang_requis) * 50
            adequation = "En-dessous des attentes"
        
        return {
            'score': min(100, round(score, 2)),
            'niveau_cv': niveau_cv,
            'formation_requise': formation_requise,
            'adequation': adequation,
            'commentaire': f"Formation: {niveau_cv} - Requis: {formation_requise}"
        }
    
    def _extraire_diplomes(self, texte: str) -> List[str]:
        """
        Extrait les diplômes mentionnés dans le CV.
        
        Args:
            texte: Texte en minuscules
            
        Returns:
            Liste des diplômes trouvés
        """
        diplomes_trouves = set()
        
        # Matching avec dictionnaire de référence
        for diplome in self.diplomes_ref:
            pattern = r'\b' + re.escape(diplome) + r'\b'
            if re.search(pattern, texte):
                diplomes_trouves.add(diplome)
        
        # Patterns additionnels pour diplômes
        patterns_diplomes = [
            # Niveaux Bac+X
            r'\bbac\s*\+\s*([2-8])\b',
            r'\bniveau\s+(bac\s*\+\s*[2-8]|master|licence|doctorat)\b',
            
            # Diplômes français
            r'\b(deug|deust|licence pro|master [12]|mastère)\b',
            r'\b(diplôme d[\'e] ingénieur|ingénieur)\b',
            r'\b(doctorat|phd|thèse)\b',
            
            # Diplômes internationaux
            r'\b(bachelor|bsc|ba|bs)\b',
            r'\b(master|msc|ma|ms|mba)\b',
            r'\b(phd|doctorate)\b'
        ]
        
        for pattern in patterns_diplomes:
            matches = re.finditer(pattern, texte)
            for match in matches:
                diplomes_trouves.add(match.group(0))
        
        return sorted(list(diplomes_trouves))
    
    def _extraire_ecoles(self, texte: str) -> List[str]:
        """
        Extrait les écoles et universités prestigieuses.
        
        Args:
            texte: Texte en minuscules
            
        Returns:
            Liste des écoles identifiées
        """
        ecoles_trouvees = set()
        
        # Écoles d'ingénieurs (Grandes Écoles)
        ecoles_ingenieurs = [
            r'\b(polytechnique|école polytechnique|x)\b',
            r'\b(centrale|école centrale)\b',
            r'\b(mines|école des mines)\b',
            r'\b(ponts|ponts et chaussées|enpc)\b',
            r'\b(supelec|supélec|centralesupélec)\b',
            r'\b(telecom|télécom)\b',
            r'\b(ensae|ensai|ensimag)\b',
            r'\b(insa|polytech|utc|utt)\b'
        ]
        
        # Écoles de commerce
        ecoles_commerce = [
            r'\b(hec|hec paris)\b',
            r'\b(essec)\b',
            r'\b(escp|escp europe)\b',
            r'\b(em lyon|emlyon)\b',
            r'\b(edhec)\b',
            r'\b(skema|audencia|grenoble em)\b'
        ]
        
        # Universités & IEP
        universites = [
            r'\b(sciences po|institut d[\'e] études politiques|iep)\b',
            r'\b(ena|école nationale d[\'e]administration)\b',
            r'\b(dauphine|paris dauphine)\b',
            r'\b(sorbonne|panthéon-sorbonne)\b',
            r'\b(mit|stanford|harvard|oxford|cambridge)\b',
            r'\b(eth zürich|epfl)\b'
        ]
        
        tous_patterns = ecoles_ingenieurs + ecoles_commerce + universites
        
        for pattern in tous_patterns:
            match = re.search(pattern, texte)
            if match:
                ecoles_trouvees.add(match.group(0))
        
        return sorted(list(ecoles_trouvees))
    
    def _extraire_domaines_etudes(self, texte: str) -> List[str]:
        """
        Extrait les domaines d'études (informatique, finance, etc.).
        
        Args:
            texte: Texte en minuscules
            
        Returns:
            Liste des domaines identifiés
        """
        domaines_trouves = set()
        
        # Domaines d'études pertinents pour la banque
        patterns_domaines = [
            (r'\b(informatique|computer science|cs)\b', 'Informatique'),
            (r'\b(mathématiques|maths|mathematics)\b', 'Mathématiques'),
            (r'\b(statistiques|statistics|data science)\b', 'Statistiques / Data Science'),
            (r'\b(finance|financial)\b', 'Finance'),
            (r'\b(économie|economics)\b', 'Économie'),
            (r'\b(gestion|management)\b', 'Gestion / Management'),
            (r'\b(ingénierie|engineering)\b', 'Ingénierie'),
            (r'\b(droit|law)\b', 'Droit'),
            (r'\b(physique|physics)\b', 'Physique'),
            (r'\b(actuariat|actuarial)\b', 'Actuariat')
        ]
        
        for pattern, domaine_normalise in patterns_domaines:
            if re.search(pattern, texte):
                domaines_trouves.add(domaine_normalise)
        
        return sorted(list(domaines_trouves))
    
    def _determiner_niveau_academique(
        self,
        diplomes: List[str],
        ecoles: List[str]
    ) -> str:
        """
        Détermine le niveau académique global.
        
        Niveaux : Doctorat > Master/Ingénieur > Licence > Bac+2 > Bac
        
        Args:
            diplomes: Liste des diplômes
            ecoles: Liste des écoles
            
        Returns:
            Niveau académique ('Bac', 'Bac+2', 'Bac+3', 'Bac+5', 'Bac+8')
        """
        texte_diplomes = ' '.join(diplomes).lower()
        
        # Doctorat (Bac+8)
        if any(mot in texte_diplomes for mot in ['doctorat', 'phd', 'thèse']):
            return "Bac+8 (Doctorat)"
        
        # Master / Ingénieur (Bac+5)
        if any(mot in texte_diplomes for mot in ['master', 'mba', 'ingénieur', 'ms', 'msc']):
            return "Bac+5 (Master/Ingénieur)"
        
        if ecoles:  # École prestigieuse = généralement Bac+5
            return "Bac+5 (Grande École)"
        
        # Licence / Bachelor (Bac+3)
        if any(mot in texte_diplomes for mot in ['licence', 'bachelor', 'bac+3']):
            return "Bac+3 (Licence)"
        
        # BTS / DUT (Bac+2)
        if any(mot in texte_diplomes for mot in ['bts', 'dut', 'bac+2']):
            return "Bac+2"
        
        # Baccalauréat
        if 'bac' in texte_diplomes:
            return "Bac"
        
        return "Non spécifié"
    
    def _calculer_score_prestige(self, ecoles: List[str]) -> int:
        """
        Calcule un score de prestige basé sur les écoles.
        
        Args:
            ecoles: Liste des écoles fréquentées
            
        Returns:
            Score 0-100
        """
        if not ecoles:
            return 50  # Score neutre
        
        texte_ecoles = ' '.join(ecoles).lower()
        
        # Écoles ultra-prestigieuses (score 100)
        ultra_prestige = ['polytechnique', 'x', 'hec', 'ena', 'mit', 'stanford', 'harvard']
        if any(ecole in texte_ecoles for ecole in ultra_prestige):
            return 100
        
        # Grandes écoles (score 90)
        grandes_ecoles = ['centrale', 'mines', 'ponts', 'essec', 'escp', 'sciences po']
        if any(ecole in texte_ecoles for ecole in grandes_ecoles):
            return 90
        
        # Bonnes écoles (score 75)
        bonnes_ecoles = ['telecom', 'supelec', 'em lyon', 'edhec', 'insa']
        if any(ecole in texte_ecoles for ecole in bonnes_ecoles):
            return 75
        
        # École mentionnée mais pas dans top (score 60)
        return 60
    
    def calculer_adequation_formation(
        self,
        formation_cv: Dict,
        formation_requise: str
    ) -> Dict[str, any]:
        """
        Calcule l'adéquation entre formation CV et exigence offre.
        
        Args:
            formation_cv: Dictionnaire retourné par extraire_formation()
            formation_requise: Texte de l'exigence
            
        Returns:
            Dictionnaire avec score et analyse
        """
        niveau_cv = formation_cv.get('niveau_academique', 'Non spécifié')
        diplomes_cv = formation_cv.get('diplomes', [])
        domaines_cv = formation_cv.get('domaines', [])
        score_prestige = formation_cv.get('score_prestige', 50)
        
        texte_requis = formation_requise.lower()
        
        # Extraction niveau requis
        niveau_requis = self._extraire_niveau_requis(texte_requis)
        
        # Extraction domaines requis
        domaines_requis = self._extraire_domaines_requis(texte_requis)
        
        # Calcul du score (4 composantes)
        score_niveau = self._comparer_niveaux(niveau_cv, niveau_requis)
        score_domaine = self._comparer_domaines(domaines_cv, domaines_requis)
        score_prestige_normalise = score_prestige / 100 * 100  # Déjà sur 100
        
        # Score final pondéré
        score_final = (
            score_niveau * 0.5 +      # 50% niveau
            score_domaine * 0.30 +    # 30% domaine
            score_prestige_normalise * 0.20  # 20% prestige
        )
        
        return {
            "score": round(score_final, 2),
            "niveau_cv": niveau_cv,
            "niveau_requis": niveau_requis,
            "domaines_cv": domaines_cv,
            "domaines_requis": domaines_requis,
            "adequation": "Excellente" if score_final >= 85 else
                         "Bonne" if score_final >= 70 else
                         "Moyenne" if score_final >= 50 else "Faible",
            "commentaire": self._generer_commentaire_formation(
                niveau_cv, niveau_requis, domaines_cv, domaines_requis
            )
        }
    
    def _extraire_niveau_requis(self, texte: str) -> str:
        """Extrait le niveau de formation requis."""
        
        if 'doctorat' in texte or 'phd' in texte:
            return "Bac+8 (Doctorat)"
        elif any(mot in texte for mot in ['master', 'bac+5', 'ingénieur', 'mba']):
            return "Bac+5 (Master/Ingénieur)"
        elif any(mot in texte for mot in ['licence', 'bac+3', 'bachelor']):
            return "Bac+3 (Licence)"
        elif any(mot in texte for mot in ['bts', 'dut', 'bac+2']):
            return "Bac+2"
        else:
            return "Bac+5 (Master/Ingénieur)"  # Par défaut pour la banque
    
    def _extraire_domaines_requis(self, texte: str) -> List[str]:
        """Extrait les domaines d'études requis."""
        
        domaines = []
        
        if any(mot in texte for mot in ['informatique', 'computer science']):
            domaines.append('Informatique')
        if any(mot in texte for mot in ['finance', 'financial']):
            domaines.append('Finance')
        if any(mot in texte for mot in ['mathématiques', 'mathematics', 'quantitatif']):
            domaines.append('Mathématiques')
        if any(mot in texte for mot in ['économie', 'economics']):
            domaines.append('Économie')
        if any(mot in texte for mot in ['statistiques', 'data science']):
            domaines.append('Statistiques / Data Science')
        
        return domaines
    
    def _comparer_niveaux(self, niveau_cv: str, niveau_requis: str) -> float:
        """Compare les niveaux académiques."""
        
        hierarchie = {
            "Bac": 1,
            "Bac+2": 2,
            "Bac+3 (Licence)": 3,
            "Bac+5 (Master/Ingénieur)": 5,
            "Bac+5 (Grande École)": 5.5,
            "Bac+8 (Doctorat)": 8
        }
        
        score_cv = hierarchie.get(niveau_cv, 0)
        score_requis = hierarchie.get(niveau_requis, 5)
        
        if score_cv >= score_requis:
            return 100.0
        elif score_cv >= score_requis - 1:
            return 80.0  # Juste en dessous acceptable
        else:
            return max(0, (score_cv / score_requis) * 70)
    
    def _comparer_domaines(self, domaines_cv: List[str], domaines_requis: List[str]) -> float:
        """Compare les domaines d'études."""
        
        if not domaines_requis:
            return 100.0  # Pas d'exigence = score max
        
        set_cv = set(d.lower() for d in domaines_cv)
        set_requis = set(d.lower() for d in domaines_requis)
        
        if not set_requis:
            return 100.0
        
        intersection = set_cv & set_requis
        taux_couverture = len(intersection) / len(set_requis)
        
        return taux_couverture * 100
    
    def _generer_commentaire_formation(
        self,
        niveau_cv: str,
        niveau_requis: str,
        domaines_cv: List[str],
        domaines_requis: List[str]
    ) -> str:
        """Génère un commentaire explicatif sur la formation."""
        
        commentaires = []
        
        commentaires.append(f"Niveau : {niveau_cv} (requis : {niveau_requis})")
        
        if domaines_cv:
            commentaires.append(f"Domaines : {', '.join(domaines_cv)}")
        
        if domaines_requis:
            set_cv = set(d.lower() for d in domaines_cv)
            set_requis = set(d.lower() for d in domaines_requis)
            manquants = set_requis - set_cv
            
            if not manquants:
                commentaires.append("Tous les domaines requis sont couverts.")
            else:
                commentaires.append(f"Domaines manquants : {', '.join(manquants)}")
        
        return " | ".join(commentaires)