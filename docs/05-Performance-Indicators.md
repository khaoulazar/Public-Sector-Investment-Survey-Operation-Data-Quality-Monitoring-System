## Phase 5 — Performance Indicators

This phase defines the DAX measures calculated from Vue_Qualite_Globale and 
the star schema tables, feeding the Power BI dashboard.

### REQ-20 — Progress and Field Coverage Indicators

- **Taux_Couverture**: proportion of units visited in the field relative 
  to the total expected.
- **Unites_Restantes**: number of units not yet covered.
- **Taux_Avancement_Par_Region**: coverage rate broken down by region, to 
  identify lagging areas.

### REQ-21 — Data Quality Indicators

- **Taux_Qualite_Parfaite**: proportion of units with score_qualite_global = 0.
- **Score_Qualite_Moyen**: average score_qualite_global across all units.
- **Taux_Anomalie_Couverture / Plages_Valeurs / Dates / Completude**: 
  anomaly rate per category, to prioritize corrective actions.
- **Ecart_GPS_Moyen**: average GPS deviation, indicator of field 
  geolocation reliability.
- **Taux_Non_Reponse**: proportion of recorded non-responses.

### REQ-22 — Surveyor and Supervisor Performance Indicators

- **Tentatives_Moyennes_Agent**: average number of collection attempts 
  per surveyor.
- **Erreurs_CAPI_Par_Agent**: CAPI error rate per surveyor.
- **Taux_Reinterview**: proportion of units requiring re-interview.

### REQ-23 — Resource Management Indicators

- **Total_Vehicules**: Total of vehicules available by region.
- **Cout_Carburant_Par_Unite**: average fuel cost per surveyed unit.

### REQ-24 — Time-Based Indicators

- **Delai_Moyen_Controle**: average delay between field collection and 
  quality control.
- **Rythme_Collecte**: number of units collected per week/month.

**Data source:** Vue_Qualite_Globale (grain: one row per surveyed unit), 
supplemented by Fait_Allocation_Ressources and Dim_Calendrier for resource 
and time-based indicators.
