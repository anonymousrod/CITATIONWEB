# Chemin : backend/src/modeles.py
from pydantic import BaseModel, Field
from typing import Optional

# 1. Modèle pour l'entrée API (ce que le Frontend nous envoie)
class SujetRecherche(BaseModel):
    sujet: str = Field(..., description="Le mot-clé pour le scraping, ex: Motivational")

# 2. Modèle pour les données stockées dans la BD (table 'quotes')
class CitationBD(BaseModel):
    id: int
    # Noms des champs en français clair, pour la cohérence
    auteur_nom: str
    texte_citation: str
    lien_citation: str
    url_image: str  # Lien public de l'image stockée dans Supabase Storage
    sujet: str
    
# 3. Modèle pour le statut de l'opération (ce que l'API renvoie au Frontend)
class StatutScraping(BaseModel):
    # Les différents statuts possibles
    statut_global: str = Field(..., description="État actuel: Inactif, En cours, Terminé, Erreur.")
    # Le compteur pour la progression
    elements_traites: int = Field(0, description="Nombre d'éléments traités.")
    message: Optional[str] = None