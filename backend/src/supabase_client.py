# Chemin : backend/src/supabase_client.py
from supabase import create_client, Client
from .config import parametres
from .modeles import CitationBD
import requests
import io
import logging
from typing import Optional

# Configuration simple du logger pour afficher les événements importants
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Initialisation du Client Supabase ---

# Tentative d'initialisation du client au chargement du module
try:
    # Utilisation des clés chargées par le module config (Base 1.2)
    supabase: Client = create_client(parametres.SUPABASE_URL, parametres.SUPABASE_SERVICE_KEY)
    logging.info("Connexion à Supabase établie avec succès.")
except Exception as e:
    logging.error(f"Erreur FATALE lors de la connexion à Supabase : {e}. Vérifiez votre fichier .env.")
    supabase = None

# --- 2. Fonction de Téléversement (Supabase Storage) ---

def televerser_image_depuis_url(url_image_source: str, nom_fichier_cible: str) -> Optional[str]:
    """
    Télécharge une image à partir d'une URL externe et la téléverse vers Supabase Storage.
    Retourne l'URL publique pour le lien de la DB.
    """
    if not supabase:
        return None # Sortie rapide si la connexion a échoué

    try:
        # Télécharger le contenu binaire de l'image source (avec timeout pour la robustesse)
        reponse_image = requests.get(url_image_source, stream=True, timeout=10)
        reponse_image.raise_for_status() # Lève une erreur si le statut n'est pas 200 (OK)

        # Lire le contenu en mémoire (objet BytesIO)
        contenu_binaire = io.BytesIO(reponse_image.content)
        
        # Chemin de stockage (nous mettons les images dans un sous-dossier 'auteurs')
        chemin_storage = f"auteurs/{nom_fichier_cible}"
        
        # Téléverser l'image dans le bucket spécifié dans config.py
        supabase.storage.from_(parametres.NOM_BUCKET_IMAGES).upload(
            file=contenu_binaire.getvalue(),
            path=chemin_storage,
            file_options={"content-type": reponse_image.headers.get('Content-Type', 'image/jpeg')}
        )

        # Récupérer l'URL publique de l'image (pour qu'elle soit affichable dans le frontend)
        url_publique = supabase.storage.from_(parametres.NOM_BUCKET_IMAGES).get_public_url(chemin_storage)
        
        logging.info(f"Image téléversée : {url_publique}")
        return url_publique
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors du téléchargement de l'image source: {e}")
        return None
    except Exception as e:
        logging.error(f"Erreur lors du téléversement vers Supabase Storage: {e}")
        return None

# --- 3. Fonction d'Insertion (Supabase Database) ---

def inserer_citation(citation: CitationBD) -> bool:
    """
    Insère un enregistrement (CitationBD) dans la table 'quotes' de la base de données.
    """
    if not supabase:
        return False
        
    try:
        # Convertir le modèle Pydantic en dictionnaire pour l'insertion SQL
        data_a_inserer = citation.model_dump()
        
        # Insertion des données dans la table 'quotes'
        resultat = supabase.table('quotes').insert([data_a_inserer]).execute()
        
        if not resultat.data:
            logging.error(f"Échec de l'insertion pour la citation de {citation.auteur_nom}")
            return False
            
        logging.info(f"Citation de {citation.auteur_nom} insérée avec succès.")
        return True
        
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion dans Supabase DB: {e}")
        return False

# --- 4. Fonction de Récupération (Supabase Database) ---

def recuperer_toutes_les_citations() -> list[dict]:
    """
    Récupère tous les enregistrements de la table 'quotes'.
    """
    if not supabase:
        return []

    try:
        resultat = supabase.table('quotes').select('*').execute()
        
        if not resultat.data:
            logging.info("Aucune citation trouvée dans la base de données.")
            return []
            
        logging.info(f"{len(resultat.data)} citations récupérées avec succès.")
        return resultat.data
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des citations depuis Supabase DB: {e}")
        return []