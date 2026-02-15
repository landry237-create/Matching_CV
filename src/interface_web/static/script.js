/**
 * SYSTÈME DE MATCHING CV/OFFRE - SCRIPT PRINCIPAL
 * Gestion des interactions et affichage des résultats
 */

// ═══════════════════════════════════════════════════════════════
// INITIALISATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
    initialiserUploadFichier();
    initialiserCompteurCaracteres();
    initialiserFormulaire();
});

// ═══════════════════════════════════════════════════════════════
// GESTION UPLOAD FICHIER
// ═══════════════════════════════════════════════════════════════

function initialiserUploadFichier() {
    const zoneUpload = document.getElementById('zone-upload');
    const inputFichier = document.getElementById('fichier-cv');
    const fichierSelectionne = document.getElementById('fichier-selectionne');
    const nomFichier = document.getElementById('nom-fichier');
    const boutonSupprimer = document.getElementById('bouton-supprimer');
    
    // Changement de fichier
    inputFichier.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const fichier = this.files[0];
            
            // Validation taille (10 MB max)
            if (fichier.size > 10 * 1024 * 1024) {
                alert('Le fichier est trop volumineux. Taille maximale : 10 MB');
                this.value = '';
                return;
            }
            
            // Validation format
            const formatsAcceptes = ['.pdf', '.docx', '.txt'];
            const extension = '.' + fichier.name.split('.').pop().toLowerCase();
            
            if (!formatsAcceptes.includes(extension)) {
                alert('Format non supporté. Formats acceptés : PDF, DOCX, TXT');
                this.value = '';
                return;
            }
            
            // Afficher le fichier sélectionné
            nomFichier.textContent = fichier.name;
            zoneUpload.querySelector('.upload-placeholder').style.display = 'none';
            fichierSelectionne.style.display = 'flex';
        }
    });
    
    // Bouton supprimer
    boutonSupprimer.addEventListener('click', function() {
        inputFichier.value = '';
        zoneUpload.querySelector('.upload-placeholder').style.display = 'block';
        fichierSelectionne.style.display = 'none';
    });
    
    // Drag & Drop
    zoneUpload.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--dore)';
        this.style.background = 'var(--blanc)';
    });
    
    zoneUpload.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--bleu-clair)';
        this.style.background = 'var(--gris-clair)';
    });
    
    zoneUpload.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--bleu-clair)';
        this.style.background = 'var(--gris-clair)';
        
        const fichiers = e.dataTransfer.files;
        if (fichiers.length > 0) {
            inputFichier.files = fichiers;
            inputFichier.dispatchEvent(new Event('change'));
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// COMPTEUR DE CARACTÈRES
// ═══════════════════════════════════════════════════════════════

function initialiserCompteurCaracteres() {
    const textarea = document.getElementById('texte-offre');
    const compteur = document.getElementById('compteur');
    
    textarea.addEventListener('input', function() {
        compteur.textContent = this.value.length;
    });
}

// ═══════════════════════════════════════════════════════════════
// SOUMISSION FORMULAIRE
// ═══════════════════════════════════════════════════════════════

function initialiserFormulaire() {
    const formulaire = document.getElementById('formulaire-analyse');
    
    formulaire.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Récupération des données
        const fichierCV = document.getElementById('fichier-cv').files[0];
        const texteOffre = document.getElementById('texte-offre').value;
        
        // Validation
        if (!fichierCV) {
            alert('Veuillez sélectionner un CV');
            return;
        }
        
        if (texteOffre.length < 50) {
            alert('L\'offre d\'emploi doit contenir au moins 50 caractères');
            return;
        }
        
        // Afficher chargement
        afficherChargement();
        
        // Préparation FormData
        const formData = new FormData();
        formData.append('fichier_cv', fichierCV);
        formData.append('texte_offre', texteOffre);
        
        try {
            // Appel API
            const response = await fetch('/analyser', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const erreur = await response.json();
                throw new Error(erreur.detail || 'Erreur lors de l\'analyse');
            }
            
            const donnees = await response.json();
            
            // Afficher résultats
            afficherResultats(donnees);
            
        } catch (erreur) {
            console.error('Erreur:', erreur);
            alert('Une erreur est survenue : ' + erreur.message);
            masquerChargement();
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// AFFICHAGE CHARGEMENT
// ═══════════════════════════════════════════════════════════════

function afficherChargement() {
    document.getElementById('zone-chargement').style.display = 'block';
    document.getElementById('section-resultats').style.display = 'none';
    
    // Animation des étapes
    const etapes = [
        'Extraction du texte du CV...',
        'Analyse des compétences...',
        'Calcul de l\'expérience...',
        'Évaluation de la formation...',
        'Calcul des scores...',
        'Génération du rapport...'
    ];
    
    let index = 0;
    const intervalEtapes = setInterval(() => {
        if (index < etapes.length) {
            document.getElementById('etape-chargement').textContent = etapes[index];
            index++;
        } else {
            clearInterval(intervalEtapes);
        }
    }, 800);
}

function masquerChargement() {
    document.getElementById('zone-chargement').style.display = 'none';
}

// ═══════════════════════════════════════════════════════════════
// AFFICHAGE RÉSULTATS
// ═══════════════════════════════════════════════════════════════

function afficherResultats(donnees) {
    masquerChargement();
    
    const resultat = donnees.resultat;
    const rapport = donnees.rapport;
    
    // Afficher section résultats
    document.getElementById('section-resultats').style.display = 'block';
    
    // Scroll vers résultats
    document.getElementById('section-resultats').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
    
    // Remplir les données
    afficherScorePrincipal(resultat, rapport);
    afficherSousScores(resultat);
    afficherCompetences(resultat);
    afficherRecommandations(resultat);
}

// ─────────────────────────────────────────────────────────────── 
// SCORE PRINCIPAL
// ─────────────────────────────────────────────────────────────── 

function afficherScorePrincipal(resultat, rapport) {
    const scoreFinal = resultat.score_final;
    const niveau = resultat.niveau_correspondance;
    const couleur = resultat.couleur_affichage;
    
    // Valeur du score
    document.getElementById('valeur-score').textContent = Math.round(scoreFinal);
    
    // Niveau de correspondance
    const niveauElement = document.getElementById('niveau-correspondance');
    niveauElement.textContent = `Correspondance ${niveau}`;
    niveauElement.style.color = couleur;
    
    // Synthèse exécutive
    document.getElementById('synthese-executive').textContent = 
        rapport.synthese_executive;
    
    // Animation cercle de progression
    const cercle = document.getElementById('cercle-score');
    const circonference = 534; // 2 * π * r (r = 85)
    const offset = circonference - (scoreFinal / 100) * circonference;
    
    // Couleur du cercle selon score
    cercle.style.stroke = couleur;
    
    // Animation
    setTimeout(() => {
        cercle.style.strokeDashoffset = offset;
    }, 300);
}

// ─────────────────────────────────────────────────────────────── 
// SOUS-SCORES
// ─────────────────────────────────────────────────────────────── 

function afficherSousScores(resultat) {
    const conteneur = document.getElementById('liste-sous-scores');
    conteneur.innerHTML = '';
    
    const sousScores = resultat.sous_scores;
    const poids = resultat.poids_utilises;
    
    const ordre = ['competences', 'experience', 'formation', 'langues', 'soft_skills'];
    const labels = {
        'competences': 'Compétences Techniques',
        'experience': 'Expérience Professionnelle',
        'formation': 'Formation Académique',
        'langues': 'Compétences Linguistiques',
        'soft_skills': 'Soft Skills'
    };
    
    ordre.forEach(cle => {
        if (sousScores[cle]) {
            const score = sousScores[cle].score;
            const poidsPourcent = poids[cle] * 100;
            
            // Couleur selon score
            let couleur;
            if (score >= 80) couleur = '#28a745';
            else if (score >= 60) couleur = '#17a2b8';
            else if (score >= 40) couleur = '#ffc107';
            else couleur = '#dc3545';
            
            const itemHTML = `
                <div class="item-sous-score">
                    <div class="sous-score-en-tete">
                        <span class="sous-score-nom">${labels[cle]}</span>
                        <span class="sous-score-valeur" style="color: ${couleur}">
                            ${score.toFixed(1)}/100
                        </span>
                    </div>
                    <div class="sous-score-barre">
                        <div class="sous-score-progression" 
                             style="width: ${score}%; background: ${couleur};">
                        </div>
                    </div>
                    <div class="sous-score-details">
                        Poids : ${poidsPourcent.toFixed(0)}% | 
                        Contribution : ${(score * poids[cle]).toFixed(1)} points
                    </div>
                </div>
            `;
            
            conteneur.innerHTML += itemHTML;
        }
    });
}

// ─────────────────────────────────────────────────────────────── 
// COMPÉTENCES
// ─────────────────────────────────────────────────────────────── 

function afficherCompetences(resultat) {
    const comp = resultat.sous_scores.competences;
    
    // Compétences correspondantes
    const correspondantes = document.getElementById('competences-correspondantes');
    correspondantes.innerHTML = '';
    
    if (comp.correspondances && comp.correspondances.length > 0) {
        comp.correspondances.forEach(competence => {
            const tag = document.createElement('span');
            tag.className = 'tag correspondant';
            tag.textContent = competence;
            correspondantes.appendChild(tag);
        });
    } else {
        correspondantes.innerHTML = '<p style="color: var(--gris)">Aucune compétence correspondante</p>';
    }
    
    // Compétences manquantes
    const manquantes = document.getElementById('competences-manquantes');
    manquantes.innerHTML = '';
    
    if (comp.manquantes && comp.manquantes.length > 0) {
        comp.manquantes.forEach(competence => {
            const tag = document.createElement('span');
            tag.className = 'tag manquant';
            tag.textContent = competence;
            manquantes.appendChild(tag);
        });
    } else {
        manquantes.innerHTML = '<p style="color: var(--gris)">Toutes les compétences sont couvertes ✓</p>';
    }
    
    // Compétences additionnelles
    const additionnelles = document.getElementById('competences-additionnelles');
    additionnelles.innerHTML = '';
    
    if (comp.additionnelles && comp.additionnelles.length > 0) {
        comp.additionnelles.slice(0, 10).forEach(competence => {
            const tag = document.createElement('span');
            tag.className = 'tag additionnel';
            tag.textContent = competence;
            additionnelles.appendChild(tag);
        });
        
        if (comp.additionnelles.length > 10) {
            const plusTag = document.createElement('span');
            plusTag.className = 'tag additionnel';
            plusTag.textContent = `+${comp.additionnelles.length - 10} autres`;
            additionnelles.appendChild(plusTag);
        }
    } else {
        additionnelles.innerHTML = '<p style="color: var(--gris)">Aucune compétence additionnelle</p>';
    }
}

// ─────────────────────────────────────────────────────────────── 
// RECOMMANDATIONS
// ─────────────────────────────────────────────────────────────── 

function afficherRecommandations(resultat) {
    const conteneur = document.getElementById('liste-recommandations');
    conteneur.innerHTML = '';
    
    if (resultat.recommandations && resultat.recommandations.length > 0) {
        resultat.recommandations.forEach(reco => {
            const li = document.createElement('li');
            li.textContent = reco;
            conteneur.appendChild(li);
        });
    } else {
        conteneur.innerHTML = '<li>Aucune recommandation spécifique</li>';
    }
}