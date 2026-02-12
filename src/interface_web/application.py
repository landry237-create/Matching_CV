"""
Application Web FastAPI
Interface utilisateur professionnelle pour le système de matching
Auteur : Architecture IA Banque
"""

import uuid
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import PyPDF2
import docx
from typing import Optional, List, Dict, Any

from src.coeur.journalisation import journaliseur
from src.analyse.analyseur_cv import AnalyseurCV
from src.analyse.analyseur_offre import AnalyseurOffre
from src.correspondance.moteur_scoring import MoteurScoring
from src.rapport.generateur_rapport import GenerateurRapport
from src.rapport.generateur_latex import GenerateurRapportLaTeX


# ═══════════════════════════════════════════════════════════
# CONFIGURATION APPLICATION
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="Système de Matching CV/Offre - Banque",
    description="Solution d'intelligence artificielle pour le recrutement bancaire",
    version="1.0.0"
)

# Chemins
RACINE = Path(__file__).parent
TEMPLATES = RACINE / "templates"
STATIC = RACINE / "static"

# Templates Jinja2
templates = Jinja2Templates(directory=str(TEMPLATES))

# Servir fichiers statiques (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

# Services
analyseur_cv = AnalyseurCV()
analyseur_offre = AnalyseurOffre()
moteur_scoring = MoteurScoring()
generateur_rapport = GenerateurRapport()
generateur_latex = GenerateurRapportLaTeX()

# Cache des résultats d'analyse (pour génération PDF à la demande)
resultat_cache = {}


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def page_accueil(request: Request):
    """
    Page d'accueil de l'application.
    """
    journaliseur.info("Accès à la page d'accueil")
    
    return templates.TemplateResponse(
        "accueil.html",
        {"request": request}
    )


@app.get("/documentation", response_class=HTMLResponse)
async def page_documentation(request: Request):
    """
    Page de documentation détaillée.
    """
    journaliseur.info("Accès à la page documentation")
    
    return templates.TemplateResponse(
        "documentation.html",
        {"request": request}
    )


@app.get("/support", response_class=HTMLResponse)
async def page_support(request: Request):
    """
    Page de support avec FAQ et tutoriels.
    """
    journaliseur.info("Accès à la page support")
    
    return templates.TemplateResponse(
        "support.html",
        {"request": request}
    )


@app.get("/contact", response_class=HTMLResponse)
async def page_contact(request: Request):
    """
    Page de contact.
    """
    journaliseur.info("Accès à la page contact")
    
    return templates.TemplateResponse(
        "contact.html",
        {"request": request}
    )


@app.post("/analyser")
async def analyser_matching(
    fichier_cv: UploadFile = File(...),
    texte_offre: str = Form(...)
):
    """
    Endpoint principal : analyse du matching CV ↔ Offre.
    
    Args:
        fichier_cv: Fichier PDF, DOCX ou TXT du CV
        texte_offre: Texte de l'offre d'emploi
        
    Returns:
        JSON avec résultats du matching
    """
    # Génération ID de session unique
    identifiant_session = str(uuid.uuid4())
    
    journaliseur.info(
        f"[{identifiant_session}] Nouvelle analyse - "
        f"Fichier: {fichier_cv.filename}, "
        f"Taille offre: {len(texte_offre)} caractères"
    )
    
    try:
        # ═══════════════════════════════════════════════════════════
        # 1. EXTRACTION DU TEXTE DU CV
        # ═══════════════════════════════════════════════════════════
        
        texte_cv = await extraire_texte_cv(fichier_cv, identifiant_session)
        
        if not texte_cv or len(texte_cv) < 50:
            raise HTTPException(
                status_code=400,
                detail="Le CV semble vide ou illisible. Veuillez vérifier le fichier."
            )
        
        # ═══════════════════════════════════════════════════════════
        # 2. VALIDATION OFFRE
        # ═══════════════════════════════════════════════════════════
        
        if not texte_offre or len(texte_offre) < 50:
            raise HTTPException(
                status_code=400,
                detail="L'offre d'emploi est trop courte. Minimum 50 caractères requis."
            )
        
        # ═══════════════════════════════════════════════════════════
        # 3. ANALYSE CV
        # ═══════════════════════════════════════════════════════════
        
        profil_cv = analyseur_cv.analyser(texte_cv, identifiant_session)
        
        # ═══════════════════════════════════════════════════════════
        # 4. ANALYSE OFFRE
        # ═══════════════════════════════════════════════════════════
        
        profil_offre = analyseur_offre.analyser(texte_offre, identifiant_session)
        
        # ═══════════════════════════════════════════════════════════
        # 5. CALCUL SCORING
        # ═══════════════════════════════════════════════════════════
        
        resultat_scoring = moteur_scoring.calculer_score_global(
            profil_cv,
            profil_offre,
            identifiant_session
        )
        
        # ═══════════════════════════════════════════════════════════
        # 6. GÉNÉRATION RAPPORT
        # ═══════════════════════════════════════════════════════════
        
        rapport = generateur_rapport.generer_rapport_complet(
            resultat_scoring,
            profil_cv,
            profil_offre,
            identifiant_session
        )
        
        # ═══════════════════════════════════════════════════════════
        # 7. RÉPONSE
        # ═══════════════════════════════════════════════════════════
        
        journaliseur.info(
            f"[{identifiant_session}] Analyse terminée avec succès - "
            f"Score: {resultat_scoring['score_final']}/100"
        )
        
        # Stocker les résultats en cache pour accès ultérieur
        resultat_cache[identifiant_session] = {
            'resultat_scoring': resultat_scoring,
            'profil_cv': profil_cv,
            'profil_offre': profil_offre
        }
        
        return JSONResponse(content={
            "succes": True,
            "identifiant_session": identifiant_session,
            "resultat": resultat_scoring,
            "rapport": rapport,
            "url_pdf": f"/rapport-pdf/{identifiant_session}"
        })
    
    except HTTPException:
        raise
    
    except Exception as e:
        journaliseur.erreur(
            f"[{identifiant_session}] Erreur lors de l'analyse : {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne : {str(e)}"
        )


@app.get("/rapport-pdf/{identifiant_session}")
async def generer_rapport_pdf(identifiant_session: str):
    """
    Génère et retourne un rapport LaTeX sophistiqué en PDF.
    
    Args:
        identifiant_session: ID de session précédente
        
    Returns:
        Fichier PDF téléchargeable
    """
    journaliseur.info(f"[{identifiant_session}] Génération rapport PDF LaTeX demandée")
    
    try:
        # Récupérer les données depuis le cache
        if identifiant_session not in resultat_cache:
            raise HTTPException(
                status_code=404,
                detail="Session non trouvée. Veuillez d'abord effectuer une analyse."
            )
        
        donnees = resultat_cache[identifiant_session]
        
        # Générer le PDF LaTeX
        pdf_bytes = generateur_latex.generer_rapport_latex(
            donnees['resultat_scoring'],
            donnees['profil_cv'],
            donnees['profil_offre'],
            identifiant_session
        )
        
        # Retourner le PDF en tant que FileResponse
        return FileResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            filename=f"rapport_matching_{identifiant_session[:8]}.pdf"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        journaliseur.erreur(
            f"[{identifiant_session}] Erreur génération PDF : {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du PDF : {str(e)}"
        )


async def extraire_texte_cv(
    fichier: UploadFile,
    identifiant_session: str
) -> str:
    """
    Extrait le texte d'un fichier CV (PDF, DOCX, TXT).
    
    Args:
        fichier: Fichier uploadé
        identifiant_session: ID de session pour logs
        
    Returns:
        Texte extrait
    """
    contenu = await fichier.read()
    nom_fichier = fichier.filename.lower()
    
    try:
        # ═══════════════════════════════════════════════════════════
        # PDF
        # ═══════════════════════════════════════════════════════════
        
        if nom_fichier.endswith('.pdf'):
            journaliseur.debug(f"[{identifiant_session}] Extraction PDF")
            
            import io
            pdf_file = io.BytesIO(contenu)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            texte = ""
            for page in pdf_reader.pages:
                texte += page.extract_text() + "\n"
            
            return texte.strip()
        
        # ═══════════════════════════════════════════════════════════
        # DOCX
        # ═══════════════════════════════════════════════════════════
        
        elif nom_fichier.endswith('.docx'):
            journaliseur.debug(f"[{identifiant_session}] Extraction DOCX")
            
            import io
            docx_file = io.BytesIO(contenu)
            doc = docx.Document(docx_file)
            
            texte = ""
            for paragraphe in doc.paragraphs:
                texte += paragraphe.text + "\n"
            
            return texte.strip()
        
        # ═══════════════════════════════════════════════════════════
        # TXT
        # ═══════════════════════════════════════════════════════════
        
        elif nom_fichier.endswith('.txt'):
            journaliseur.debug(f"[{identifiant_session}] Extraction TXT")
            
            return contenu.decode('utf-8', errors='ignore').strip()
        
        # ═══════════════════════════════════════════════════════════
        # FORMAT NON SUPPORTÉ
        # ═══════════════════════════════════════════════════════════
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non supporté : {nom_fichier}. "
                       f"Formats acceptés : PDF, DOCX, TXT"
            )
    
    except Exception as e:
        journaliseur.error(
            f"[{identifiant_session}] Erreur extraction texte : {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Impossible d'extraire le texte du CV : {str(e)}"
        )


@app.get("/sante")
async def verifier_sante():
    """
    Endpoint de santé pour monitoring.
    """
    return {
        "statut": "OK",
        "service": "Système de Matching CV/Offre",
        "version": "1.0.0"
    }


# ═══════════════════════════════════════════════════════════
# GESTION ERREURS
# ═══════════════════════════════════════════════════════════

@app.exception_handler(404)
async def gestionnaire_404(request: Request, exc):
    """Gestion des erreurs 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Page non trouvée"}
    )


@app.exception_handler(500)
async def gestionnaire_500(request: Request, exc):
    """Gestion des erreurs 500."""
    journaliseur.erreur(f"Erreur serveur 500 : {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )


# ═══════════════════════════════════════════════════════════
# DÉMARRAGE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    journaliseur.info("Démarrage de l'application web...")
    
    uvicorn.run(
        "application:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )