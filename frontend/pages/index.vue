<script setup lang="ts">
import { useScrapingStore } from '~/stores/scraping';
import { ref, onMounted, onUnmounted, computed } from 'vue';
// NOTE: UInput et UButton ont été retirés, on utilise des éléments HTML simples maintenant
// import { UInput, UButton } from '#app/components'; // Remplacé par input et button

// Assurez-vous d'avoir un composant TableauCitations créé ou de le retirer temporairement s'il cause des problèmes
import TableauCitations from '~/components/TableauCitations.vue'; 
import { triggerBackendDownload } from '~/utils/export';


const store = useScrapingStore();
const sujet = ref('');
let intervalId: NodeJS.Timeout | null = null;

// Lance le scraping via le Store
const handleLancerScraping = () => {
    if (sujet.value) {
        store.lancerScraping(sujet.value);
        // Après le lancement, nous forçons la vérification immédiate du statut
        startPolling(); 
    }
};

// Démarre le polling (vérification du statut toutes les 3 secondes)
const startPolling = () => {
    // Si l'intervalle est déjà défini ou si le statut est déjà 'en cours', on ne fait rien
    if (intervalId && store.statut.statut_global === 'En cours') return; 
    
    // Assure que le store vérifie le statut immédiatement
    store.verifierStatut();

    intervalId = setInterval(() => {
        store.verifierStatut();
        // Arrête le polling si la tâche est terminée/arrêtée/en erreur
        if (store.statut.statut_global === 'Terminé' || store.statut.statut_global === 'Erreur' || store.statut.statut_global === 'Arrêté') {
            stopPolling();
            store.chargerCitations(); // Charger les résultats finaux
        }
    }, 3000);
};

// Arrête le polling
const stopPolling = () => {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
};

// Démarre le polling et charge les données existantes au montage
onMounted(async () => {
    await store.verifierStatut(); // On récupère le statut réel du backend
    store.chargerCitations(); // On charge les citations

    // Si le statut est "En cours", on démarre le polling
    if (store.statut.statut_global === 'En cours') {
        startPolling();
    }
});

// Arrête le polling lorsque le composant est détruit
onUnmounted(() => {
    stopPolling();
});

// Calcul de la classe de couleur pour le statut
const statutColorClass = computed(() => {
    switch (store.statut.statut_global) {
        case 'En cours':
            return 'bg-blue-500';
        case 'Terminé':
            return 'bg-green-500';
        case 'Erreur':
            return 'bg-red-500';
        case 'Arrêté':
            return 'bg-yellow-500';
        default:
            return 'bg-gray-500';
    }
});
</script>

<template>
    <!-- Utilisation des classes CSS simples -->
    <div class="container">
        <h1>CitationsWeb Scraper</h1>
        <p>Contrôle et visualisation du moteur d'extraction.</p>

        <div class="card">
            <h2>Contrôle du Scraping</h2>

            <div class="flex-row">
                <!-- Remplacement de UInput par input HTML -->
                <input 
                    type="text"
                    v-model="sujet" 
                    placeholder="Entrez un sujet (ex: motivational, funny, life)" 
                    class="input-field flex-grow"
                    :disabled="store.isScraping"
                />
                
                <!-- Remplacement de UButton par button HTML (Lancer) -->
                <button 
                    :disabled="store.isScraping || !sujet"
                    class="btn btn-indigo"
                    @click="handleLancerScraping"
                >
                    <span v-if="store.isScraping">Scraping en cours...</span>
                    <span v-else>Lancer le Scraping</span>
                </button>

                <!-- Remplacement de UButton par button HTML (Arrêter) -->
                <button 
                    v-if="store.isScraping"
                    class="btn btn-red"
                    @click="store.arreterScraping"
                >
                    Arrêter
                </button>

                <!-- Remplacement de UButton par button HTML (Recharger) -->
                <button 
                    class="btn btn-gray"
                    @click="store.chargerCitations"
                >
                    Recharger
                </button>
            </div>

            <div class="status-bar flex-space-between">
                <div class="flex-row" style="margin-bottom: 0;">
                    <span :class="['status-indicator', statutColorClass]"></span>
                    <p class="text-status-title" style="margin: 0;">Statut Global: 
                        <span class="text-status-value">{{ store.statut.statut_global }}</span>
                    </p>
                </div>
                <p class="text-status-title" style="margin: 0;">
                    Éléments Traités: <span class="text-status-value">{{ store.statut.elements_traites }}</span>
                </p>
            </div>
             <p v-if="store.statut.message" class="mt-2 text-sm text-gray-500 italic">
                Message: {{ store.statut.message }}
            </p>

            <div class="flex-row" style="margin-top: 20px;">
                <button 
                    class="btn btn-gray"
                    @click="triggerBackendDownload('csv')"
                >
                    Télécharger CSV
                </button>
                <button 
                    class="btn btn-gray"
                    @click="triggerBackendDownload('json')"
                >
                    Télécharger JSON
                </button>
            </div>
        </div>

        <!-- Assurez-vous d'avoir ce composant ou de le retirer/simuler -->
        <TableauCitations />
    </div>
</template>
