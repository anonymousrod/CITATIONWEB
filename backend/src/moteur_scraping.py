# Chemin : backend/src/moteur_scraping.py
import asyncio
import threading
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import re
import logging
from .modeles import CitationBD, StatutScraping
from .supabase_client import televerser_image_depuis_url, inserer_citation
from typing import Dict, Any, Optional

# Configuration simple du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Gestion de l'État Global ---
# Ce dictionnaire stocke l'état du scraper, accessible par l'API principale (main.py)
ETAT_GLOBAL: Dict[str, Any] = {
    "statut_global": "Inactif", # Inactif, En cours, Terminé, Erreur
    "elements_traites": 0,
    "doit_arreter": False       # Flag pour signaler l'arrêt demandé
}

# --- 2. Fonctions de Contrôle de l'API ---

def obtenir_statut() -> StatutScraping:
    """Retourne l'état actuel pour le Frontend."""
    return StatutScraping(
        statut_global=ETAT_GLOBAL["statut_global"],
        elements_traites=ETAT_GLOBAL["elements_traites"]
    )

def demarrer_scraping(sujet: str):
    """Initialise l'état et lance la tâche de scraping dans un thread séparé."""
    if ETAT_GLOBAL["statut_global"] == "En cours":
        return {"message": "Le scraping est déjà en cours."}
    
    # Réinitialisation de l'état
    ETAT_GLOBAL.update({
        "statut_global": "En cours",
        "elements_traites": 0,
        "doit_arreter": False
    })
    
    # Lancer l'opération dans un thread dédié pour ne pas bloquer l'API
    thread = threading.Thread(target=_thread_starter, args=(sujet,))
    thread.start()
    
    logging.info(f"Tâche de scraping démarrée pour le sujet: {sujet}")
    return {"message": f"Scraping démarré pour le sujet: {sujet}"}

def arreter_scraping():
    """Signale au scraper qu'il doit s'arrêter lors de la prochaine itération."""
    if ETAT_GLOBAL["statut_global"] == "En cours":
        ETAT_GLOBAL["doit_arreter"] = True
        return {"message": "Signal d'arrêt envoyé. Le scraper s'arrêtera prochainement."}
    return {"message": "Le scraper n'est pas en cours d'exécution."}

# --- 3. Logique de Threading et d'Asyncio ---

def _thread_starter(sujet: str):
    """
    Point d'entrée pour le thread. Crée une nouvelle boucle d'événements 
    asyncio et y exécute la tâche de scraping.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_executer_tache_scraping(sujet))
    loop.close()

# --- 4. Moteur Playwright (Logique Asynchrone Principale) ---

async def _executer_tache_scraping(sujet: str):
    """
    Fonction asynchrone qui contient le moteur Playwright et la boucle d'extraction.
    Gère la pagination pour scraper toutes les pages.
    """
    sujet_formatte = sujet.lower().replace(' ', '-')
    url_cible = f"https://www.brainyquote.com/topics/{sujet_formatte}-quotes"
    
    ETAT_GLOBAL["statut_global"] = "En cours"
    
    playwright = None
    browser = None
    try:
        playwright = await async_playwright().start()
        logging.info("Lancement du navigateur Firefox...")
        browser = await playwright.firefox.launch(headless=True)
        page = await browser.new_page()
        logging.info(f"Accès à l'URL de départ: {url_cible}")
        await page.goto(url_cible, wait_until="domcontentloaded")

        # Tenter de cliquer sur le bouton d'acceptation des cookies une seule fois
        try:
            logging.info("Recherche du bouton d'acceptation des cookies...")
            cookie_button = page.locator('button:has-text("Accept all")').first
            await cookie_button.click(timeout=5000)
            logging.info("Bouton des cookies cliqué.")
        except PlaywrightTimeoutError:
            logging.warning("Bouton d'acceptation des cookies non trouvé, continuation.")

        # Boucle principale pour la pagination
        page_actuelle = 1
        while True:
            logging.info(f"--- Scraping de la page {page_actuelle} ---")
            
            CITATION_CONTAINER_SELECTOR = "div.grid-item.bqQt"
            try:
                # Attendre que le sélecteur soit visible sur la page actuelle
                await page.wait_for_selector(CITATION_CONTAINER_SELECTOR, timeout=15000)
            except PlaywrightTimeoutError:
                logging.warning(f"Aucun conteneur de citation trouvé sur la page du a la limite de temps {page_actuelle}. Fin possible.")
                break

            elements_citations = await page.locator(CITATION_CONTAINER_SELECTOR).all()
            logging.info(f"Trouvé {len(elements_citations)} conteneurs de citations sur la page {page_actuelle}.")

            for i, conteneur in enumerate(elements_citations):
                if ETAT_GLOBAL["doit_arreter"]: break
                try:
                    element_lien = conteneur.locator('a.b-qt').first
                    texte_citation = await element_lien.inner_text() or "N/A"
                    lien_citation = "https://www.brainyquote.com" + (await element_lien.get_attribute("href") or "")

                    element_auteur = conteneur.locator('a.bq-aut').first
                    auteur_nom = await element_auteur.inner_text() or "Inconnu"
                    
                    image_locator = conteneur.locator('div.qti-listm img')
                    url_image_source = None
                    if await image_locator.count() > 0:
                        url_image_source = await image_locator.first.get_attribute('src')
                    
                    url_image_publique = "N/A"
                    if url_image_source:
                        nom_fichier = f"{sujet_formatte}_{auteur_nom.replace(' ', '_').replace('.', '')}_{page_actuelle}_{i}.jpg"
                        if not url_image_source.startswith('http'):
                            url_image_source = f"https://www.brainyquote.com{url_image_source}"
                        url_publique_result = televerser_image_depuis_url(url_image_source, nom_fichier)
                        if url_publique_result:
                            url_image_publique = url_publique_result

                    citation = CitationBD(auteur_nom=auteur_nom.strip(), texte_citation=texte_citation.strip(), lien_citation=lien_citation, url_image=url_image_publique, sujet=sujet)
                    
                    if inserer_citation(citation):
                        ETAT_GLOBAL["elements_traites"] += 1

                except Exception as e:
                    logging.error(f"Erreur sur un élément de la page {page_actuelle}: {e}")
            
            if ETAT_GLOBAL["doit_arreter"]: break

            # Logique de pagination améliorée
            next_button_locator = page.locator('a.page-link:has-text("Next")')
            if await next_button_locator.count() > 0:
                logging.info("Passage à la page suivante...")
                await next_button_locator.click()
                page_actuelle += 1
                # La boucle recommencera et attendra le sélecteur sur la nouvelle page
            else:
                logging.info("Dernière page atteinte. Fin du scraping.")
                break

        if ETAT_GLOBAL["doit_arreter"]:
            ETAT_GLOBAL["statut_global"] = "Arrêté"
        else:
            ETAT_GLOBAL["statut_global"] = "Terminé"
        logging.info(f"Extraction finalisée. Statut: {ETAT_GLOBAL['statut_global']}. Total: {ETAT_GLOBAL['elements_traites']} éléments.")

    except Exception as e:
        logging.error(f"Une erreur majeure est survenue: {e}")
        if ETAT_GLOBAL["elements_traites"] > 0:
            ETAT_GLOBAL["statut_global"] = "Partiellement complété"
            ETAT_GLOBAL["message"] = f"Tâche terminée avec des erreurs après avoir traité {ETAT_GLOBAL['elements_traites']} éléments. Erreur: {e}"
        else:
            ETAT_GLOBAL["statut_global"] = "Erreur"
            ETAT_GLOBAL["message"] = str(e)
        if page: 
            try:
                await page.screenshot(path='debug_screenshot.png')
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
                logging.info("Screenshot et HTML de débogage enregistrés.")
            except Exception as de:
                logging.error(f"Impossible de sauvegarder les infos de débogage: {de}")
    finally:
        if browser: await browser.close()
        if playwright: await playwright.stop()
        logging.info("Ressources Playwright libérées.")