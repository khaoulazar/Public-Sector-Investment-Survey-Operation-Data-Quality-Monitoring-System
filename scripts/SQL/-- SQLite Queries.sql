-- SQLite
SELECT name
FROM sqlite_master
WHERE type = 'table';
SELECT sql FROM sqlite_master WHERE type='table';

-- View the table 'fait_Qualite'
SELECT * FROM Fait_Qualite;

--Create 5 Quality control views
-- But first lets check the nbr of non reponse greater than 0 with 'aucune' in methode imputation

-- J'ai eu avant la correction 136 lignes
SELECT COUNT(*) AS nb_lignes_a_corriger 
FROM Fait_Qualite
WHERE non_reponse > 0 AND methode_imputation = 'aucune';

--Correct the data in the table Fait_Qualite by updating the methode_imputation
UPDATE Fait_Qualite
SET methode_imputation = CASE
    WHEN non_reponse = 0 THEN 'aucune'
    WHEN non_reponse > 0 AND methode_imputation = 'aucune' THEN
        CASE ABS(RANDOM() % 4)
            WHEN 0 THEN 'moyenne_strate'
            WHEN 1 THEN 'mediane_strate'
            WHEN 2 THEN 'valeur_precedente'
            WHEN 3 THEN 'validation_terrain'
        END
    ELSE methode_imputation
END;

-- Check the result of the update
  SELECT non_reponse, methode_imputation
  FROM Fait_Qualite
  WHERE non_reponse>0;

--1 Imputation coherence validation view
-- since its already corrected we add to this view for future validation of the coherence of the imputation method
DROP VIEW IF EXISTS Vue_Coherence_Imputation_Validee;
CREATE VIEW Vue_Coherence_Imputation_Validee AS
SELECT
    qualite_id,
    unite_id,
    date_id,
    nb_corrections,
   nb_erreurs_capi,
   non_reponse,
 methode_imputation,
   reinterview_requise
   FROM Fait_Qualite
   WHERE (non_reponse=0 AND methode_imputation='aucune')
   OR (non_reponse>0 AND methode_imputation != 'aucune');

--Verifier les modalités de methode_imputation
SELECT DISTINCT methode_imputation FROM Fait_Qualite;

--Voir la vue de coherence d'imputation
SELECT *FROM Vue_Coherence_Imputation_Validee;

--Verify how many non reponse are in the table 
SELECT 
    non_reponse,
    COUNT(*) AS nb,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Fait_Qualite),2)AS pourcentage
FROM Fait_Qualite
GROUP BY non_reponse;

--2 Completion validation view for the Fait_suivi_terrain table 
DROP VIEW IF EXISTS Vue_Completude_Validee;
CREATE VIEW Vue_Completude_Validee AS
SELECT
    suivi_id,
    unite_id,
    date_id,
    CASE
        WHEN mode_collecte IS NULL OR TRIM(mode_collecte) = '' THEN 'non_renseigné'
        ELSE mode_collecte
    END AS mode_collecte,
    nb_tentatives,
    ecart_gps_metres,
    CASE
        WHEN etat_questionnaire IS NULL OR TRIM(etat_questionnaire) = '' THEN 'non_renseigné'
        ELSE etat_questionnaire
    END AS etat_questionnaire
FROM Fait_Suivi_Terrain;

--Afficher la vue de completude
SELECT * FROM Vue_Completude_Validee;

--Verifier les modalités de etat_questionnaire
SELECT DISTINCT etat_questionnaire
FROM Vue_Completude_Validee;

--Verifier le nombre d'unité par etat_questionnaire
SELECT etat_questionnaire,COUNT(*) AS nb_unités 
FROM Vue_Completude_Validee
GROUP BY etat_questionnaire;
--Verifier le nombre total des unités
SELECT COUNT(*) AS nb_unites 
FROM Vue_Completude_Validee;

--TEST
SELECT * FROM Dim_Unite_Enquetee;
SELECT DISTINCT unite_id FROM Fait_Suivi_Terrain;

--3 Create the coverage view 
--Detect the surveyed units in Dim_unites_enquetee that have no matching row at all in Fait_suivi_terrain
DROP VIEW IF EXISTS Vue_Couverture_Validee;
CREATE VIEW Vue_Couverture_Validee AS
SELECT
    ue.unite_id,
    ue.region_id,
    ue.type_unite_id,
    ue.agent_id,
    ue.secteur_activite,
    ue.milieu,
    'sans suivi terrain' AS anomalie
FROM Dim_Unite_Enquetee ue
LEFT JOIN Fait_Suivi_Terrain ft ON ue.unite_id = ft.unite_id -- to match them they should have same data type
WHERE ft.unite_id IS NULL;

--Afficher la vue de couverture
SELECT * FROM Vue_Couverture_Validee;

-- pas de resultas de la vue 
--test 
SELECT COUNT(*) AS total_unites FROM Dim_Unite_Enquetee;
SELECT COUNT(DISTINCT unite_id) AS total_suivi FROM Fait_Suivi_Terrain;
 -- vue est correcte, Les chiffres égaux, ça veut dire qu'il y a exactement autant d'unités enquêtées que d'unités suivies sur le terrain 

 --4 Vue plage_valeurs_validee
--4 Create the value ranges view
--Include analysis-ready columns for all units, flag ALL out-of-range values without dropping them
DROP VIEW IF EXISTS Vue_Plages_Valeurs_Validee;
CREATE VIEW Vue_Plages_Valeurs_Validee AS
SELECT
    ue.unite_id,
    ue.region_id,
    ue.type_unite_id,
    ue.agent_id,
    ue.secteur_activite,
    ue.milieu,
    ft.date_id,
    CASE WHEN ft.ecart_gps_metres < 0 THEN NULL ELSE ft.ecart_gps_metres END AS ecart_gps_metres,
    ft.nb_tentatives,
    fq.nb_corrections,
    fq.nb_erreurs_capi,
    TRIM(
        (CASE WHEN ft.ecart_gps_metres < 0 THEN 'ecart_gps_metres negatif; ' ELSE NULL END) ||
        (CASE WHEN ft.ecart_gps_metres > 700 THEN 'ecart_gps_metres hors plage (>700m); ' ELSE NULL END) ||
        (CASE WHEN ft.nb_tentatives > 10 THEN 'nb_tentatives hors plage (>10); ' ELSE NULL END) ||
        (CASE WHEN fq.nb_corrections > 10 THEN 'nb_corrections hors plage (>10); ' ELSE NULL END) ||
        (CASE WHEN fq.nb_erreurs_capi > 10 THEN 'nb_erreurs_capi hors plage (>10); ' ELSE NULL END)
    ) AS anomalie
FROM Dim_Unite_Enquetee ue
LEFT JOIN Fait_Suivi_Terrain ft ON ue.unite_id = ft.unite_id
LEFT JOIN Fait_Qualite fq ON ue.unite_id = fq.unite_id;

--Afficher la vue des plages de valeurs
SELECT * FROM Vue_Plages_Valeurs_Validee;
-- VERIFIER LES ANOMALIES
SELECT anomalie FROM Vue_Plages_Valeurs_Validee 
WHERE anomalie IS NOT NULL;

--5 Vue date_coherence_view
-- verifier la forme de dates si cest comparable format text 
SELECT date_id FROM Dim_Calendrier LIMIT 5; 
-- cest la bonne format 

--Check date_id from both fact tables against the survey period, and against each other for the same unit
DROP VIEW IF EXISTS Vue_Coherence_Dates_Validee;
CREATE VIEW Vue_Coherence_Dates_Validee AS
SELECT
    ue.unite_id,
    ue.region_id,
    ue.type_unite_id,
    ue.agent_id,
    ue.secteur_activite,
    ue.milieu,
    ft.date_id AS date_suivi_terrain,
    fq.date_id AS date_qualite,
    TRIM(
        (CASE WHEN ft.date_id < '2025-01-01' OR ft.date_id > '2025-07-01' THEN 'date_suivi_terrain hors periode collecte; ' ELSE NULL END) ||
        (CASE WHEN fq.date_id < '2025-01-01' OR fq.date_id > '2025-07-01' THEN 'date_qualite hors periode collecte; ' ELSE NULL END) ||
        (CASE WHEN ft.date_id IS NOT NULL AND fq.date_id IS NOT NULL AND ft.date_id != fq.date_id THEN 'date_suivi_terrain et date_qualite incoherentes; ' ELSE NULL END)
    ) AS anomalie
FROM Dim_Unite_Enquetee ue
LEFT JOIN Fait_Suivi_Terrain ft ON ue.unite_id = ft.unite_id
LEFT JOIN Fait_Qualite fq ON ue.unite_id = fq.unite_id;

--Afficher la vue de coherence des dates
SELECT * FROM Vue_Coherence_Dates_Validee;
-- VERIFIER LES ANOMALIES
SELECT anomalie FROM Vue_Coherence_Dates_Validee 
WHERE anomalie IS NOT NULL;

--THIS PART IS VERY IMPORTANT FOR the LOAD STEP OF ETL WHICH IS PHASE 4 
--LOAD THE VIEWS IN TABLE_QUALITE_GLOBALE 

--Load: Table de synthèse qualité globale, une ligne par unité enquêtée
DROP TABLE IF EXISTS Table_Qualite_Globale;
CREATE TABLE Table_Qualite_Globale AS
SELECT
    ue.unite_id,
    ue.region_id,
    ue.type_unite_id,
    ue.agent_id,
    ue.secteur_activite,
    ue.milieu,
    vp.ecart_gps_metres,
    vp.nb_tentatives,
    vp.nb_corrections,
    vp.nb_erreurs_capi,
    vd.date_suivi_terrain,
    vd.date_qualite,
    CASE WHEN vc.unite_id IS NOT NULL THEN 'unité sans suivi terrain' ELSE NULL END AS anomalie_couverture,
    CASE WHEN vp.anomalie = NULL THEN 'NNULL' ELSE vp.anomalie END AS anomalie_plages_valeurs,
    CASE WHEN vd.anomalie = NULL THEN 'NNULL' ELSE vd.anomalie END AS anomalie_dates,
    CASE WHEN vco.mode_collecte = 'non_renseigné' OR vco.etat_questionnaire = 'non_renseigné'
         THEN 'donnee(s) manquante(s) (mode_collecte/etat_questionnaire)' ELSE NULL END AS anomalie_completude,
    (
        (CASE WHEN vc.unite_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN vp.anomalie IS NOT NULL AND vp.anomalie != NULL THEN 1 ELSE 0 END) +
        (CASE WHEN vd.anomalie IS NOT NULL AND vd.anomalie != NULL THEN 1 ELSE 0 END) +
        (CASE WHEN vco.mode_collecte = 'non_renseigné' OR vco.etat_questionnaire = 'non_renseigné' THEN 1 ELSE 0 END)
    ) AS score_qualite_global
FROM Dim_Unite_Enquetee ue
LEFT JOIN Vue_Couverture_Validee vc ON ue.unite_id = vc.unite_id
LEFT JOIN Vue_Plages_Valeurs_Validee vp ON ue.unite_id = vp.unite_id
LEFT JOIN Vue_Coherence_Dates_Validee vd ON ue.unite_id = vd.unite_id
LEFT JOIN Vue_Completude_Validee vco ON ue.unite_id = vco.unite_id;

--Vérifier le résultat
SELECT * FROM Table_Qualite_Globale LIMIT 10;

--Vérifier la distribution du score
SELECT score_qualite_global, COUNT(*) AS nb_unites
FROM Table_Qualite_Globale
GROUP BY score_qualite_global;

--apres avoir verifier la table qualite globale, date qualité doit etre grande que date suivi terrain
-- afficher les lignes ou on a cette INCOHERENCE
SELECT ft.unite_id, ft.date_id AS date_suivi_terrain, fq.date_id AS date_qualite
FROM Fait_Suivi_Terrain ft
JOIN Fait_Qualite fq ON ft.unite_id = fq.unite_id
WHERE fq.date_id <= ft.date_id;

-- UTILISER LANCIENNE TABLE POUR CALCULER LE NBR DE LIGNES AVEC INCOHERENCE DE DATE
WITH Incoherence_dates AS (
    SELECT ft.unite_id, ft.date_id AS date_suivi_terrain, fq.date_id AS date_qualite
FROM Fait_Suivi_Terrain ft
JOIN Fait_Qualite fq ON ft.unite_id = fq.unite_id
WHERE fq.date_id <= ft.date_id   
)
SELECT COUNT(*) AS nb_lignes_incoherentes   
FROM Incoherence_dates;

-- Corriger les incohérences de date dans la table Fait_Qualite en mettant à jour la date_id pour qu'elle soit supérieure à la date de suivi terrain
-- Uniquement pr les lignes incoherentes, date_qualite=date_suivi + 1 
UPDATE Fait_Qualite
SET date_id = (SELECT date(ft.date_id,'+1 day')
FROM Fait_suivi_Terrain ft 
WHERE ft.unite_id=Fait_Qualite.unite_id)
WHERE unite_id IN (
    SELECT ft.unite_id
    FROM Fait_Suivi_Terrain ft
    JOIN Fait_Qualite fq ON ft.unite_id = fq.unite_id
    WHERE fq.date_id <= ft.date_id
);
-- VERIFIER LA CORRECTION
SELECT COUNT(*) AS nb_lignes_encore_incoherentes
FROM Fait_Suivi_Terrain ft
JOIN Fait_Qualite fq ON ft.unite_id = fq.unite_id
WHERE fq.date_id <= ft.date_id;








