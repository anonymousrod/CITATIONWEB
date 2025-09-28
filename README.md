🏛️ Rôle de l'Application et Architecture
CitationsWeb est divisé en deux composants principaux, chacun avec une mission claire :

🧠 1. Le Cerveau (Backend - FastAPI)
Le Backend, développé avec FastAPI (Python), est le moteur de l'application. Son rôle est de gérer la complexité et les opérations gourmandes en temps :

Orchestration Asynchrone : Utilise asyncio pour lancer et surveiller la tâche de scraping (via un outil comme Playwright). Cela permet au serveur de répondre immédiatement aux requêtes du Frontend (comme les mises à jour de statut) même si le scraping dure plusieurs minutes.

Logique Métier : Il reçoit le sujet de recherche du client, gère la navigation, l'extraction des données brutes et leur nettoyage.

Persistance et Statut : Responsable du stockage des citations collectées dans la base de données (ex: Supabase) et du maintien d'un statut global unique accessible en temps réel.

Export : Génération des fichiers CSV et JSON demandés.

💻 2. L'Interface (Frontend - Nuxt/Vue)
Le Frontend est la console de contrôle interactive construite avec Nuxt 3 (Vue). Il sert d'interface entre l'utilisateur et le moteur asynchrone :

Contrôle Utilisateur : Permet à l'utilisateur de démarrer et d'arrêter la tâche de scraping en envoyant des requêtes POST au Backend.

Polling de Statut : Il effectue des requêtes courtes et fréquentes (GET /api/statut) pour mettre à jour l'état de la tâche (Inactif, En cours, Terminé) et afficher le nombre d'éléments traités.

Visualisation des Résultats : Affichage des citations collectées dans un tableau dynamique.

🧪 Tests d'API Cruciaux pour la Stabilité
Avant tout déploiement, ces endpoints doivent être testés rigoureusement pour garantir le comportement asynchrone attendu.

Endpoint

Méthode

Objectif du Test

Réussite Attendue

/api/lancer

POST

Vérifier le lancement du processus asynchrone.

Réponse immédiate du serveur (statut 202 Accepted ou 200 OK) confirmant que la tâche est en cours de démarrage, sans attendre la fin du scraping.

/api/statut

GET

Tester le mécanisme de polling et la mise à jour des données.

Le statut_global doit passer à "En cours". Le elements_traites doit s'incrémenter au fil du temps.

/api/arreter

POST

Confirmer la capacité du système à stopper une tâche longue.

Le statut_global doit passer à "Arrêté". Le scraping en arrière-plan doit cesser.

/api/citations

GET

Vérifier l'accès aux données stockées.

Retourne un tableau JSON contenant les objets Citation correctement formatés (avec auteur_nom, texte_citation, etc.).

/api/telecharger/csv

GET

Confirmer l'exportation des données.

Déclenche le téléchargement d'un fichier CSV contenant toutes les citations.

⚙️ Directives de Lancement Local (Rappel Essentiel)
Pour garantir que le Frontend et le Backend se synchronisent correctement :

Démarrer le Backend en premier (FastAPI) pour qu'il soit joignable.
cd C:\Users\FHB\Documents\CitationsWeb

### Étape 2 : Création de l'Environnement Virtuel

Créez et activez un environnement virtuel nommé `venv`.

```powershell
# 1. Crée l'environnement virtuel
python -m venv venv

# 2. Active l'environnement virtuel (pour PowerShell)
.\venv\Scripts\Activate.ps1

# Si vous utilisez un terminal standard (cmd) ou Bash :
# .\venv\Scripts\activate

Une fois activé, vous verrez **`(venv)`** au début de votre ligne de commande.

### Étape 3 : Installation des Dépendances Python

Utilisez le fichier `requirements.txt` pour installer tous les paquets en une seule commande :

```powershell
pip install -r requirements.txt

### Étape 4 : Installation des Navigateurs pour Playwright

Playwright a besoin d'installer les navigateurs qu'il utilisera pour le scraping (Chromium, Firefox, WebKit).

```powershell
playwright install

### Étape 5 : Lancement du Serveur FastAPI (Uvicorn)

Une fois tout est installé, vous pouvez démarrer le serveur. Assurez-vous que votre fichier principal FastAPI est nommé **`main.py`** et que l'objet principal de l'application est nommé **`app`**.

```powershell
# Démarre le serveur Uvicorn sur localhost:8000 avec rechargement automatique
uvicorn main:app --reload

Vous devriez voir un message confirmant que le serveur tourne :

Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

Votre Backend est maintenant opérationnel à **`http://localhost:8000`** et prêt à communiquer avec le Frontend Nuxt !

---

### Vérification Finale

Pour confirmer que le Backend est accessible :

1.  Ouvrez votre navigateur.
2.  Allez à l'adresse des outils de documentation automatiques de FastAPI : **`http://localhost:8000/docs`**.

Si vous voyez l'interface Swagger de FastAPI, votre Backend est parfaitement configuré. Vous pouvez alors lancer le Frontend avec `npm run dev`.
Démarrer le Frontend en second (Nuxt) via npm run dev.



Important : Si vous rencontrez des problèmes de compilation Nuxt, supprimez toujours les dossiers .nuxt, node_modules et package-lock.json avant de lancer un npm install pour garantir une reconstitution propre de l'environnement.