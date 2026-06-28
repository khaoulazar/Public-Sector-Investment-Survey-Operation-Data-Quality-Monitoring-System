🇬🇧 [English](README.md) | 🇫🇷 **Français**

---

# Système de suivi et de contrôle qualité de la collecte des données de l'enquête sur l'investissement public

Système de suivi et de contrôle qualité de bout en bout pour une enquête administrative portant sur 2 068 unités — conception d'un schéma en étoile, détection de valeurs aberrantes (IQR/Z-score), indice composite de qualité, et tableau de bord Power BI.

## Présentation générale du projet

Ce projet consiste à concevoir et documenter un **système de suivi et de contrôle qualité d'une enquête administrative**, sur la base de données anonymisées, mais avec une méthodologie directement inspirée des pratiques professionnelles d'enquête statistique (suivi de terrain, contrôle de cohérence, indices de qualité). Le cas d'usage retenu est une enquête exhaustive sur les investissements des administrations publiques marocaines, couvrant 2 068 unités administratives (collectivités territoriales, établissements publics administratifs, sociétés de développement local) réparties sur 12 régions, mobilisant 48 enquêteurs et 12 superviseurs régionaux sur une période de terrain de 7 mois. L'objectif n'est pas de produire un simple tableau de bord, mais de reconstituer, de bout en bout, le rôle qu'occuperait un analyste de données chargé de concevoir ce système : du cadrage des besoins jusqu'à sa gouvernance documentaire, en passant par la modélisation des données, le traitement de la qualité statistique et la restitution décisionnelle.

La démarche est structurée en huit phases successives, chacune produisant un livrable concret qui conditionne les phases suivantes. 
<br>**Cadrage:** traduit les compétences à démontrer en exigences fonctionnelles précises et traçables.
<br>**Modélisation des données:** construit, à partir de ces exigences, un schéma en étoile normalisé compatible SQLite et Azure SQL Database.
<br>**Architecture technique:** définit l'infrastructure de collecte, de stockage et d'ingestion des données. 
<br>**ETL et contrôle qualité:** met en œuvre les règles de validation, la détection des valeurs aberrantes par IQR et Z-score, et le calcul de l'indice composite de qualité.
<br>**Indicateurs de pilotage:** formalise les KPIs de couverture, de vélocité et de qualité. 
<br>**Visualisation Power BI:** restitue l'ensemble sous forme de tableau de bord interactif à trois niveaux de lecture.
<br>**Automatisation et alertes:** introduit des mécanismes de notification et un score de risque par unité. 
<br>**Documentation et gouvernance:** consolide le dictionnaire de données, le journal des décisions méthodologiques et la documentation technique du projet.
