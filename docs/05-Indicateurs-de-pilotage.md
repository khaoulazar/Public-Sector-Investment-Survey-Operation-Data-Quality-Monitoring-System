## Phase 5 — Indicateurs de pilotage

Cette phase définit les mesures DAX calculées à partir de Vue_Qualite_Globale 
et des tables du schéma en étoile, pour alimenter le tableau de bord Power BI.

### EX-20 — Indicateurs d'avancement et de couverture terrain

- **Taux_Couverture** : proportion d'unités visitées sur le terrain par 
  rapport au total attendu.
- **Unites_Restantes** : nombre d'unités non encore couvertes.
- **Taux_Avancement_Par_Region** : taux de couverture décliné par région, 
  pour identifier les zones en retard.

### EX-21 — Indicateurs de qualité des données

- **Taux_Qualite_Parfaite** : proportion d'unités avec score_qualite_global = 0.
- **Score_Qualite_Moyen** : moyenne du score_qualite_global sur l'ensemble 
  des unités.
- **Taux_Anomalie_Couverture / Plages_Valeurs / Dates / Completude** : taux 
  d'anomalie par catégorie, pour prioriser les actions correctives.
- **Ecart_GPS_Moyen** : écart GPS moyen, indicateur de fiabilité de la 
  géolocalisation terrain.
- **Taux_Non_Reponse** : proportion de non-réponses enregistrées.

### EX-22 — Indicateurs de performance des agents et superviseurs

- **Tentatives_Moyennes_Agent** : nombre moyen de tentatives de collecte 
  par agent.
- **Erreurs_CAPI_Par_Agent** : taux d'erreurs CAPI par agent.
- **Taux_Reinterview** : proportion d'unités nécessitant une réinterview.

### EX-23 — Indicateurs de gestion des ressources

- **Total_Vehicules_Disponible** : Total des véhicules disponibles par région.
- **Cout_Carburant_Par_Unite** : coût moyen de carburant par unité enquêtée.

### EX-24 — Indicateurs temporels

- **Delai_Moyen_Controle** : délai moyen entre la collecte terrain et le 
  contrôle qualité.
- **Rythme_Collecte** : nombre d'unités collectées par semaine/mois.

**Source de données :** Vue_Qualite_Globale (grain : une ligne par unité 
enquêtée), complétée par Fait_Allocation_Ressources et Dim_Calendrier pour 
les indicateurs de ressources et temporels.
