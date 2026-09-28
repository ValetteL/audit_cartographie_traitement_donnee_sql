# 9. TP3 — Audit qualité & nettoyage des données

Audit de qualité sur les 4 tables produites par le TP1 et le TP2, correction des anomalies confirmées, recontrôle. Prolonge le TP1/TP2 : mêmes tables, même base.

## Cartographie et schéma cible

Le schéma cible (4 tables : `commune`, `transaction_dvf`, `diagnostic_dpe`, `diagnostic_dpe_flux`) est vérifié et à jour dans [05_modele_logique.md](05_modele_logique.md) et [07_cartographie_globale.md](07_cartographie_globale.md) — `diagnostic_dpe_flux` (ajoutée en TP2) y manquait, corrigé à l'occasion de ce TP3.

## Matrice de contrôles qualité

Ciblée sur ce que les contraintes SQL déjà actives (PK, FK, CHECK) ne couvrent **pas** — sinon l'audit ne ferait que redémontrer des contraintes déjà appliquées à l'insertion.

| Dimension | Table.champ | Règle | Requête (sql/07) |
|---|---|---|---|
| Complétude | `diagnostic_dpe.annee_construction` | Taux de NULL | § 1 |
| Complétude | `diagnostic_dpe(_flux).surface_habitable_logement` | Taux de NULL | § 1 |
| Complétude | `transaction_dvf.surface_reelle_bati` / `type_local` / `longitude` | Taux de NULL, structurel ou non | § 1 |
| Unicité | `diagnostic_dpe.adresse` + `date_etablissement_dpe` | Faux doublons potentiels | § 2 |
| Unicité | `transaction_dvf.id_mutation` | `valeur_fonciere` cohérente sur tous les lots d'une même mutation | § 2 |
| Validité | `transaction_dvf.nombre_pieces_principales` | = 0 invalide pour un logement habitable | § 3 |
| Validité | `diagnostic_dpe.surface_habitable_logement` | > 400 m² invraisemblable pour un "appartement" | § 3 |
| Validité | `diagnostic_dpe.annee_construction` | < 1700 : cas extrêmes à examiner | § 3 |
| Cohérence | `transaction_dvf` (agrégé par mutation) | Prix au m² > 15 000 €/m² | § 4 |
| Intégrité référentielle | `*.code_insee` → `commune.code_insee` | 0 orphelin attendu | § 5 |

## Méthodologie de l'audit

Script unique, [sql/07_audit_qualite.sql](../sql/07_audit_qualite.sql), exécuté à l'identique avant et après [sql/08_nettoyage.sql](../sql/08_nettoyage.sql) pour produire le comparatif ci-dessous. Deux points méthodologiques rencontrés en cours d'audit, qui ont changé la façon dont les contrôles sont écrits :

- **Le prix au m² ne peut pas être calculé ligne par ligne.** Une mutation DVF à plusieurs lots répète la même `valeur_fonciere` (le prix total de la mutation) sur chaque ligne — diviser par la surface d'une seule ligne produit des prix au m² absurdes (jusqu'à 566 250 €/m² observés avant correction de la méthode). Le contrôle de cohérence agrège d'abord par `id_mutation` (même logique que [sql/05_requetes_analyse.sql](../sql/05_requetes_analyse.sql), déjà établie en TP1).
- **"Même adresse + même date" n'est pas un critère de doublon fiable.** Un immeuble collectif peut légitimement compter plusieurs centaines de logements diagnostiqués la même campagne, à la même adresse (jusqu'à 869 DPE observés pour une seule adresse+date) — chacun avec un `numero_dpe` distinct, donc un logement réellement différent. La clé primaire (`numero_dpe`) reste le seul critère d'unicité fiable ; ce contrôle sert à documenter pourquoi une intuition naïve serait fausse, pas à trouver de vrais doublons.

## Anomalies identifiées et corrections

| # | Anomalie | Avant | Après | Décision | Justification |
|---|---|---|---|---|---|
| 1 | `nombre_pieces_principales = 0` sur un logement (Maison/Appartement) | 46 | **0** | Substitution → NULL | 0 pièce est invalide pour un logement habitable (normal en revanche pour Dépendance/local) ; vraie valeur inconnue, NULL plutôt qu'une valeur inventée |
| 2 | `surface_habitable_logement` > 400 m² pour un "appartement" | 34 | **0** | Substitution → NULL | Au-delà des plus grands appartements individuels réels du marché français ; probable confusion avec la surface totale de l'immeuble. Répercuté sur `diagnostic_dpe_flux` |
| 3 | `annee_construction` < 1700 | 34 | 34 (inchangé) | **Aucune correction** | Le bâti ancien existe réellement en Loire-Atlantique ; rien ne prouve que ces valeurs soient fausses — les supprimer sur la seule base de leur rareté statistique ne serait pas justifiable |
| 4 | Mutations à prix/m² > 15 000 €/m² (agrégées) | 22 | 22 (inchangé) | **Aucune correction** | Chaque valeur brute est individuellement plausible ; le ratio n'est pas interprétable à ce niveau (ventes en bloc multi-lots à surface partiellement renseignée, ou marché haut de gamme réel du littoral) — à exclure de tout calcul de moyenne, pas à corriger |
| 5 | `annee_construction` NULL | 119 644 (34 %) | 119 644 (inchangé) | **Aucune imputation** | Fabriquer une année précise sur 34 % du jeu de données introduirait plus de biais que ça n'en résout. `periode_construction`, complet à 100 %, reste le substitut fiable pour toute analyse par époque |
| 6 | `surface_reelle_bati`/`type_local`/`surface_terrain` NULL sur `transaction_dvf` | 52 589 / 31 229 / 25 854 | inchangé | **Aucune correction** | NULL structurel : 0 cas sur les types Maison/Appartement, 100 % sur les mutations sans bâti (terrain nu, dépendance) — absence légitime, pas une anomalie |
| 7 | Orphelins référentiels (3 relations) | 0 / 0 / 0 | 0 / 0 / 0 | Contrôle confirmatoire | Déjà garanti par les contraintes FK à l'insertion |

Deux corrections réelles appliquées (46 + 34 lignes), cinq décisions de ne pas corriger — documentées ici plutôt que silencieuses, pour ne pas donner l'impression d'anomalies non traitées.

## Recontrôle

Script [sql/07_audit_qualite.sql](../sql/07_audit_qualite.sql) ré-exécuté à l'identique après [sql/08_nettoyage.sql](../sql/08_nettoyage.sql), sur la base réelle (351 959 diagnostics, 79 315 transactions, 207 communes, pipeline TP2 tourné à ~350k lignes dans `diagnostic_dpe_flux`). Les deux anomalies corrigées passent à 0, les cinq décisions "aucune correction" restent inchangées à l'identique (preuve que les corrections 1 et 2 sont ciblées et n'ont pas d'effet de bord sur le reste de l'audit).

## Comment reproduire

```bash
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # avant
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/08_nettoyage.sql        # corrections
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # après
```
