// Path: frontend/stores/scraping.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'

// Interface pour le statut global de l'API
interface StatutScraping {
  statut_global: 'Inactif' | 'En cours' | 'Arrêté' | 'Terminé' | 'Erreur'
  elements_traites: number
  message: string | null
}

// Interface pour la structure des citations
interface Citation {
  id: number;
  sujet: string;
  auteur_nom: string;
  texte_citation: string;
  lien_citation: string;
  url_image: string;
}

export const useScrapingStore = defineStore('scraping', () => {
  // Récupération de l'URL du backend
  const config = useRuntimeConfig()
  const BACKEND_URL = config.public.backendUrl

  // --- États ---
  const statut = ref<StatutScraping>({ statut_global: 'Inactif', elements_traites: 0, message: null })
  const citations = ref<Citation[]>([])
  const isScraping = computed(() => statut.value.statut_global === 'En cours')

  // --- Actions ---

  // 1. Lancer le scraping
  async function lancerScraping(sujet: string) {
    statut.value.statut_global = 'En cours'
    statut.value.message = `Démarrage du scraping pour ${sujet}...`
    statut.value.elements_traites = 0

    try {
      const response = await $fetch(`${BACKEND_URL}/api/lancer`, {
        method: 'POST',
        body: { sujet },
      })
      statut.value.message = (response as { message: string }).message
    } catch (error) {
      console.error('Erreur au lancement du scraping:', error)
      statut.value.statut_global = 'Erreur'
      statut.value.message = "Erreur: Impossible de lancer le scraping (Backend inaccessible?)."
    }
  }

  // 2. Arrêter le scraping
  async function arreterScraping() {
    statut.value.message = 'Envoi de la commande d\'arrêt...'
    try {
      await $fetch(`${BACKEND_URL}/api/arreter`, { method: 'POST' })
      statut.value.statut_global = 'Arrêté'
      statut.value.message = 'Scraping arrêté par l\'utilisateur.'
    } catch (error) {
      console.error('Erreur à l\'arrêt du scraping:', error)
      statut.value.message = "Erreur: Impossible d'arrêter le scraping."
    }
  }

  // 3. Mettre à jour le statut (polling)
  async function verifierStatut() {
    try {
      const data = await $fetch<StatutScraping>(`${BACKEND_URL}/api/statut`)
      statut.value = data
    } catch (error) {
      // Ignorer les erreurs de statut pour garder l'interface fluide
      console.error('Erreur lors de la vérification du statut:', error)
    }
  }

  // 4. Charger les citations (pour le tableau)
  async function chargerCitations() {
    try {
      const data = await $fetch<Citation[]>(`${BACKEND_URL}/api/citations`)
      citations.value = data
    } catch (error) {
      console.error('Erreur lors du chargement des citations:', error)
      citations.value = []
    }
  }

  return { 
    statut, 
    citations, 
    isScraping,
    lancerScraping, 
    arreterScraping, 
    verifierStatut, 
    chargerCitations 
  }
})