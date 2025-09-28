# Chemin : backend/src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Classe de configuration générale de l'application
class ParametresApp(BaseSettings):
    # Indique à Pydantic de chercher les variables dans le fichier .env
    # 'extra='ignore' permet d'ignorer toute autre variable non listée ici
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Clés Supabase
    SUPABASE_URL: str = Field(..., description="URL de votre projet Supabase.")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Clé Service Role de Supabase (SECRÈTE).")
    
    # Paramètres de l'API (pour le lancement local)
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Nom du bucket de stockage (doit correspondre à ce que vous avez créé dans Supabase)
    NOM_BUCKET_IMAGES: str = "quote-images" 

# Instance unique des paramètres
parametres = ParametresApp()

# Note : Le "..." dans Field indique que le champ est obligatoire.