<script setup lang="ts">
import { useScrapingStore } from '~/stores/scraping';
import { computed } from 'vue';

const store = useScrapingStore();

const citationsAffichees = computed(() => store.citations.slice(0, 10));
const totalCitations = computed(() => store.citations.length);
</script>

<template>
    <div class="table-wrapper">
        <h2 class="table-title">
            Citations Collectées <span class="total-count">({{ totalCitations }})</span>
        </h2>

        <div v-if="store.citations.length === 0" class="empty-state">
            <p>Aucune citation trouvée. Lancez un scraping pour commencer !</p>
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
                        <td data-label="ID">{{ citation.id }}</td>
                        <td data-label="Sujet">{{ citation.sujet }}</td>
                        <td data-label="Auteur">{{ citation.auteur_nom }}</td>
                        <td data-label="Citation">{{ citation.texte_citation }}</td>
                        <td data-label="Lien"><a :href="citation.lien_citation" target="_blank" class="table-link">Voir la source</a></td>
                    </tr>
                </tbody>
            </table>
            <p v-if="totalCitations > 10" class="note-affichage">
                Affichage des {{ citationsAffichees.length }} premières citations sur {{ totalCitations }}.
            </p>
        </div>
    </div>
</template>

<style scoped>
.table-wrapper {
    margin-top: 48px;
}

.table-title {
    font-size: 1.5rem; /* 24px */
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 24px;
}

.total-count {
    font-weight: 400;
    color: var(--color-text-secondary);
}

.table-container {
    overflow-x: auto;
    background-color: var(--color-bg-secondary);
    border-radius: 12px;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

th, td {
    padding: 16px 20px;
    text-align: left;
    border-bottom: 1px solid var(--color-border);
    white-space: nowrap;
}

td {
    color: var(--color-text-secondary);
}

th {
    background-color: var(--color-bg);
    font-weight: 600;
    color: var(--color-text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.75rem;
}

tr:last-child td {
    border-bottom: none;
}

tr:hover {
    background-color: var(--color-bg);
}

.empty-state {
    padding: 40px;
    background-color: var(--color-bg-secondary);
    border: 2px dashed var(--color-border);
    border-radius: 12px;
    color: var(--color-text-secondary);
    text-align: center;
    font-size: 1.1rem;
}

.table-link {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
}
.table-link:hover {
    text-decoration: underline;
    color: var(--color-primary-hover);
}

.note-affichage {
    padding: 12px 20px;
    font-size: 0.8rem;
    color: var(--color-text-muted);
    background-color: var(--color-bg);
    border-top: 1px solid var(--color-border);
    margin: 0;
    text-align: center;
}
</style>
