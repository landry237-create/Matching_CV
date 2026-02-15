text

# 🏛️ Architecture Détaillée - Système de Matching Bancaire

## Document Technique Approfondi

Version : 1.0.0  
Date : Février 2026  
Classification : Confidentiel - Usage Interne Bancaire

---

## Table des Matières

1. [Vue d'Ensemble Architecture](#vue-densemble-architecture)
2. [Principes de Conception](#principes-de-conception)
3. [Architecture Logicielle](#architecture-logicielle)
4. [Flux de Données](#flux-de-données)
5. [Algorithmes Détaillés](#algorithmes-détaillés)
6. [Modèle d'IA](#modèle-dia)
7. [Sécurité et Conformité](#sécurité-et-conformité)
8. [Performance et Scalabilité](#performance-et-scalabilité)
9. [Déploiement](#déploiement)
10. [Maintenance et Evolution](#maintenance-et-evolution)

---

## 1. Vue d'Ensemble Architecture

### 1.1 Architecture en Couches

```
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                        │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐     │
│  │  Interface  │    │   API REST   │    │   Webhooks  │     │
│  │     Web     │    │   (FastAPI)  │    │  (futur)    │     │
│  └─────────────┘    └──────────────┘    └─────────────┘     │
└───────────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE ORCHESTRATION                        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │          Moteur de Scoring Principal                 │    │
│  │  • Coordination des analyseurs                       │    │
│  │  • Calcul des scores pondérés                        │    │
│  │  • Génération des rapports                           │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE MÉTIER (IA)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Analyseur │  │Analyseur │  │  Service │  │  Moteur  │    │
│  │   CV     │  │  Offre   │  │Embeddings│  │Similarité│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└───────────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE EXTRACTION                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │ Extracteur │ │ Extracteur │ │ Extracteur │               │
│  │Compétences │ │ Expérience │ │ Formation  │               │
│  └────────────┘ └────────────┘ └────────────┘               │
└───────────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE INFRASTRUCTURE                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Configuration │  │Journalisation│  │  Sécurité    │       │
│  │ Centralisée  │  │  Structurée  │  │  & RGPD      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Pattern Architectural

**Pattern Principal** : Clean Architecture + Hexagonal Architecture

- **Indépendance des frameworks** : Logique métier isolée
- **Testabilité** : Chaque couche testable indépendamment
- **Indépendance de l'UI** : Changement d'interface sans impact métier
- **Indépendance des données** : Persistance découplée
- **Règles métier** : Au cœur du système

---

## 2. Principes de Conception

### 2.1 SOLID Principles

✅ **Single Responsibility** : Chaque classe a une responsabilité unique  
✅ **Open/Closed** : Ouvert à l'extension, fermé à la modification  
✅ **Liskov Substitution** : Interfaces cohérentes  
✅ **Interface Segregation** : Interfaces spécifiques et ciblées  
✅ **Dependency Inversion** : Dépendances vers abstractions

### 2.2 Patterns de Conception Utilisés

- **Singleton** : Configuration globale, Journaliseur
- **Strategy** : Différents extracteurs interchangeables
- **Factory** : Création d'analyseurs
- **Observer** : Événements de logging
- **Template Method** : Flux d'analyse standardisé

### 2.3 Principes Métier

🎯 **Explicabilité** : Chaque score doit être justifiable  
🎯 **Reproductibilité** : Mêmes entrées → mêmes résultats  
🎯 **Auditabilité** : Traçabilité complète des calculs  
🎯 **Équité** : Minimisation des biais algorithmiques  
🎯 **Performance** : Réponse en < 5 secondes

---

## 3. Architecture Logicielle

### 3.1 Modules Core (Coeur)

#### Configuration (`configuration.py`)

**Responsabilité** : Centralisation de tous les paramètres système

**Classes Principales** :
- `ConfigurationScoring` : Pondérations des critères
- `ConfigurationIA` : Paramètres du modèle d'embeddings
- `ConfigurationSecurite` : Paramètres RGPD et sécurité
- `GestionnaireConfiguration` : Singleton de configuration

**Validations** :
- Somme des poids = 1.0
- Cohérence des paramètres
- Vérification au démarrage

#### Journalisation (`journalisation.py`)

**Responsabilité** : Logging structuré conforme standards bancaires

**Fonctionnalités** :
- Format JSON pour parsing automatisé
- Anonymisation automatique (emails, téléphones, etc.)
- Rotation des logs
- Multi-handlers (console + fichier)
- Niveaux : DEBUG, INFO, WARNING, ERROR, CRITICAL

**Conformité** :
- Retention : 90 jours
- Anonymisation : Obligatoire
- Audit trail : Complet

### 3.2 Modules Analyse

#### Extracteur de Compétences

**Algorithme** :

1. **Normalisation** : Mise en minuscules, suppression caractères spéciaux
2. **Matching Exact** : Regex avec délimiteurs de mots
3. **Scoring Confiance** :
   - 1 mention : confiance 60%
   - 2 mentions : confiance 70%
   - 3+ mentions : confiance 80-100%
4. **Déduplication** : Ensemble unique de compétences

**Dictionnaires** :
- 80+ compétences techniques bancaires
- 25+ soft skills valorisés
- Mise à jour trimestrielle recommandée

#### Extracteur d'Expérience

**Patterns de Détection** :
```regex
Années : (\d+)\s*(?:ans?|années?)\s*(?:d[''])?(?:expérience|exp)
Durées : (\d{4})\s*[-–]\s*(\d{4}|présent|actuel)
Séniorité : \b(junior|confirmé|senior|expert|lead|manager)\b
```

**Calcul** :
- Somme des périodes détectées
- Validation cohérence temporelle
- Bonus séniorité : +2% par niveau

#### Extracteur de Formation

**Niveaux Reconnus** :
```
Bac       : Niveau 1
BTS/DUT   : Niveau 2
Licence   : Niveau 3
Master/MBA: Niveau 4
Doctorat  : Niveau 5
```

**Certifications Valorisées** :
- CFA, FRM, CAIA (Finance)
- PMP, PRINCE2 (Gestion de projet)
- AWS, Azure, GCP (Cloud)
- CISSP, CISA (Sécurité)

### 3.3 Modules Correspondance

#### Service Embeddings

**Modèle** : `paraphrase-multilingual-MiniLM-L12-v2`

**Caractéristiques** :
- Dimension : 384 features
- Langues : 50+ (focus FR/EN)
- Vitesse : ~500 embeddings/sec (CPU)
- Mémoire : ~120 Mo

**Process** :
1. Chargement modèle (cache en RAM)
2. Tokenization du texte
3. Forward pass du transformer
4. Mean pooling sur tokens
5. Normalisation L2

**Optimisations** :
- Batch processing (32 textes)
- Conversion numpy (pas torch)
- Pas de gradient (inférence only)

#### Moteur de Similarité

**Similarité Cosinus** :
```
cos(A,B) = (A·B) / (||A|| × ||B||)

Avec:
- A·B : Produit scalaire
- ||A|| : Norme euclidienne de A
- Résultat : [-1, 1] normalisé [0, 1]
```

**Similarité Jaccard** :
```
J(A,B) = |A ∩ B| / |A ∪ B|

Avec:
- A, B : Ensembles de compétences
- Intersection : Compétences communes
- Union : Toutes compétences
```

#### Moteur de Scoring

**Formule Générale** :
```
Score_Final = Σ(i=1 to 5) Score_i × Poids_i

Avec:
Score_1 = Score_Compétences (45%)
Score_2 = Score_Expérience  (25%)
Score_3 = Score_Formation   (15%)
Score_4 = Score_Langues     (10%)
Score_5 = Score_SoftSkills  ( 5%)
```

**Détail Score Compétences** :
```
Score_Comp = (0.7 × Jaccard + 0.3 × Cosinus) × 100

Où:
- Jaccard : Correspondance exacte
- Cosinus : Similarité sémantique
- Pondération 70/30 privilégie l'exact
```

---

## 4. Flux de Données

### 4.1 Flux Principal d'Analyse

```
┌──────────────┐
│  Utilisateur │
└──────┬───────┘
       │ Upload CV + Offre
       ▼
┌──────────────────┐
│   Validation     │ ◄── Taille < 10Mo, Format OK
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Nettoyage      │ ◄── Normalisation, Suppression contrôles
└──────┬───────────┘
       │
       ├─────────────────────┬──────────────────┐
       │                     │                  │
       ▼                     ▼                  ▼
┌─────────────┐      ┌─────────────┐    ┌─────────────┐
│Analyse CV   │      │Analyse Offre│    │Embeddings   │
└─────┬───────┘      └─────┬───────┘    └─────┬───────┘
      │                    │                   │
      └────────────────────┴───────────────────┘
                           │
                           ▼
                ┌──────────────────┐
                │  Calcul Scores   │
                │  • Compétences   │
                │  • Expérience    │
                │  • Formation     │
                │  • Langues       │
                │  • Soft Skills   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Score Pondéré    │
                │    Final         │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │Génération Rapport│
                │  • Résumé        │
                │  • Détails       │
                │  • Recommandations│
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   Affichage      │
                │  Utilisateur     │
                └───────────────────