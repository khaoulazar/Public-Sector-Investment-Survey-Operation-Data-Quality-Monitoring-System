 Déploiement Power BI Service / Power BI Service Deployment

## 1. Architecture de la source de données / Data Source Architecture

Le modèle est connecté à une base **SQLite locale** (`data/enquete_administrative.db`)
via **ODBC** (DSN: `EnqueteDB`). Une actualisation automatique programmée depuis
Power BI Service vers une base SQLite locale nécessite une **passerelle de données
locale (On-premises Data Gateway)** installée sur la machine hébergeant la base —
sans cette passerelle, le jeu de données publié reste figé après l'import initial.

**Statut** : passerelle (`khaoula`) installée, active, et mappée à la source ODBC.
Actualisation confirmée fonctionnelle en Development.

The model connects to a **local SQLite database** (`data/enquete_administrative.db`)
via **ODBC** (DSN: `EnqueteDB`). Scheduled automatic refresh from Power BI Service
to a local SQLite database requires an **On-premises Data Gateway** installed on
the machine hosting the database — without it, the published dataset stays frozen
after the initial import.

**Status**: gateway (`khaoula`) installed, active, and mapped to the ODBC source.
Refresh confirmed functional in Development.

---

## 2. Dashboard de synthèse / Summary Dashboard

Un tableau de bord dédié a été construit en épinglant les visuels clés des 7 pages
du rapport (taux de réalisation, taux de couverture, score de qualité global) pour
une vue de suivi condensée.

A dedicated dashboard was built by pinning key visuals from the report's 7 pages
(completion rate, coverage rate, overall quality score) into a condensed
monitoring view.

### Comportement des slicers sur un dashboard / Slicer Behavior on Dashboards

**Point méthodologique important** : contrairement à un rapport, un dashboard
Power BI est une collection de **snapshots indépendants** — un slicer épinglé
devient une image figée de son état au moment de l'épinglage et ne filtre plus
dynamiquement les autres tuiles. Pour conserver une interactivité complète
(y compris les slicers synchronisés entre pages via **Sync slicers**), les tuiles
de dashboard pointent vers les **pages complètes du rapport** plutôt que vers des
visuels isolés.

**Important methodological point**: unlike a report, a Power BI dashboard is a
collection of **independent snapshots** — a pinned slicer becomes a frozen image
of its state at pinning time and no longer dynamically filters other tiles. To
preserve full interactivity (including slicers synchronized across pages via
**Sync slicers**), dashboard tiles link to **full report pages** rather than
isolated visuals.

---

## 3. Alertes de données / Data Alerts

### Contrainte technique identifiée / Identified Technical Constraint

Les alertes de données Power BI (**Manage alerts**) ne sont disponibles que sur
des tuiles de dashboard **numériques simples** : Carte (Card), Jauge (Gauge), ou
KPI. Elles ne sont pas proposées sur les graphiques multi-points, tableaux, ou
visuels cartographiques, une alerte nécessitant une valeur unique comparable à un
seuil.

Power BI data alerts (**Manage alerts**) are only available on **single-value**
dashboard tiles: Card, Gauge, or KPI. They are not offered on multi-point charts,
tables, or map visuals, since an alert requires a single value comparable to a
threshold.

**KPI retenus pour alertes / KPIs selected for alerts** :
- Taux de non-réponse / Non-response rate
- Taux de couverture / Coverage rate
- Taux de réalisation vs cible (`Target_réalisation` = 0.9) / Completion rate vs target

---

## 4. Pipeline de déploiement / Deployment Pipeline

Une pipeline de déploiement **Development → Test → Production** a été mise en
place pour cet espace de travail, isolant les modifications actives des versions
consultées par les décideurs.

A **Development → Test → Production** deployment pipeline was set up for this
workspace, isolating active changes from the versions viewed by decision-makers.

### Principe de fonctionnement / How It Works

- Les modifications se font exclusivement dans **Development** (republication
  depuis Power BI Desktop)
- **Test** sert de validation intermédiaire avant mise en production
- **Production** reste inchangée tant qu'un déploiement explicite **Test → Production**
  n'est pas déclenché — les décideurs ne voient les changements qu'à ce moment précis

- Changes are made exclusively in **Development** (republished from Power BI Desktop)
- **Test** serves as an intermediate validation stage before going live
- **Production** remains unchanged until an explicit **Test → Production** deployment
  is triggered — decision-makers only see changes at that exact point

### Journal de résolution d'incident / Incident Resolution Log

Lors du premier déploiement Development → Test, le semantic model n'a pas pu
s'actualiser en Test :

During the first Development → Test deployment, the semantic model failed to
refresh in Test:

| Étape / Step | Constat / Finding |
|---|---|
| Erreur observée / Error observed | `DM_GWPipeline_Gateway_InvalidConnectionCredentials` — `AccessUnauthorized` sur la source ODBC / on the ODBC source |
| Cause | Chaque espace de travail (Test) requiert ses **propres identifiants de connexion validés**, même si la passerelle physique est déjà installée et partagée / Each workspace (Test) requires its **own validated connection credentials**, even when the physical gateway is already installed and shared |
| Diagnostic | Passerelle correctement mappée à la source ODBC (`Gateway connections` confirmé) mais authentification manquante côté Test / Gateway correctly mapped to the ODBC source (`Gateway connections` confirmed) but authentication missing on the Test side |
| Résolution / Resolution | Ressaisie des identifiants via authentification Microsoft (Azure AD / MFA) dans les paramètres du dataset en Test / Re-entering credentials via Microsoft authentication (Azure AD / MFA) in the Test dataset settings |

Ce type d'incident est représentatif des défis courants de déploiement multi-
environnements sur Power BI Service, et sa résolution est documentée ici à des
fins de reproductibilité.

This type of incident is representative of common multi-environment deployment
challenges on Power BI Service, and its resolution is documented here for
reproducibility purposes.

### Distinction importante / Important Distinction

La pipeline de déploiement Power BI gère le **versionnement d'environnements**
(Dev/Test/Prod) — elle ne remplace pas un système de contrôle de version du code
source comme Git. Le fichier `.pbix` (binaire) reste versionné séparément dans ce
dépôt GitHub, indépendamment de l'état des étapes de la pipeline.

The Power BI deployment pipeline manages **environment versioning** (Dev/Test/Prod)
— it does not replace a source-control system like Git. The `.pbix` file (binary)
remains version-tracked separately in this GitHub repository, independent of the
pipeline stages' state.
