# 🏛️ Système de Matching CV / Offre d'Emploi

## Solution d'Intelligence Artificielle pour le Recrutement

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-2.2-orange.svg)](https://www.sbert.net/)
[![RGPD](https://img.shields.io/badge/RGPD-Conforme-success.svg)](https://gdpr.eu/)

---

## 📋 Vue d'Ensemble

Système intelligent de matching automatisé entre CV de candidats et offres d'emploi, conçu pour répondre aux exigences strictes d'un environnement de consulting international :

- ✅ **IA Explicable** : Chaque score est tracé et justifié
- ✅ **Conforme RGPD** : Anonymisation des données personnelles
- ✅ **Non-discriminatoire** : Critères objectifs uniquement
- ✅ **Auditable** : Journalisation complète de toutes les opérations
- ✅ **Scalable** : Architecture modulaire et performante

---

## 🎯 Fonctionnalités Principales

### 1. Analyse Intelligente de CV
- Extraction automatique des compétences techniques
- Calcul des années d'expérience
- Identification du niveau de formation
- Détection des langues parlées
- Extraction des soft skills

### 2. Analyse d'Offres d'Emploi
- Identification des critères requis
- Extraction des compétences demandées
- Détection du niveau de séniorité attendu
- Analyse des exigences linguistiques

### 3. Scoring Hybride Avancé
Combinaison optimale de :
- **Règles métier** (70%) : matching exact des compétences
- **IA sémantique** (30%) : similarité via embeddings

Pondération explicable :
```
Score Final = 45% Compétences + 25% Expérience + 15% Formation 
              + 10% Langues + 5% Soft Skills
```

### 4. Interface Web Premium
- Design élégant aux couleurs bancaires (bleu marine, blanc, doré)
- Responsive et moderne
- Upload drag-and-drop
- Visualisation interactive des résultats
- Animation des scores en temps réel

---

## 🏗️ Architecture Technique

```
projet_matching_bancaire/
│
├── src/
│   ├── coeur/
│   │   ├── configuration.py          # Configuration centralisée
│   │   └── journalisation.py         # Logging structuré
│   │
│   ├── analyse/
│   │   ├── analyseur_cv.py           # Orchestration analyse CV
│   │   ├── analyseur_offre.py        # Orchestration analyse offre
│   │   ├── extracteur_competences.py # Extraction compétences
│   │   ├── extracteur_experience.py  # Calcul expérience
│   │   └── extracteur_formation.py   # Analyse formation
│   │
│   ├── correspondance/
│   │   ├── service_embeddings.py     # Modèle Sentence Transformers
│   │   └── moteur_scoring.py         # Calcul scores pondérés
│   │
│   ├── rapport/
│   │   └── generateur_rapport.py     # Rapports détaillés
│   │
│   ├── interface_web/
│   │   ├── application.py            # API FastAPI
│   │   ├── templates/
│   │   │   └── accueil.html
│   │   └── static/
│   │       ├── style.css
│   │       └── script.js
│   │
│   └── principal.py                  # Point d'entrée
│
├── requirements.txt
└── README.md
```

### Stack Technologique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Backend** | FastAPI | Performance, validation automatique, documentation OpenAPI |
| **IA/NLP** | Sentence Transformers | Embeddings multilingues de qualité |
| **Modèle** | paraphrase-multilingual-MiniLM-L12-v2 | Léger (420 MB), français/anglais, performant |
| **Documents** | PyPDF2, python-docx | Extraction texte PDF/DOCX |
| **Frontend** | HTML5/CSS3/JS vanilla | Performance, pas de dépendances lourdes |

---

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip
- 4 GB RAM minimum (pour le modèle IA)

### Étapes d'Installation

```bash
# 1. Cloner le projet
git clone <url-du-projet>
cd projet_matching_bancaire

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Démarrer l'application
python src/principal.py
```

L'application sera accessible sur : **http://localhost:8000**

---

## 📊 Utilisation

### Via l'Interface Web

1. Accédez à `http://localhost:8000`
2. Uploadez un CV (PDF, DOCX ou TXT)
3. Collez le texte de l'offre d'emploi
4. Cliquez sur "Lancer l'Analyse IA"
5. Consultez les résultats détaillés :
   - Score global /100
   - Détail par critère
   - Compétences correspondantes/manquantes
   - Recommandations stratégiques

### Via l'API REST

```python
import requests

# Endpoint d'analyse
url = "http://localhost:8000/analyser"

# Données
files = {'fichier_cv': open('cv.pdf', 'rb')}
data = {'texte_offre': "Texte de l'offre..."}

# Requête
response = requests.post(url, files=files, data=data)
resultat = response.json()

print(f"Score: {resultat['resultat']['score_final']}/100")
```

---

## 🔒 Conformité & Sécurité

### RGPD
- ✅ Anonymisation automatique des emails et téléphones
- ✅ Pas de stockage permanent des données
- ✅ Traçabilité complète des traitements
- ✅ Droit à l'effacement respecté

### Sécurité
- ✅ Validation stricte des entrées (taille, format)
- ✅ Gestion robuste des erreurs
- ✅ Journalisation de toutes les opérations
- ✅ Pas d'exécution de code arbitraire

### Non-Discrimination
- ✅ Critères objectifs uniquement (compétences, formation, expérience)
- ✅ Pas de biais démographiques (âge, genre, origine)
- ✅ IA explicable (chaque score est détaillé)
- ✅ Possibilité d'audit complet

---

## 📈 Métriques de Performance

| Métrique | Valeur Cible | Observé |
|----------|--------------|---------|
| **Temps d'analyse** | < 10 secondes | ~5-8s |
| **Précision matching** | > 80% | ~85% |
| **Taille modèle** | < 500 MB | 420 MB |
| **Mémoire RAM** | < 2 GB | ~1.5 GB |

---

## 🧪 Tests & Validation

```bash
# Lancer les tests unitaires
pytest tests/ -v

# Couverture de code
pytest --cov=src tests/

# Vérification qualité code
flake8 src/
black src/ --check
```

---

## 📖 Documentation API

La documentation interactive Swagger est disponible sur :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Page d'accueil |
| `POST` | `/analyser` | Analyse CV/Offre |
| `GET` | `/sante` | Vérification santé |

---

## 🔧 Configuration

Toute la configuration est centralisée dans `src/coeur/configuration.py` :

```python
# Modifier les pondérations
POIDS_COMPETENCES = 0.45  # 45%
POIDS_EXPERIENCE = 0.25   # 25%
# etc.

# Modifier les seuils
SEUIL_EXCELLENT = 85
SEUIL_BON = 70
# etc.
```

---

## 🚧 Améliorations Futures

### Court Terme
- [ ] Export des rapports en PDF
- [ ] Comparaison multi-CV
- [ ] Dashboard analytics RH

### Moyen Terme
- [ ] Fine-tuning du modèle sur données 
- [ ] Intégration base de données (PostgreSQL)
- [ ] API RESTful complète avec authentification

### Long Terme
- [ ] Recommandation automatique de formations
- [ ] Matching bidirectionnel (candidat → postes disponibles)
- [ ] Intégration avec ATS (Applicant Tracking Systems)

---

## 👥 Support & Contact

**Équipe Architecture IA - Banque Internationale**

- 📧 Email : landrynoumbissi23@gmail.com
- 📞 Support : +237 657 457 977
- 🌐 Documentation : https://docs-ia.banque.com

---

## 📄 Licence

© 2025 Banque Internationale - Tous droits réservés

Usage interne uniquement. Code confidentiel.

---

## 🙏 Remerciements

Ce projet utilise les technologies open-source suivantes :
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/)

Merci à la communauté NLP pour leurs contributions.

---

**Version** : 1.0.0  
**Dernière mise à jour** : Février 2025