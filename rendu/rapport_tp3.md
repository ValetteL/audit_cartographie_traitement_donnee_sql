---
title: "TP3 — Audit qualité & nettoyage des données"
subtitle: "Prolongement du TP1/TP2 — Immobilier × Énergie, Loire-Atlantique (44)"
author:
  - Louis Valette
  - Alexis Fouquet
  - Ruben Cofflard
toc: true
toc-depth: 1
geometry: margin=2.2cm
fontsize: 11pt
mainfont: "Calibri"
monofont: "Consolas"
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes: |
  \usepackage{etoolbox}
  \usepackage[htt]{hyphenat}
  \usepackage{float}
  \floatplacement{figure}{H}
  \AtBeginEnvironment{longtable}{\small}
  \AtBeginEnvironment{Shaded}{\footnotesize}
---

# 1. Périmètre

Audit qualité sur les 4 tables du schéma cible (TP1 : `commune`, `transaction_dvf`, `diagnostic_dpe` ; TP2 : `diagnostic_dpe_flux`). Le schéma cible, vérifié à cette occasion, est tenu à jour dans [docs/05_modele_logique.md](../docs/05_modele_logique.md) (`diagnostic_dpe_flux` y manquait, ajoutée avant l'audit).

# 2. Matrice de contrôles qualité

Ciblée sur ce que les contraintes SQL actives (PK, FK, CHECK) ne couvrent pas déjà.

| Dimension | Contrôle |
|---|---|
| Complétude | Taux de NULL sur les champs significatifs (`annee_construction`, `surface_habitable_logement`, `surface_reelle_bati`...) |
| Unicité | Cohérence des doublons attendus (multi-lots DVF) ; risque de faux positif sur "adresse + date" |
| Validité | Valeurs hors bornes plausibles (pièces à 0, surfaces aberrantes, années impossibles) |
| Cohérence | Prix au m² extrêmes, agrégés par mutation |
| Intégrité référentielle | Orphelins sur les 3 relations vers `commune` |

# 3. Méthodologie

Script unique, [sql/07_audit_qualite.sql](../sql/07_audit_qualite.sql), exécuté à l'identique avant et après [sql/08_nettoyage.sql](../sql/08_nettoyage.sql).

Deux pièges méthodologiques rencontrés, qui ont changé la façon dont les contrôles sont écrits :

- **Prix au m² non calculable ligne par ligne** : une mutation DVF à plusieurs lots répète la même `valeur_fonciere` sur chaque ligne — diviser par la surface d'un seul lot donne des prix au m² absurdes (jusqu'à 566 250 €/m² avant correction de la méthode). Agrégation par `id_mutation` requise (même logique qu'en TP1).
- **"Même adresse + même date" n'est pas un doublon** : un immeuble collectif peut compter plusieurs centaines de logements diagnostiqués la même campagne (jusqu'à 869 observés) — chacun avec un `numero_dpe` distinct et légitime.

# 4. Anomalies et corrections

| # | Anomalie | Avant | Après | Décision |
|---|---|---|---|---|
| 1 | `nombre_pieces_principales = 0` sur logement habitable | 46 | **0** | Substitution → NULL |
| 2 | `surface_habitable_logement` > 400 m² pour un appartement | 34 | **0** | Substitution → NULL |
| 3 | `annee_construction` < 1700 | 34 | 34 | Aucune correction (bâti ancien réel, rien ne prouve l'erreur) |
| 4 | Mutations à prix/m² > 15 000 €/m² (agrégées) | 22 | 22 | Aucune correction (valeurs individuelles plausibles, ratio non interprétable à ce niveau) |
| 5 | `annee_construction` NULL | 119 644 (34 %) | inchangé | Aucune imputation (`periode_construction`, complet à 100 %, sert de substitut) |
| 6 | NULL structurels `transaction_dvf` (mutations sans bâti) | 52 589 / 31 229 | inchangé | Aucune correction (absence légitime, 0 cas sur Maison/Appartement) |
| 7 | Orphelins référentiels | 0 | 0 | Contrôle confirmatoire (déjà garanti par les FK) |

Deux corrections réelles (46 + 34 lignes), cinq décisions documentées de ne pas corriger — pour ne pas laisser d'anomalies non traitées en silence.

# 5. Recontrôle

Script d'audit ré-exécuté à l'identique après nettoyage, sur la base réelle (351 959 diagnostics, 79 315 transactions, 207 communes). Les deux anomalies corrigées passent à 0 ; les cinq décisions "aucune correction" restent inchangées à l'identique, confirmant que les corrections appliquées sont ciblées et sans effet de bord.

## Comment reproduire

```bash
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # avant
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/08_nettoyage.sql        # corrections
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # après
```
