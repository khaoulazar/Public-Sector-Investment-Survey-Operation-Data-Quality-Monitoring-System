# Phase 3 — Architecture technique et infrastructure

## 3.1 Objectif de la phase

Définir l'environnement technique sur lequel le schéma de la Phase 2 sera implémenté : moteur de base de données, outil de génération des données simulées, et chaîne d'analyse — en garantissant une portabilité réelle vers Azure SQL Database (EX-01, EX-12), pas seulement déclarative.

## 3.2 Composants retenus

| Composant | Outil retenu | Justification |
|---|---|---|
| Base de données (portfolio) | SQLite | Aucune installation serveur, fichier `.db` versionnable dans le repo, suffisant pour 2 068 lignes |
| Compatibilité cible | Azure SQL Database | Exigée par EX-12 — implique d'éviter les fonctions strictement propriétaires à SQLite dans les requêtes destinées à être réutilisées |
| Génération des données simulées | Python (`faker`, `random`, `numpy`) | Contrôle fin des distributions et des taux d'anomalies/non-réponse |
| Chargement des données dans SQLite | Python (`sqlite3` natif) | Un script `generate_data.py` peuple les 9 tables dans l'ordre des dépendances (dimensions avant faits) |
| Analyse (IQR/Z-score, indice composite) | SQL + Python (`pandas`, `scipy`) | SQL pour les agrégats simples, Python pour les calculs statistiques (EX-04, EX-07) |
| Restitution | Power BI Desktop | Connexion directe au fichier SQLite (ou export CSV intermédiaire) |

## 3.3 Décisions techniques actées

| Décision | Choix retenu | Raison |
|---|---|---|
| Ordre de génération des données | Dimensions d'abord (région → superviseur → type unité → enquêteur → unité enquêtée → calendrier), puis faits | Respect des contraintes FK |
| Respect du 1:1 à la génération | Une seule ligne par `unite_id` dans `Fait_Suivi_Terrain` et `Fait_Qualite` | Cohérence avec la contrainte UNIQUE actée en Phase 2 |
| Taux d'anomalie simulé | **~10–15%** des unités avec `ecart_gps_metres` aberrant ou `nb_erreurs_capi` élevé | Modéré : suffisant pour démontrer la détection IQR/Z-score (EX-04) sans fausser excessivement les KPIs globaux |
| Taux de non-réponse simulé | **~10%** des unités avec `non_reponse` = Oui | Réaliste pour une enquête administrative obligatoire, sans dominer les indicateurs |
| Emplacement du fichier base | `data/enquete_administrative.db` à la racine du repo | Cohérent avec la structure GitHub déjà posée |
| Emplacement du script de génération | `scripts/generate_data.py` | Séparation claire code / données |

## 3.4 Livrable de fin de phase

Spécification technique de l'environnement (SQLite + Python + Power BI), paramètres de simulation actés (10–15% anomalies, 10% non-réponse), structure de dossiers du repo confirmée (`data/`, `scripts/`).
