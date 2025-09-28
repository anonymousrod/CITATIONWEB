# Chemin : backend/main.py
import asyncio
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

# Correction pour l'erreur NotImplementedError de Playwright sur Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from src.supabase_client import recuperer_toutes_les_citations
import csv
import io
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from src.modeles import SujetRecherche, StatutScraping, CitationBD
from src.moteur_scraping import demarrer_scraping, obtenir_statut, arreter_scraping
from src.config import parametres
import logging

logging.basicConfig(level=logging.INFO)

# Initialisation de l'application FastAPI
app = FastAPI(title="API CitationsWeb", version="1.0")

# --- 1. Configuration CORS ---
# Crucial pour permettre au Frontend (Nuxt) de parler à ce Backend
origins = [
    "http://localhost:3000",  # L'URL par défaut de Nuxt
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Points de Terminaison (Endpoints) pour le Contrôle ---

@app.post("/api/lancer", response_model=dict)
async def lancer_scraping(sujet_recherche: SujetRecherche):
    """
    Démarre la tâche de scraping en arrière-plan.
    """
    # Le moteur_scraping gère lui-même le lancement asynchrone (asyncio.create_task)
    resultat = demarrer_scraping(sujet_recherche.sujet)
    return resultat

@app.post("/api/arreter", response_model=dict)
async def arreter_le_scraper():
    """
    Envoie un signal d'arrêt au moteur de scraping.
    """
    return arreter_scraping()

@app.get("/api/statut", response_model=StatutScraping)
async def verifier_statut():
    """
    Retourne l'état actuel et le nombre d'éléments traités.
    """
    return obtenir_statut()


# --- 3. Point de Terminaison pour les Données ---

@app.get("/api/citations", response_model=List[CitationBD])
async def get_citations():
    """
    Récupère toutes les citations de la base de données.
    Retourne une liste vide si aucune citation n'est trouvée.
    """
    citations = recuperer_toutes_les_citations()
    return citations

# --- 4. Point de Terminaison pour le Téléchargement ---

@app.get("/api/telecharger/{format}")
async def telecharger_citations(format: str):
    """
    Télécharge toutes les citations stockées dans la base de données
    dans le format spécifié (json ou csv).
    """
    citations = recuperer_toutes_les_citations()

    if not citations:
        raise HTTPException(status_code=404, detail="Aucune citation à télécharger.")

    if format.lower() == "json":
        return citations

    elif format.lower() == "csv":
        output = io.StringIO()
        # S'assurer que les noms de champs sont extraits correctement, même si la liste est vide après le filtrage
        fieldnames = citations[0].keys() if citations else []
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(citations)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=citations.csv"}
        )
        return response

    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json' ou 'csv'.")


# --- 4. Lancement du Serveur ---

if __name__ == "__main__":
    # Utilise les paramètres d'hôte et de port définis dans le fichier .env
    uvicorn.run(app, host=parametres.API_HOST, port=parametres.API_PORT)