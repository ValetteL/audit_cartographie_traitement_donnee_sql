"""Configure Metabase entièrement par son API REST, sans passer par l'assistant
web : compte admin, connexion PostgreSQL, et le dashboard métier (6 graphiques
sur diagnostic_dpe_flux). Contrairement à Grafana, Metabase n'a pas de mécanisme
de provisioning par fichiers déposés au démarrage — ce script joue ce rôle.

Idempotent seulement au sens où il ne casse rien s'il est relancé sur une
instance déjà configurée (le POST /api/setup échoue silencieusement, ignoré) ;
il ne mettra pas à jour un dashboard déjà créé. À lancer une fois, après le
premier `docker compose up -d` (le volume metabase_data fait persister le
résultat pour les démarrages suivants).

Usage : python bootstrap.py
"""
import json
import os
import time
import urllib.error
import urllib.request

METABASE_URL = os.environ.get("METABASE_URL", "http://metabase:3000")
ADMIN_EMAIL = "admin@tp2.local"
ADMIN_PASSWORD = "MetabaseTp2!2026"
PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD = "db", 5432, "audit_immo_energie_44", "postgres", "postgres"

DASHBOARD_NAME = "TP2 — Dataviz métier (DPE & marché immobilier)"

CARDS = [
    (
        "Répartition des étiquettes DPE reçues",
        "SELECT etiquette_dpe AS \"Étiquette\", COUNT(*) AS \"Nombre\" "
        "FROM diagnostic_dpe_flux GROUP BY etiquette_dpe ORDER BY etiquette_dpe",
        "pie",
    ),
    (
        "Origine des DPE reçus (backfill vs live)",
        "SELECT source_flux AS \"Origine\", COUNT(*) AS \"Nombre\" "
        "FROM diagnostic_dpe_flux GROUP BY source_flux",
        "pie",
    ),
    (
        "Volume de DPE traités dans le temps",
        "SELECT date_trunc('minute', traite_le) AS \"Heure\", COUNT(*) AS \"Nombre\" "
        "FROM diagnostic_dpe_flux GROUP BY 1 ORDER BY 1",
        "line",
    ),
    (
        "10 communes les plus chères (prix moyen €/m²)",
        "SELECT c.nom_commune AS \"Commune\", MAX(f.prix_m2_commune_reference) AS \"Prix moyen\" "
        "FROM diagnostic_dpe_flux f JOIN commune c ON c.code_insee = f.code_insee "
        "WHERE f.prix_m2_commune_reference IS NOT NULL "
        "GROUP BY c.nom_commune ORDER BY 2 DESC LIMIT 10",
        "bar",
    ),
    (
        "Part de logements F-G par tranche de prix communal",
        "SELECT CASE "
        "WHEN prix_m2_commune_reference < 2000 THEN '< 2000' "
        "WHEN prix_m2_commune_reference < 3000 THEN '2000-3000' "
        "WHEN prix_m2_commune_reference < 4000 THEN '3000-4000' "
        "ELSE '>= 4000' END AS \"Tranche €/m²\", "
        "100.0 * SUM(CASE WHEN etiquette_dpe IN ('F','G') THEN 1 ELSE 0 END) / COUNT(*) AS \"% F-G\" "
        "FROM diagnostic_dpe_flux WHERE prix_m2_commune_reference IS NOT NULL GROUP BY 1 ORDER BY 1",
        "bar",
    ),
    (
        "Derniers DPE reçus",
        "SELECT f.numero_dpe, c.nom_commune, f.etiquette_dpe, f.etiquette_ges, "
        "f.surface_habitable_logement, f.prix_m2_commune_reference, f.source_flux, f.traite_le "
        "FROM diagnostic_dpe_flux f JOIN commune c ON c.code_insee = f.code_insee "
        "ORDER BY f.traite_le DESC LIMIT 50",
        "table",
    ),
]

LAYOUT = [
    (0, 0, 6, 8), (0, 6, 6, 8), (0, 12, 6, 8),
    (8, 0, 9, 8), (8, 9, 9, 8),
    (16, 0, 18, 8),
]


def call(method, path, session=None, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if session:
        headers["X-Metabase-Session"] = session
    req = urllib.request.Request(METABASE_URL + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def wait_ready():
    for _ in range(60):
        try:
            if call("GET", "/api/health").get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Metabase indisponible")


def main():
    wait_ready()
    props = call("GET", "/api/session/properties")

    if props.get("has-user-setup"):
        print("Metabase déjà configuré (compte admin existant) — rien à faire côté setup.")
        print(f"Identifiants attendus : {ADMIN_EMAIL} / {ADMIN_PASSWORD} (si générés par ce script précédemment).")
        try:
            session = call("POST", "/api/session", body={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})["id"]
        except urllib.error.HTTPError:
            print("Connexion impossible avec ces identifiants : compte admin créé autrement (assistant web), "
                  "ou déjà différent. Rien de plus à automatiser depuis ce script.")
            return
    else:
        token = props["setup-token"]
        setup = call("POST", "/api/setup", body={
            "token": token,
            "user": {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "first_name": "TP2", "last_name": "Admin"},
            "prefs": {"site_name": "TP2 Audit 44"},
            "database": {
                "engine": "postgres",
                "name": "audit_immo_energie_44",
                "details": {
                    "host": PG_HOST, "port": PG_PORT, "dbname": PG_DB,
                    "user": PG_USER, "password": PG_PASSWORD, "ssl": False,
                },
            },
        })
        session = setup["id"]
        print(f"Compte admin créé : {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

    databases = call("GET", "/api/database", session=session).get("data", [])
    db = next((d for d in databases if d["name"] == "audit_immo_energie_44"), None)
    if db is None:
        db = call("POST", "/api/database", session=session, body={
            "engine": "postgres",
            "name": "audit_immo_energie_44",
            "details": {
                "host": PG_HOST, "port": PG_PORT, "dbname": PG_DB,
                "user": PG_USER, "password": PG_PASSWORD, "ssl": False,
            },
        })
    db_id = db["id"]

    dashboards = call("GET", "/api/dashboard", session=session)
    if any(d["name"] == DASHBOARD_NAME for d in dashboards):
        print("Dashboard déjà présent, rien à recréer.")
        return

    card_ids = []
    for name, sql, display in CARDS:
        card = call("POST", "/api/card", session=session, body={
            "name": name,
            "dataset_query": {"type": "native", "native": {"query": sql}, "database": db_id},
            "display": display,
            "visualization_settings": {},
            "collection_id": None,
        })
        card_ids.append(card["id"])
        print(f"Card créée : {name} (id={card['id']})")

    dashboard = call("POST", "/api/dashboard", session=session, body={"name": DASHBOARD_NAME})
    dashcards = [
        {"id": -(i + 1), "card_id": cid, "row": row, "col": col, "size_x": sx, "size_y": sy}
        for i, (cid, (row, col, sx, sy)) in enumerate(zip(card_ids, LAYOUT))
    ]
    call("PUT", f"/api/dashboard/{dashboard['id']}", session=session, body={"dashcards": dashcards})
    print(f"Dashboard créé : {DASHBOARD_NAME} (id={dashboard['id']})")
    print(f"-> http://localhost:3001/dashboard/{dashboard['id']}")


if __name__ == "__main__":
    main()
