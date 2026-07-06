"""
generate_data.py
-----------------
Génère une base SQLite simulée pour le système de suivi et de contrôle
qualité d'une enquête administrative (2 068 unités, 12 régions).
"""

import sqlite3
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker("fr_FR")
random.seed(42)  # reproductibilité

DB_PATH = "data/enquete_administrative.db"

REGIONS_DATA = [
    {"nom": "Tanger-Tétouan-Al Hoceïma", "unites": 190, "enqueteurs": 4, "vehicules": 4, "tablettes": 5},
    {"nom": "L'Oriental",                 "unites": 164, "enqueteurs": 4, "vehicules": 4, "tablettes": 5},
    {"nom": "Fès-Meknès",                 "unites": 249, "enqueteurs": 6, "vehicules": 6, "tablettes": 7},
    {"nom": "Rabat-Salé-Kénitra",         "unites": 228, "enqueteurs": 5, "vehicules": 5, "tablettes": 6},
    {"nom": "Béni Mellal-Khénifra",       "unites": 175, "enqueteurs": 4, "vehicules": 4, "tablettes": 5},
    {"nom": "Casablanca-Settat",          "unites": 261, "enqueteurs": 6, "vehicules": 6, "tablettes": 7},
    {"nom": "Marrakech-Safi",             "unites": 299, "enqueteurs": 7, "vehicules": 7, "tablettes": 8},
    {"nom": "Drâa-Tafilalet",             "unites": 159, "enqueteurs": 4, "vehicules": 4, "tablettes": 5},
    {"nom": "Souss-Massa",                "unites": 217, "enqueteurs": 5, "vehicules": 5, "tablettes": 6},
    {"nom": "Guelmim-Oued Noun",          "unites": 67,  "enqueteurs": 1, "vehicules": 1, "tablettes": 1},
    {"nom": "Laâyoune-Sakia El Hamra",    "unites": 35,  "enqueteurs": 1, "vehicules": 1, "tablettes": 1},
    {"nom": "Eddakhla-Oued Eddahab",      "unites": 24,  "enqueteurs": 1, "vehicules": 1, "tablettes": 1},
]

assert sum(r["unites"] for r in REGIONS_DATA) == 2068
assert sum(r["enqueteurs"] for r in REGIONS_DATA) == 48
assert sum(r["vehicules"] for r in REGIONS_DATA) == 48
assert sum(r["tablettes"] for r in REGIONS_DATA) == 57

N_UNITES = 2068
N_REGIONS = len(REGIONS_DATA)
N_ENQUETEURS = sum(r["enqueteurs"] for r in REGIONS_DATA)
N_SUPERVISEURS = N_REGIONS

REPARTITION_TYPE_UNITE = {"CT": 0.70, "EPA": 0.20, "SDL": 0.10}
TAUX_NON_REPONSE = 0.10
TAUX_ANOMALIE_GPS = 0.08
TAUX_ANOMALIE_CAPI = 0.08

DATE_DEBUT = date(2025, 1, 1)
DATE_FIN = date(2025, 7, 1)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS Fait_Qualite;
    DROP TABLE IF EXISTS Fait_Suivi_Terrain;
    DROP TABLE IF EXISTS Fait_Allocation_Ressources;
    DROP TABLE IF EXISTS Dim_Unite_Enquetee;
    DROP TABLE IF EXISTS Dim_Enqueteur;
    DROP TABLE IF EXISTS Dim_Type_Unite;
    DROP TABLE IF EXISTS Dim_Region;
    DROP TABLE IF EXISTS Dim_Superviseur;
    DROP TABLE IF EXISTS Dim_Calendrier;

    CREATE TABLE Dim_Superviseur (
        superviseur_id   INTEGER PRIMARY KEY,
        email            TEXT,
        telephone        TEXT,
        date_embauche    TEXT,
        anciennete_annees INTEGER
    );

    CREATE TABLE Dim_Region (
        region_id          INTEGER PRIMARY KEY,
        zone_geographique   TEXT NOT NULL,
        population          INTEGER,
        superficie_km2      REAL,
        superviseur_id      INTEGER UNIQUE,
        FOREIGN KEY (superviseur_id) REFERENCES Dim_Superviseur(superviseur_id)
    );

    CREATE TABLE Dim_Type_Unite (
        type_unite_id     INTEGER PRIMARY KEY,
        description        TEXT NOT NULL,
        priorite_collecte  TEXT
    );

    CREATE TABLE Dim_Enqueteur (
        agent_id              INTEGER PRIMARY KEY,
        region_id              INTEGER NOT NULL,
        anciennete_annees     INTEGER,
        niveau_experience     TEXT,
        niveau_competence_it  TEXT,
        FOREIGN KEY (region_id) REFERENCES Dim_Region(region_id)
    );

    CREATE TABLE Dim_Unite_Enquetee (
        unite_id        INTEGER PRIMARY KEY,
        region_id        INTEGER NOT NULL,
        type_unite_id    INTEGER NOT NULL,
        agent_id         INTEGER NOT NULL,
        secteur_activite TEXT,
        milieu           TEXT,
        FOREIGN KEY (region_id) REFERENCES Dim_Region(region_id),
        FOREIGN KEY (type_unite_id) REFERENCES Dim_Type_Unite(type_unite_id),
        FOREIGN KEY (agent_id) REFERENCES Dim_Enqueteur(agent_id)
    );

    CREATE TABLE Dim_Calendrier (
        date_id           TEXT PRIMARY KEY,
        trimestre         TEXT,
        est_jour_ouvrable INTEGER
    );

    CREATE TABLE Fait_Allocation_Ressources (
        allocation_id       INTEGER PRIMARY KEY,
        region_id            INTEGER NOT NULL,
        nb_vehicules         INTEGER,
        nb_tablettes          INTEGER,
        budget_carburant_dh   REAL,
        FOREIGN KEY (region_id) REFERENCES Dim_Region(region_id)
    );

    CREATE TABLE Fait_Suivi_Terrain (
        suivi_id            INTEGER PRIMARY KEY,
        unite_id              INTEGER UNIQUE NOT NULL,
        date_id               TEXT NOT NULL,
        mode_collecte         TEXT,
        nb_tentatives         INTEGER,
        ecart_gps_metres      REAL,
        etat_questionnaire    TEXT,
        FOREIGN KEY (unite_id) REFERENCES Dim_Unite_Enquetee(unite_id),
        FOREIGN KEY (date_id) REFERENCES Dim_Calendrier(date_id)
    );

    CREATE TABLE Fait_Qualite (
        qualite_id            INTEGER PRIMARY KEY,
        unite_id                INTEGER UNIQUE NOT NULL,
        date_id                 TEXT NOT NULL,
        nb_corrections           INTEGER,
        nb_erreurs_capi          INTEGER,
        methode_imputation       TEXT,
        non_reponse              INTEGER,
        reinterview_requise      INTEGER,
        FOREIGN KEY (unite_id) REFERENCES Dim_Unite_Enquetee(unite_id),
        FOREIGN KEY (date_id) REFERENCES Dim_Calendrier(date_id)
    );
    """)
    conn.commit()


def generate_superviseurs(conn):
    rows = []
    for i in range(1, N_SUPERVISEURS + 1):
        rows.append((
            i,
            fake.email(),
            fake.phone_number(),
            fake.date_between(start_date=date(2015, 1, 1), end_date=date(2023, 1, 1)).isoformat(),
            random.randint(2, 15),
        ))
    conn.executemany("INSERT INTO Dim_Superviseur VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_regions(conn):
    rows = []
    for i, region in enumerate(REGIONS_DATA, start=1):
        rows.append((
            i,
            region["nom"],
            random.randint(50_000, 7_000_000),
            round(random.uniform(8_000, 100_000), 1),
            i,
        ))
    conn.executemany("INSERT INTO Dim_Region VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_types_unite(conn):
    rows = [
        (1, "Collectivité Territoriale (CT)", "Haute"),
        (2, "Établissement Public Administratif (EPA)", "Moyenne"),
        (3, "Société de Développement Local (SDL)", "Moyenne"),
    ]
    conn.executemany("INSERT INTO Dim_Type_Unite VALUES (?, ?, ?)", rows)
    conn.commit()


def generate_enqueteurs(conn):
    niveaux_exp = ["Débutant", "Intermédiaire", "Expérimenté"]
    niveaux_it = ["Faible", "Moyen", "Élevé"]
    rows = []
    agent_id = 1
    for region_id, region in enumerate(REGIONS_DATA, start=1):
        for _ in range(region["enqueteurs"]):
            rows.append((
                agent_id,
                region_id,
                random.randint(0, 12),
                random.choice(niveaux_exp),
                random.choice(niveaux_it),
            ))
            agent_id += 1
    conn.executemany("INSERT INTO Dim_Enqueteur VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_calendrier(conn):
    rows = []
    d = DATE_DEBUT
    while d <= DATE_FIN:
        trimestre = f"T{((d.month - 1) // 3) + 1}-{d.year}"
        est_ouvrable = 0 if d.weekday() >= 5 else 1
        rows.append((d.isoformat(), trimestre, est_ouvrable))
        d += timedelta(days=1)
    conn.executemany("INSERT INTO Dim_Calendrier VALUES (?, ?, ?)", rows)
    conn.commit()
    return [r[0] for r in rows]


def generate_unites_enquetees(conn):
    cur = conn.cursor()
    agents_par_region = {}
    for region_id, agent_id in cur.execute("SELECT region_id, agent_id FROM Dim_Enqueteur"):
        agents_par_region.setdefault(region_id, []).append(agent_id)

    region_sequence = []
    for region_id, region in enumerate(REGIONS_DATA, start=1):
        region_sequence.extend([region_id] * region["unites"])
    random.shuffle(region_sequence)
    assert len(region_sequence) == N_UNITES

    n_ct = round(N_UNITES * REPARTITION_TYPE_UNITE["CT"])
    n_epa = round(N_UNITES * REPARTITION_TYPE_UNITE["EPA"])
    n_sdl = N_UNITES - n_ct - n_epa
    types_sequence = [1] * n_ct + [2] * n_epa + [3] * n_sdl
    random.shuffle(types_sequence)

    secteurs = ["Administration générale", "Éducation", "Santé",
                "Infrastructures", "Développement local", "Finances"]
    milieux = ["Urbain", "Rural"]

    rows = []
    for unite_id in range(1, N_UNITES + 1):
        region_id = region_sequence[unite_id - 1]
        type_unite_id = types_sequence[unite_id - 1]
        agent_id = random.choice(agents_par_region[region_id])
        rows.append((
            unite_id, region_id, type_unite_id, agent_id,
            random.choice(secteurs), random.choice(milieux),
        ))
    conn.executemany("INSERT INTO Dim_Unite_Enquetee VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_allocation_ressources(conn):
    rows = []
    for region_id, region in enumerate(REGIONS_DATA, start=1):
        rows.append((
            region_id, region_id, region["vehicules"], region["tablettes"],
            round(random.uniform(15_000, 60_000), 2),
        ))
    conn.executemany("INSERT INTO Fait_Allocation_Ressources VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_suivi_terrain(conn, dates_disponibles):
    cur = conn.cursor()
    unite_ids = [r[0] for r in cur.execute("SELECT unite_id FROM Dim_Unite_Enquetee")]
    n_outliers_gps = round(len(unite_ids) * TAUX_ANOMALIE_GPS)
    outliers_gps = set(random.sample(unite_ids, n_outliers_gps))
    modes = ["CAPI tablette", "Papier"]
    etats = ["Complet", "Incomplet", "Refusé", "Non localisé","En cours"]
    distribution_tentatives = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5,6]

    rows = []
    for unite_id in unite_ids:
        date_id = random.choice(dates_disponibles)
        nb_tentatives = random.choice(distribution_tentatives)
        if unite_id in outliers_gps:
            ecart_gps = round(random.uniform(500, 3000), 1)
        else:
            ecart_gps = round(abs(random.gauss(15, 8)), 1)
        rows.append((
            unite_id, unite_id, date_id, random.choice(modes),
            nb_tentatives, ecart_gps, random.choice(etats),
        ))
    conn.executemany("INSERT INTO Fait_Suivi_Terrain VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()


def generate_qualite(conn, dates_disponibles):
    cur = conn.cursor()
    unite_ids = [r[0] for r in cur.execute("SELECT unite_id FROM Dim_Unite_Enquetee")]
    n_outliers_capi = round(len(unite_ids) * TAUX_ANOMALIE_CAPI)
    outliers_capi = set(random.sample(unite_ids, n_outliers_capi))
    n_non_reponse = round(len(unite_ids) * TAUX_NON_REPONSE)
    unites_non_reponse = set(random.sample(unite_ids, n_non_reponse))
    methodes_imputation = ["moyenne_strate", "mediane_strate", "valeur_precedente", "validation_terrain"]

    rows = []
    for unite_id in unite_ids:
        date_id = random.choice(dates_disponibles)
        non_reponse = 1 if unite_id in unites_non_reponse else 0
        if unite_id in outliers_capi:
            nb_erreurs_capi = random.randint(8, 20)
        else:
            nb_erreurs_capi = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
        nb_corrections = random.randint(1, 4) if nb_erreurs_capi >= 3 else random.choice([0, 0, 0, 1])
        methode_imputation = random.choice(methodes_imputation) if nb_corrections > 0 else "aucune"
        reinterview_requise = 1 if (non_reponse or nb_erreurs_capi >= 8) else 0
        rows.append((
            unite_id, unite_id, date_id, nb_corrections, nb_erreurs_capi,
            methode_imputation, non_reponse, reinterview_requise,
        ))
    conn.executemany("INSERT INTO Fait_Qualite VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()


def main():
    conn = get_connection()
    print("Création du schéma...")
    create_schema(conn)
    print("Génération des dimensions...")
    generate_superviseurs(conn)
    generate_regions(conn)
    generate_types_unite(conn)
    generate_enqueteurs(conn)
    dates_disponibles = generate_calendrier(conn)
    generate_unites_enquetees(conn)
    print("Génération des faits...")
    generate_allocation_ressources(conn)
    generate_suivi_terrain(conn, dates_disponibles)
    generate_qualite(conn, dates_disponibles)
    conn.close()
    print(f"Base générée avec succès : {DB_PATH}")
    print(f"  - {N_UNITES} unités enquêtées (effectifs réels par région)")
    print(f"  - {N_REGIONS} régions / {N_SUPERVISEURS} superviseurs (1:1)")
    print(f"  - {N_ENQUETEURS} enquêteurs (effectifs réels par région)")


if __name__ == "__main__":
    main()