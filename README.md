# 🌐 Projet ALMF51 : Suite Algorithmique de Graphes

## 📖 Description

Ce projet est une application web interactive développée dans le cadre du module **ALMF51 (Algorithmique des graphes)** à l'EFREI Paris.

Elle permet de visualiser, manipuler et comprendre le fonctionnement de **8 algorithmes fondamentaux** de la théorie des graphes appliqués à un réseau routier (carte de France) ou à des données personnalisées. L'application offre une visualisation graphique dynamique ainsi que des rapports textuels détaillés pour chaque exécution.

---

## ✨ Fonctionnalités Principales

* **8 Algorithmes Implémentés :**
* 🏁 **Parcours :** BFS (Largeur), DFS (Profondeur).
* 🛣️ **Plus Court Chemin :** Dijkstra, Bellman-Ford (détection cycles négatifs), Floyd-Warshall.
* 🌳 **Arbre Couvrant Minimal :** Prim, Kruskal.
* 📅 **Ordonnancement :** Méthode PERT (Chemin critique).


* **Visualisation Interactive :** Manipulation des nœuds, zoom, et **surbrillance des résultats** en temps réel.
* **Données Personnalisables :**
* Utilisation du graphe par défaut (10 villes de France).
* Saisie de votre propre **Matrice d'Adjacence**.
* Saisie de vos propres tâches pour le **PERT (JSON)**.


* **Interface Moderne :** Design "Glassmorphism" avec mode sombre et onglets ergonomiques.

---

## 🎨 Légende Visuelle (Code Couleur)

Pour faciliter la lecture des résultats sur le graphe, nous utilisons un code couleur spécifique selon le type d'algorithme exécuté :

| Type de Résultat | Couleur | Algorithmes concernés | Signification |
| --- | --- | --- | --- |
| **Chemin & Séquence** | 🟡 **Jaune / Orange** | `Dijkstra`, `Bellman-Ford`, `PERT` | Représente un itinéraire précis d'un point A à un point B, ou une suite chronologique de tâches (chemin critique). C'est une **séquence ordonnée**. |
| **Structure & Arbre** | 🔴 **Rose Néon / Rouge** | `BFS`, `DFS`, `Prim`, `Kruskal` | Représente une structure globale : un **arbre couvrant** ou un **arbre de découverte**. Il n'y a pas de notion de "début/fin" linéaire, mais de connexion d'ensemble. |
| **Nœuds Actifs** | 🟢 **Vert Néon** | *Tous* | Indique les villes/tâches visitées ou sélectionnées par l'algorithme. |

---

## 🛠️ Spécifications Techniques

* **Backend :** Python 3, Framework Django.
* **Frontend :** HTML5, CSS3, JavaScript (Vanilla).
* **Visualisation :** Librairie [Vis.js Network](https://visjs.github.io/vis-network/docs/network/).
* **Calcul Scientifique :** Utilisation native de Python (listes, dictionnaires) et `heapq` pour les files de priorité.

---

## 🚀 Installation et Démarrage

Suivez ces étapes pour lancer le projet sur votre machine locale.

### Prérequis

* Python (version 3.8 ou supérieure) installé.
* pip (gestionnaire de paquets Python).

### 1. Cloner ou télécharger le projet

```bash
git clone https://github.com/votre-repo/projet-graphe.git
cd projet-graphe

```

### 2. Créer un environnement virtuel (Recommandé)

Cela évite les conflits avec vos autres projets Python.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Installer les dépendances

Installez Django et les bibliothèques requises.

```bash
pip install django numpy

```

### 4. Lancer les migrations (Base de données)

Même si le projet utilise peu la BDD, Django en a besoin pour sa configuration initiale.

```bash
python manage.py migrate

```

### 5. Démarrer le serveur

```bash
python manage.py runserver

```

### 6. Accéder à l'application

Ouvrez votre navigateur et allez à l'adresse :
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 💡 Guide d'Utilisation

### Utiliser les données par défaut

1. Laissez le bouton **"Défaut"** activé.
2. Choisissez un algorithme dans le menu déroulant (ex: *Dijkstra*).
3. Remplissez les champs requis (ex: *Départ: Paris*, *Arrivée: Lyon*).
4. Cliquez sur **"LANCER L'ANALYSE"**.
5. Naviguez entre l'onglet **"Visualisation"** (Graphe) et **"Résultats Détaillés"** (Texte).

### Utiliser vos propres données (Matrice)

1. Cliquez sur le bouton **"Custom"**.
2. Entrez la liste des villes : `A, B, C`
3. Entrez la matrice d'adjacence (liste de listes Python) :
* Utilisez `0` pour la diagonale.
* Utilisez `inf` pour l'absence de liaison.
* *Exemple :* `[[0, 10, inf], [10, 0, 5], [inf, 5, 0]]`


4. Lancez l'algorithme de votre choix.

### Utiliser vos propres données (PERT)

1. Sélectionnez l'algorithme **PERT**.
2. Activez le mode **"Custom"**.
3. Une zone de texte JSON apparaît. Entrez vos tâches sous ce format :

```json
{
    "A": {"duree": 3, "predecesseurs": []},
    "B": {"duree": 4, "predecesseurs": ["A"]},
    "C": {"duree": 2, "predecesseurs": ["B"]}
}

```

---

## 📂 Structure du Projet

Voici comment s'organise le code source pour faciliter la correction :

```text
graphe_project/
│
├── manage.py               # Gestionnaire de commandes Django
├── graphe_project/         # Configuration globale (urls, settings)
│
└── core/                   # Cœur de l'application
    ├── views.py            # Contrôleur principal (API et gestion des erreurs)
    ├── templates/
    │   └── index.html      # Interface unique (HTML/JS/Vis.js)
    │
    ├── # --- ALGORITHMES ---
    ├── dijkstra.py         # Implémentation Dijkstra
    ├── bellmanford.py      # Implémentation Bellman-Ford
    ├── Floyd_Warshall.py   # Implémentation Floyd-Warshall
    ├── bfs_dfs.py          # Implémentation Parcours (BFS/DFS)
    ├── prim_kruskal.py     # Implémentation Arbres (Prim/Kruskal)
    ├── MethodePert.py      # Implémentation PERT
    │
    └── Matrice.py          # Données par défaut (Carte de France)

```

---

## 👥 Auteurs

* **[Votre Nom]** - *Développeur Fullstack (Django/JS)*
* **[Nom Coéquipière]** - *Algorithmique & Recherche*

---

*Projet réalisé pour l'école d'ingénieurs EFREI Paris - 2026*