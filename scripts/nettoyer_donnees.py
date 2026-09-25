"""Nettoie les 3 extraits bruts (département 44) et produit les CSV prêts à
l'import dans data/staging/, conformes au modèle logique (docs/05_modele_logique.md).

Prérequis : les fichiers bruts dans data/ (cf. scripts/telecharger_donnees.sh
ou docs/02_sources.md).
Usage (depuis la racine du projet) : python scripts/nettoyer_donnees.py
"""
import pandas as pd

DATA = "data"
STAGING = f"{DATA}/staging"


def main():
    # ---------- COMMUNE ----------
    cog = pd.read_csv(f"{DATA}/cog_communes_44.csv", dtype=str)
    print(f"COG 44 : {len(cog)} lignes brutes")
    cog_clean = cog[[
        "code_insee", "nom_standard", "code_postal", "epci_code", "epci_nom",
        "dep_code", "dep_nom", "reg_code", "reg_nom",
    ]].copy()
    cog_clean.columns = [
        "code_insee", "nom_commune", "code_postal", "epci_code", "epci_nom",
        "dep_code", "dep_nom", "reg_code", "reg_nom",
    ]
    print(f"COG : doublons code_insee = {cog_clean['code_insee'].duplicated().sum()}")
    cog_clean = cog_clean.drop_duplicates(subset=["code_insee"]).dropna(subset=["code_insee"])
    cog_clean.to_csv(f"{STAGING}/commune.csv", index=False)
    print(f"COG : {len(cog_clean)} communes -> {STAGING}/commune.csv")
    valid_insee = set(cog_clean["code_insee"])

    # ---------- DVF ----------
    dvf = pd.read_csv(f"{DATA}/dvf_44_2025.csv.gz", dtype=str, compression="gzip")
    print(f"\nDVF : {len(dvf)} lignes brutes")

    dvf_clean = dvf[[
        "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere",
        "code_commune", "type_local", "surface_reelle_bati",
        "nombre_pieces_principales", "surface_terrain", "longitude", "latitude",
    ]].copy()
    dvf_clean.columns = [
        "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere",
        "code_insee", "type_local", "surface_reelle_bati",
        "nombre_pieces_principales", "surface_terrain", "longitude", "latitude",
    ]

    before = len(dvf_clean)
    dvf_clean = dvf_clean[dvf_clean["code_insee"].isin(valid_insee)]

    dvf_clean["valeur_fonciere"] = pd.to_numeric(dvf_clean["valeur_fonciere"], errors="coerce")
    dvf_clean["surface_reelle_bati"] = pd.to_numeric(dvf_clean["surface_reelle_bati"], errors="coerce")
    dvf_clean["surface_terrain"] = pd.to_numeric(dvf_clean["surface_terrain"], errors="coerce")
    dvf_clean["nombre_pieces_principales"] = pd.to_numeric(
        dvf_clean["nombre_pieces_principales"], errors="coerce"
    ).astype("Int64")
    dvf_clean["longitude"] = pd.to_numeric(dvf_clean["longitude"], errors="coerce")
    dvf_clean["latitude"] = pd.to_numeric(dvf_clean["latitude"], errors="coerce")

    dvf_clean = dvf_clean.dropna(subset=["valeur_fonciere"])
    print(f"DVF : {len(dvf_clean)} lignes -> {STAGING}/transaction_dvf.csv (sur {before} initiales)")
    dvf_clean.to_csv(f"{STAGING}/transaction_dvf.csv", index=False)

    # ---------- DPE ----------
    dpe = pd.read_csv(f"{DATA}/dpe_44.csv", dtype=str)
    print(f"\nDPE : {len(dpe)} lignes brutes")
    valid_labels = set("ABCDEFG")

    dpe_clean = dpe.rename(columns={"adresse_ban": "adresse"}).drop(columns=["code_postal_ban"])
    before = len(dpe_clean)
    dpe_clean = dpe_clean[dpe_clean["code_insee_ban"].isin(valid_insee)]
    dpe_clean = dpe_clean.rename(columns={"code_insee_ban": "code_insee"})

    dpe_clean = dpe_clean[
        dpe_clean["etiquette_dpe"].isin(valid_labels) & dpe_clean["etiquette_ges"].isin(valid_labels)
    ]
    dpe_clean = dpe_clean.drop_duplicates(subset=["numero_dpe"])
    dpe_clean["annee_construction"] = pd.to_numeric(dpe_clean["annee_construction"], errors="coerce").astype("Int64")
    dpe_clean["surface_habitable_logement"] = pd.to_numeric(
        dpe_clean["surface_habitable_logement"], errors="coerce"
    )

    print(f"DPE : {len(dpe_clean)} lignes -> {STAGING}/diagnostic_dpe.csv (sur {before} initiales)")
    dpe_clean.to_csv(f"{STAGING}/diagnostic_dpe.csv", index=False)

    print("\nTerminé.")


if __name__ == "__main__":
    main()
