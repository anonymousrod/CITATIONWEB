<script setup lang="ts">
import { useScrapingStore } from '~/stores/scraping';
import { computed } from 'vue';

const store = useScrapingStore();

const citationsAffichees = computed(() => store.citations.slice(0, 10));
const totalCitations = computed(() => store.citations.length);
</script>

<template>
    <div class="mt-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">
            Citations Collectées (Total: {{ totalCitations }})
        </h2>

        <div v-if="store.citations.length === 0" class="empty-state">
            <p>Aucune citation trouvée dans la base de données. Lancez un scraping pour collecter des données !</p>
        </div>

        <div v-else class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Sujet</th>
                        <th>Auteur</th>
                        <th>Citation</th>
                        <th>Lien</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="citation in citationsAffichees" :key="citation.id">
                        <td>{{ citation.id }}</td>
                        <td>{{ citation.sujet }}</td>
                        <td>{{ citation.auteur_nom }}</td>
                        <td>{{ citation.texte_citation }}</td>
                        <td><a :href="citation.lien_citation" target="_blank" class="table-link">Voir la source</a></td>
                    </tr>
                </tbody>
            </table>
            <p v-if="totalCitations > 10" class="note-affichage">
                Affiche les {{ citationsAffichees.length }} premières citations sur {{ totalCitations }}.
            </p>
        </div>
    </div>
</template>

<style scoped>
/* Styles spécifiques pour le tableau */
.mt-8 {
    margin-top: 32px;
}
.table-container {
    overflow-x: auto;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    padding: 1px; /* Pour gérer le border-radius avec overflow */
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}
th {
    background-color: #f9fafb;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
tr:hover {
    background-color: #f3f4f6;
}
.empty-state {
    padding: 24px;
    background-color: #fef3c7;
    border: 1px solid #fcd34d;
    border-radius: 6px;
    color: #92400e;
    text-align: center;
}
.table-link {
    color: #4f46e5;
    text-decoration: none;
}
.table-link:hover {
    text-decoration: underline;
}
.note-affichage {
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #6b7280;
    background-color: #f9fafb;
    border-top: 1px solid #e5e7eb;
    margin-bottom: 0;
}
</style>
