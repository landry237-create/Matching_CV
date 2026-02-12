"""
Générateur de Rapport LaTeX Sophistiqué
=========================================

Module de génération de rapports PDF professionnels en LaTeX
avec score global, points forts, architecture et analyse détaillée.

Auteur : Architecture IA Banque
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.coeur.journalisation import journaliseur


class GenerateurRapportLaTeX:
    """
    Génère des rapports PDF sophistiqués en LaTeX.
    
    Sections :
    - Couverture professionnelle avec score global
    - Résumé exécutif
    - Score global avec visualisation
    - Points forts détaillés
    - Points faibles et compétences manquantes
    - Architecture du système
    - Justifications et recommandations
    - Appendices techniques
    """
    
    def __init__(self):
        """Initialise le générateur LaTeX."""
        self.journaliseur = journaliseur
        self.temp_dir = tempfile.gettempdir()
    
    def generer_rapport_latex(
        self,
        resultat_scoring: Dict[str, Any],
        profil_cv: Dict[str, Any],
        profil_offre: Dict[str, Any],
        identifiant_session: str
    ) -> bytes:
        """
        Génère un rapport LaTeX complet et retourne le PDF en bytes.
        
        Args:
            resultat_scoring: Résultat du moteur de scoring
            profil_cv: Profil du candidat
            profil_offre: Profil de l'offre
            identifiant_session: ID de session
            
        Returns:
            Contenu PDF en bytes
        """
        self.journaliseur.info(f"[{identifiant_session}] Génération rapport LaTeX")
        
        try:
            # Générer le contenu LaTeX
            contenu_latex = self._generer_contenu_latex(
                resultat_scoring,
                profil_cv,
                profil_offre,
                identifiant_session
            )
            
            # Compiler LaTeX en PDF
            pdf_bytes = self._compiler_latex_en_pdf(contenu_latex, identifiant_session)
            
            self.journaliseur.info(
                f"[{identifiant_session}] Rapport LaTeX généré avec succès "
                f"({len(pdf_bytes)} bytes)"
            )
            
            return pdf_bytes
        
        except Exception as e:
            self.journaliseur.erreur(
                f"[{identifiant_session}] Erreur génération rapport LaTeX : {str(e)}",
                exc_info=True
            )
            raise
    
    def _generer_contenu_latex(
        self,
        resultat_scoring: Dict[str, Any],
        profil_cv: Dict[str, Any],
        profil_offre: Dict[str, Any],
        identifiant_session: str
    ) -> str:
        """Génère le contenu LaTeX complet."""
        
        score_final = resultat_scoring['score_final']
        niveau = resultat_scoring['niveau_correspondance']
        sous_scores = resultat_scoring['sous_scores']
        poids = resultat_scoring['poids_utilises']
        
        # Éléments visuels
        couleur_score = self._obtenir_couleur_score(score_final)
        emoji_niveau = self._obtenir_emoji_niveau(niveau)
        
        latex = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[french]{babel}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage{tikzset}

\pgfplotsset{compat=1.18}

% Couleurs
\definecolor{primary}{RGB}{0, 102, 204}
\definecolor{accent}{RGB}{255, 153, 0}
\definecolor{success}{RGB}{76, 175, 80}
\definecolor{warning}{RGB}{255, 152, 0}
\definecolor{danger}{RGB}{244, 67, 54}
\definecolor{score_color}{RGB}{""" + couleur_score + r"""}

% En-têtes
\pagestyle{fancy}
\fancyhf{}
\rhead{\textbf{Matching CV/Offre - Session } \texttt{""" + identifiant_session[:8] + r"""}}
\lhead{Système de Matching Bancaire}
\cfoot{\thepage\ / \pageref{LastPage}}

\title{\LARGE \textbf{RAPPORT D'ANALYSE DE MATCHING CV/OFFRE D'EMPLOI}}
\author{\textbf{Système de Matching Bancaire Intelligent}}
\date{\today}

\begin{document}

% ═══════════════════════════════════════════════════════════
% COUVERTURE
% ═══════════════════════════════════════════════════════════

\maketitle

\vspace{1cm}

\begin{center}
\begin{tikzpicture}[scale=2]
  \draw[line width=3pt, score_color] (0,0) circle (1.5cm);
  \node[font=\Large\bfseries, color=score_color] at (0,0) {""" + str(score_final) + r"""}%;
  \node[font=\small, color=black] at (0,-2.2cm) {\textbf{Score Global}};
  \node[font=\Large, color=score_color] at (0,-2.8cm) {""" + emoji_niveau + r""" \textit{""" + niveau + r"""}};
\end{tikzpicture}
\end{center}

\vspace{1.5cm}

\begin{center}
  \textbf{Date du rapport :} """ + datetime.now().strftime("%d/%m/%Y à %H:%M") + r"""
  
  \textbf{Identifiant session :} \texttt{""" + identifiant_session + r"""}
  
  \vspace{0.5cm}
  
  \textit{Rapport généré automatiquement par le système IA de matching}
\end{center}

\newpage

% ═══════════════════════════════════════════════════════════
% RÉSUMÉ EXÉCUTIF
% ═══════════════════════════════════════════════════════════

\section{Résumé Exécutif}

"""
        
        # Résumé basé sur le score
        if score_final >= 85:
            synthese = f"""
Le candidat présente une \textbf{{excellente correspondance}} avec le poste recherché 
(score {score_final}/100). Le profil répond à l'ensemble des critères essentiels et 
démontre une forte adéquation avec les compétences, l'expérience et la formation requises.

\textbf{{Recommandation :}} Candidat hautement qualifié pour le poste. À interviewer en priorité.
"""
        elif score_final >= 70:
            synthese = f"""
Le candidat présente une \textbf{{bonne correspondance}} avec le poste recherché 
(score {score_final}/100). La plupart des critères sont satisfaits, avec une adéquation 
globale solide sur les compétences clés.

\textbf{{Recommandation :}} Candidat qualifié. À interviewer.
"""
        elif score_final >= 50:
            synthese = f"""
Le candidat présente une \textbf{{correspondance moyenne}} avec le poste recherché 
(score {score_final}/100). Certaines compétences clés sont manquantes, nécessitant 
une évaluation approfondie.

\textbf{{Recommandation :}} À considérer avec réserve. Entretien recommandé pour clarifier.
"""
        else:
            synthese = f"""
Le candidat présente une \textbf{{faible correspondance}} avec le poste recherché 
(score {score_final}/100). Le profil ne répond pas aux critères essentiels et présente 
des lacunes significatives.

\textbf{{Recommandation :}} Profil peu adapté au poste. Non recommandé pour cette position.
"""
        
        latex += synthese
        
        # Détail des scores
        latex += r"""

\subsection{Détail des Critères de Scoring}

\begin{center}
\begin{tabular}{lcccc}
\toprule
\textbf{Critère} & \textbf{Score} & \textbf{Poids} & \textbf{Contribution} & \textbf{Impact} \\
\midrule
"""
        
        criterias = [
            ('Compétences Techniques', 'competences', sous_scores['competences']['score']),
            ('Expérience Professionnelle', 'experience', sous_scores['experience']['score']),
            ('Formation Académique', 'formation', sous_scores['formation']['score']),
            ('Compétences Linguistiques', 'langues', sous_scores['langues']['score']),
            ('Soft Skills', 'soft_skills', sous_scores['soft_skills']['score']),
        ]
        
        for label, key, score in criterias:
            poids_val = poids[key] * 100
            contribution = score * poids[key]
            latex += f"""{label} & {score:.1f}/100 & {poids_val:.0f}\\% & {contribution:.1f} & """
            
            if score >= 80:
                latex += r"""\textcolor{success}{\textbf{Excellent}}"""
            elif score >= 60:
                latex += r"""\textcolor{accent}{\textbf{Bon}}"""
            elif score >= 40:
                latex += r"""\textcolor{warning}{\textbf{Moyen}}"""
            else:
                latex += r"""\textcolor{danger}{\textbf{Faible}}"""
            
            latex += r""" \\
"""
        
        latex += r"""\bottomrule
\end{tabular}
\end{center}

\newpage

% ═══════════════════════════════════════════════════════════
% POINTS FORTS
% ═══════════════════════════════════════════════════════════

\section{Points Forts et Adéquations}

"""
        
        # Points forts
        points_forts = self._analyser_points_forts(resultat_scoring, profil_cv)
        
        for i, point in enumerate(points_forts, 1):
            latex += f"\\subsection{{{i}. {point['titre']}}}\n\n"
            latex += point['description'] + "\n\n"
        
        latex += r"""

\newpage

% ═══════════════════════════════════════════════════════════
% COMPÉTENCES MANQUANTES
% ═══════════════════════════════════════════════════════════

\section{Compétences Manquantes et Points d'Amélioration}

"""
        
        # Points faibles
        points_faibles = self._analyser_points_faibles(resultat_scoring, profil_cv, profil_offre)
        
        for i, point in enumerate(points_faibles, 1):
            latex += f"\\subsection{{{i}. {point['titre']}}}\n\n"
            latex += point['description'] + "\n\n"
        
        latex += r"""

\newpage

% ═══════════════════════════════════════════════════════════
% ARCHITECTURE DU SYSTÈME
% ═══════════════════════════════════════════════════════════

\section{Architecture du Système de Matching}

"""
        
        latex += self._generer_section_architecture()
        
        latex += r"""

\newpage

% ═══════════════════════════════════════════════════════════
% JUSTIFICATIONS TECHNIQUES
% ═══════════════════════════════════════════════════════════

\section{Justifications Techniques et Méthodologie}

"""
        
        latex += self._generer_section_justifications(resultat_scoring)
        
        latex += r"""

\newpage

% ═══════════════════════════════════════════════════════════
% RECOMMANDATIONS
% ═══════════════════════════════════════════════════════════

\section{Recommandations}

"""
        
        for i, rec in enumerate(resultat_scoring['recommandations'], 1):
            latex += f"{i}. {rec}\n\n"
        
        latex += r"""

\newpage

% ═══════════════════════════════════════════════════════════
% APPENDICES
% ═══════════════════════════════════════════════════════════

\section*{Appendices Techniques}

\subsection*{A. Métriques de Scoring}

Le système utilise une approche \textbf{hybride rule-based et ML} :

\begin{itemize}
  \item \textbf{Matching exact} (70\%) : correspondance directe avec dictionnaire
  \item \textbf{Similarité sémantique} (30\%) : encodages par réseau de neurones
  \item \textbf{Pondérations} : ajustées selon les exigences bancaires
\end{itemize}

\subsection*{B. Modèles Utilisés}

\begin{itemize}
  \item \textbf{Embeddings} : \texttt{sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2}
  \item \textbf{Architecture} : Modèle BERT multilingue fine-tuné
  \item \textbf{Dimensionnalité} : 384 dimensions pour les vecteurs d'embeddings
\end{itemize}

\subsection*{C. Conformité}

\begin{itemize}
  \item \textbf{RGPD} : Données personnelles anonymisées dans les logs
  \item \textbf{Auditabilité} : Tous les scores sont traçables et reproductibles
  \item \textbf{Non-discrimination} : Critères objectifs et mesurables uniquement
\end{itemize}

\subsection*{D. Limitations et Considérations}

\begin{enumerate}
  \item Le score reflète une adéquation technique uniquement
  \item Les aspects comportementaux et culturels requièrent une évaluation humaine
  \item La qualité du score dépend de la qualité des documents fournis
  \item Un score élevé ne garantit pas le succès en entretien
\end{enumerate}

\vspace{2cm}

\hrule

\vspace{1cm}

\begin{center}
  \textit{Rapport généré automatiquement par le système IA de Matching CV/Offre}
  
  \textit{Système de Matching Bancaire v1.0.0}
\end{center}

\end{document}
"""
        
        return latex
    
    def _obtenir_couleur_score(self, score: float) -> str:
        """Retourne la couleur RGB selon le score."""
        if score >= 85:
            return "76, 175, 80"  # Vert
        elif score >= 70:
            return "33, 150, 243"  # Bleu
        elif score >= 50:
            return "255, 152, 0"  # Orange
        else:
            return "244, 67, 54"  # Rouge
    
    def _obtenir_emoji_niveau(self, niveau: str) -> str:
        """Retourne un emoji selon le niveau."""
        emojis = {
            "Excellent": "⭐⭐⭐",
            "Bon": "⭐⭐",
            "Moyen": "⭐",
            "Faible": "⚠"
        }
        return emojis.get(niveau, "❓")
    
    def _analyser_points_forts(
        self,
        resultat_scoring: Dict[str, Any],
        profil_cv: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Extrait et analyse les points forts."""
        
        points = []
        sous_scores = resultat_scoring['sous_scores']
        
        # Point fort 1 : Compétences
        if sous_scores['competences']['score'] >= 70:
            points.append({
                'titre': 'Compétences Techniques Excellentes',
                'description': f"""
Le candidat possède {len(sous_scores['competences']['correspondantes'])} compétences techniques 
correspondant aux exigences de l'offre, avec un taux de couverture de 
{sous_scores['competences']['taux_couverture']:.1f}\\%. 

\\textbf{{Compétences correspondantes :}} {', '.join(sous_scores['competences']['correspondantes'][:5])}...
"""
            })
        
        # Point fort 2 : Expérience
        if sous_scores['experience']['score'] >= 70:
            points.append({
                'titre': 'Expérience Professionnelle Appropriée',
                'description': f"""
Le candidat dispose de {sous_scores['experience']['annees_cv']} années d'expérience 
pour une exigence de {sous_scores['experience']['annees_requises']} ans. 
Son profil est classé comme \\textbf{{{sous_scores['experience']['adequation']}}}.
"""
            })
        
        # Point fort 3 : Formation
        if sous_scores['formation']['score'] >= 70:
            points.append({
                'titre': 'Formation Académique Solide',
                'description': f"""
La formation du candidat ({profil_cv['formation'].get('niveau_academique', 'Non spécifié')}) 
correspond aux exigences de l'offre. Formation académique : 
\\textbf{{{sous_scores['formation']['adequation']}}}.
"""
            })
        
        # Point fort 4 : Soft skills
        if sous_scores['soft_skills']['score'] >= 60:
            points.append({
                'titre': 'Soft Skills Développées',
                'description': f"""
Le candidat maîtrise {len(sous_scores['soft_skills']['correspondantes'])} soft skills 
requises pour le poste, démontrant des qualités essentielles pour le succès.
"""
            })
        
        return points
    
    def _analyser_points_faibles(
        self,
        resultat_scoring: Dict[str, Any],
        profil_cv: Dict[str, Any],
        profil_offre: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Extrait et analyse les points faibles."""
        
        points = []
        sous_scores = resultat_scoring['sous_scores']
        
        # Faiblesse 1 : Compétences manquantes
        if sous_scores['competences']['score'] < 80:
            manquantes = sous_scores['competences']['manquantes']
            points.append({
                'titre': 'Compétences Techniques Manquantes',
                'description': f"""
Le candidat ne maîtrise pas {len(manquantes)} compétence(s) requise(s) :

\\begin{{itemize}}
{chr(10).join([f'  \\item {comp}' for comp in manquantes[:5]])}
\\end{{itemize}}

\\textbf{{Recommandation :}} Formation ou apprentissage recommandé sur ces domaines.
"""
            })
        
        # Faiblesse 2 : Expérience
        if sous_scores['experience']['score'] < 70:
            points.append({
                'titre': 'Expérience Insuffisante',
                'description': f"""
Le candidat dispose de {sous_scores['experience']['annees_cv']} années d'expérience 
alors que {sous_scores['experience']['annees_requises']} ans sont requis. 
Cette lacune nécessite une évaluation attentive lors de l'entretien.
"""
            })
        
        # Faiblesse 3 : Formation
        if sous_scores['formation']['score'] < 70:
            points.append({
                'titre': 'Formation Académique En-Dessous des Attentes',
                'description': f"""
La formation du candidat ({profil_cv['formation'].get('niveau_academique', 'Non spécifié')}) 
est légèrement en-dessous de celle recommandée. 

\\textbf{{Impact :}} {sous_scores['formation']['commentaire']}
"""
            })
        
        return points
    
    def _generer_section_architecture(self) -> str:
        """Génère la section architecture du système."""
        
        return r"""

\subsection{Pipeline de Traitement}

Le système fonctionne selon une architecture modulaire composée de 5 étapes principales :

\subsubsection{1. Prétraitement des Documents}

\begin{itemize}
  \item Extraction de texte depuis PDF, DOCX, ou TXT
  \item Normalisation et nettoyage du texte
  \item Suppression des caractères spéciaux et normalisation d'espaces
\end{itemize}

\subsubsection{2. Analyse Structurée}

\textbf{Extracteurs spécialisés} :

\begin{itemize}
  \item \textbf{ExtracteurCompétences} : Identification des compétences techniques et soft skills
  \item \textbf{ExtracteurExpérience} : Extraction des années d'expérience et niveau de séniorité
  \item \textbf{ExtracteurFormation} : Détection des diplômes et domaines d'études
  \item \textbf{AnalyseurCV} : Orchestration complète de l'analyse CV
  \item \textbf{AnalyseurOffre} : Extraction des critères de l'offre d'emploi
\end{itemize}

\subsubsection{3. Calcul du Score Global (MoteurScoring)}

Approche \textbf{hybride rule-based + ML} :

\begin{enumerate}
  \item \textbf{Compétences (45\%)} : Matching exact (70\%) + Similarité sémantique (30\%)
  \item \textbf{Expérience (25\%)} : Score basé sur les années et la séniorité
  \item \textbf{Formation (15\%)} : Adéquation du niveau académique
  \item \textbf{Langues (10\%)} : Couverture des exigences linguistiques
  \item \textbf{Soft Skills (5\%)} : Correspondance avec critères interpersonnels
\end{enumerate}

\subsubsection{4. Génération du Rapport}

Trois formats disponibles :

\begin{itemize}
  \item \textbf{JSON} : Pour intégration dans systèmes tiers
  \item \textbf{Texte} : Rapport lisible formaté
  \item \textbf{LaTeX/PDF} : Rapport sophistiqué (ce document)
\end{itemize}

\subsubsection{5. Interface Web (FastAPI)}

\begin{itemize}
  \item Endpoint POST /analyser : Analyse du matching
  \item Endpoints GET : Documentation, support, contact
  \item Endpoint GET /sante : Monitoring et health check
\end{itemize}

\subsection{Stack Technologique}

\begin{itemize}
  \item \textbf{Backend} : Python 3.9+, FastAPI, Uvicorn
  \item \textbf{NLP} : sentence-transformers, HuggingFace Transformers
  \item \textbf{ML} : NumPy, Scikit-learn
  \item \textbf{Extraction} : PyPDF2, python-docx
  \item \textbf{Logging} : Système de journalisation structuré (RGPD-compliant)
\end{itemize}

"""
    
    def _generer_section_justifications(
        self,
        resultat_scoring: Dict[str, Any]
    ) -> str:
        """Génère la section des justifications techniques."""
        
        score_final = resultat_scoring['score_final']
        
        return f"""

\subsection{{Méthodologie de Scoring}}

\subsubsection{{Approche Hybride}}

Le système combine deux approches complémentaires :

\\begin{{enumerate}}
  \\item \\textbf{{Rule-based}} : Utilise des dictionnaires de compétences validés et des patterns regex
  \\item \\textbf{{ML-based}} : Utilise des embeddings pour capturer la similarité sémantique
\\end{{enumerate}}

Cette combinaison permet de capturer à la fois les correspondances exactes (robustesse) 
et les correspondances sémantiques (flexibilité).

\\subsubsection{{Pondérations}}

Les poids ont été calibrés selon les priorités bancaires :

\\begin{{itemize}}
  \\item 45\\% Compétences Techniques : Critères directs du poste
  \\item 25\\% Expérience : Indicateur de capacité à performer
  \\item 15\\% Formation : Fondations académiques et crédibilité
  \\item 10\\% Langues : Important pour environnement international
  \\item 5\\% Soft Skills : Adaptation culturelle et travail en équipe
\\end{{itemize}}

\\subsection{{Interprétation du Score {score_final}/100}}

\\begin{{itemize}}
  \\item \\textbf{{85-100}} : Correspondance excellente - Candidat hautement qualifié
  \\item \\textbf{{70-84}} : Bonne correspondance - Candidat qualifié
  \\item \\textbf{{50-69}} : Correspondance moyenne - À évaluer attentivement
  \\item \\textbf{{0-49}} : Faible correspondance - Peu adapté
\\end{{itemize}}

\\subsection{{Limitations du Système}}

\\begin{{enumerate}}
  \\item Ne capture pas les aspects comportementaux et culturels (soft)
  \\item Dépend de la qualité et complétude des documents fournis
  \\item Ne prend pas en compte l'évolution professionnelle récente (sauf si mentionnée)
  \\item La similarité sémantique suppose un ensemble d'apprentissage représentatif
\\end{{enumerate}}

"""
    
    def _compiler_latex_en_pdf(self, contenu_latex: str, identifiant_session: str) -> bytes:
        """Compile le LaTeX en PDF et retourne les bytes."""
        
        # Créer un fichier .tex temporaire
        tex_file = os.path.join(self.temp_dir, f"rapport_{identifiant_session}.tex")
        pdf_file = os.path.join(self.temp_dir, f"rapport_{identifiant_session}.pdf")
        
        try:
            # Écrire le contenu LaTeX
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(contenu_latex)
            
            # Compiler avec pdflatex
            self.journaliseur.debug(f"Compilation LaTeX : {tex_file}")
            
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', self.temp_dir, tex_file],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.journaliseur.avertissement(
                    f"Avertissement compilation LaTeX (code {result.returncode})"
                )
            
            # Lire le PDF généré
            if os.path.exists(pdf_file):
                with open(pdf_file, 'rb') as f:
                    pdf_bytes = f.read()
                
                return pdf_bytes
            else:
                raise RuntimeError("Le fichier PDF n'a pas pu être généré")
        
        except FileNotFoundError:
            self.journaliseur.erreur(
                "pdflatex non trouvé. Installer TeXLive ou MiKTeX pour générer des PDF."
            )
            raise RuntimeError(
                "pdflatex non disponible. Installez TeXLive (Linux/Mac) ou MiKTeX (Windows)"
            )
        
        finally:
            # Nettoyage des fichiers temporaires
            for ext in ['.tex', '.pdf', '.aux', '.log', '.out']:
                try:
                    os.remove(tex_file.replace('.tex', ext))
                except:
                    pass
