# Awalé AI

## Table of Contents
<details>
  <summary>Contents</summary>
  1. [Prérequis](#prérequis)
  2. [Installation et Lancement](#installation-et-lancement)
  3. [Architecture du Projet](#architecture-du-projet)
  4. [Description des agents](#description-des-agents-bots)
</details>

Application Python permettant de jouer à l'Awalé via une interface graphique (Pygame) ou de lancer des tournois automatisés afin de benchmarquer la puissance de différentes Intelligences Artificielles : un algorithme heuristique déterministe (MinMax) et une recherche arborescente de Monte Carlo (MCTS).

## Prérequis
- Python 3.10 ou supérieur
- Pygame (uniquement pour l'interface graphique)

## Installation et Lancement

1. Cloner ou dézipper le projet.
2. Installer Pygame (si vous souhaitez utiliser l'interface graphique) :
    ```bash
    pip install pygame
    ```
    ou

    ```bash
    py -m pip install pygame
    ```

3. Lancer le jeu avec l'interface graphique : 
    ```bash
    python main.py
    ```
    ou
    ```bash
    py main.py
    ```

4. Lancer les concours:
    ```bash
    python concours.py
    ```
    ou 

    ```bash
    py concours.py
    ```

## Architecture du projet

* `awale.py` : C'est le moteur du jeu. Il gère les règles brutes, distribue les graines, calcule les scores et vérifie si un coup est valide ou si un joueur affame l'autre.
* `main.py` : Le fichier principal pour la version graphique. C'est la boucle de jeu qui capte tes clics et appelle les bots quand c'est leur tour.
* `gui.py` : Tout le visuel. Le dessin du plateau, le menu pour choisir le mode au début et la fenêtre de fin de match.
* `concours.py` : Le gestionnaire de tournoi automatique. Idéal pour faire s'affronter deux types de bots sur 100 parties. Il alterne automatiquement le joueur qui commence pour que les stats soient justes.
* `human.py` : Fait juste le pont entre l'endroit où tu cliques sur l'écran et la case que ça doit jouer.

## Description des agents (Bots)

### 1. StupidBot
Agent de référence basé sur le hasard. Il récupère la liste des coups valides fournie par le moteur à chaque tour et en sélectionne un de manière uniforme. Permet de valider la progression des autres algorithmes.

### 2. GloutonBot
Approche heuristique monocoup à court terme. Cet agent simule l'ensemble des coups légaux pour le tour courant et sélectionne immédiatement celui qui maximise le nombre de graines capturées chez l'adversaire, sans anticiper les tours suivants.

### 3. MinMax
Algorithme d'anticipation adverse basé sur un arbre de recherche avec **élagage Alpha-Beta** afin de restreindre l'espace d'exploration. Il évalue la situation sur plusieurs coups d'avance (profondeur paramétrable) en maximisant son différentiel de points.

### 4. MCTS (Monte Carlo Tree Search)
Recherche arborescente probabiliste guidée par la formule UCB1 pour l'équilibre entre exploration et exploitation. Le processus s'appuie sur la classe `Sommet` (optimisée pour minimiser l'usage mémoire) et se déroule en quatre phases : sélection, développement, simulation (déroulement de fins de parties aléatoires) et rétropropagation des scores de victoire.