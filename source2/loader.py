"""Source 2 — DVF (open data, CSV), déjà collecté et nettoyé en TP1.

Rôle dans le projet : fournir le prix moyen au m² par commune, utilisé par
l'agrégateur pour enrichir chaque DPE reçu (lien métier : performance
énergétique vs marché immobilier local, cf. TP1).

Ce chargeur n'est pas un flux continu (DVF est mis à jour ~2x/an par la DGFiP) :
il tourne une fois au démarrage, dépose la donnée brute dans le Data Lake, et
produit un CSV dérivé (prix moyen au m² par commune) prêt pour la jointure.
"""
import csv
import os
import shutil
from collections import defaultdict

DVF_SRC = os.environ.get("DVF_SRC", "/data/staging/transaction_dvf.csv")
DATALAKE_RAW = os.environ.get("DATALAKE_RAW", "/datalake/raw/source2")
OUT_PRIX_COMMUNE = os.path.join(DATALAKE_RAW, "prix_moyen_commune.csv")


def main():
    os.makedirs(DATALAKE_RAW, exist_ok=True)

    dest = os.path.join(DATALAKE_RAW, "dvf_44.csv")
    shutil.copyfile(DVF_SRC, dest)
    print(f"[source2] DVF brut copié vers {dest}")

    # Agrégation par mutation (pas par ligne) pour éviter le biais des mutations
    # multi-lots identifié en TP1 (valeur_fonciere répétée sur chaque lot).
    mutations = {}  # id_mutation -> [valeur_fonciere, surface_totale, code_insee]
    with open(DVF_SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("type_local") not in ("Maison", "Appartement"):
                continue
            if row.get("nature_mutation") != "Vente":
                continue
            try:
                surface = float(row["surface_reelle_bati"])
                valeur = float(row["valeur_fonciere"])
            except (TypeError, ValueError):
                continue
            if surface <= 0:
                continue
            key = row["id_mutation"]
            if key not in mutations:
                mutations[key] = [valeur, 0.0, row["code_insee"]]
            mutations[key][1] += surface

    par_commune = defaultdict(list)
    for valeur, surface, code_insee in mutations.values():
        if surface > 0:
            par_commune[code_insee].append(valeur / surface)

    with open(OUT_PRIX_COMMUNE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["code_insee", "prix_m2_moyen", "nb_mutations"])
        for code_insee, prix_list in par_commune.items():
            moyenne = sum(prix_list) / len(prix_list)
            writer.writerow([code_insee, round(moyenne, 2), len(prix_list)])

    print(f"[source2] prix moyen au m² calculé pour {len(par_commune)} communes -> {OUT_PRIX_COMMUNE}")


if __name__ == "__main__":
    main()
