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

## Périmètre d'analyse pertinent sur transaction_dvf

Les taux de NULL globaux sur `transaction_dvf` (66 % sur `surface_reelle_bati`, 39 % sur `type_local`) donnent une image trompeuse si on ne précise pas qu'ils sont calculés sur **toutes** les natures de mutation confondues (terrain nu, dépendance, local commercial, etc.), pas seulement sur les logements. [sql/05_requetes_analyse.sql](../sql/05_requetes_analyse.sql) filtre déjà correctement `type_local IN ('Maison', 'Appartement')` pour le calcul du prix au m² — les autres catégories n'ont jamais pollué les résultats du TP1.

Recalculés sur ce même périmètre (Maison/Appartement, 24 775 lignes), les taux de complétude changent radicalement :

| Champ | Taux de NULL (toutes natures) | Taux de NULL (Maison/Appartement uniquement) |
|---|---|---|
| `surface_reelle_bati` | 66 % | **0 %** |
| `type_local` | 39 % | 0 % (filtre lui-même) |
| `nombre_pieces_principales` | 39 % | 0,2 % (46 lignes, après correction 1) |

**Décision** : ne pas supprimer les autres catégories de la table — ce sont des transactions réelles et légitimes (`transaction_dvf` a vocation à représenter toutes les mutations DVF du département, pas seulement celles utiles à cette analyse précise), et une future question pourrait vouloir les exploiter (marché du terrain nu, de l'immobilier commercial...). Le bon réflexe est de filtrer au niveau de la requête d'analyse (déjà fait), pas de tronquer la table source. Documenté ici pour que la lecture des taux de complétude globaux ne soit pas mal interprétée.

## `annee_construction` vs `periode_construction`

Aucune des deux colonnes n'est aujourd'hui exploitée dans les requêtes d'analyse existantes ([sql/05_requetes_analyse.sql](../sql/05_requetes_analyse.sql)) — la question de leur utilité se pose donc pour de futures analyses, pas pour corriger l'existant.

**Pourquoi garder les deux plutôt que ne garder que `periode_construction`** : elles ne portent pas la même information. `annee_construction` donne une précision à l'année quand elle est présente (66 % des lignes) ; `periode_construction` donne une tranche de 5 à 27 ans mais est complète à 100 %. Supprimer `annee_construction` détruirait une précision réelle sur les deux tiers du jeu de données pour un gain nul (`periode_construction` ne remplace pas cette précision, elle la complète). La bonne pratique est d'utiliser `periode_construction` comme champ par défaut pour toute analyse nécessitant la couverture complète, et `annee_construction` seulement pour une analyse plus fine limitée au sous-ensemble renseigné — pas de supprimer l'un des deux.

**Comment exploiter `periode_construction`** : c'est un champ catégoriel à 10 valeurs fixes, calées sur les grandes réglementations thermiques françaises (RT1974, RT1982/88, RT2000, RT2005, RT2012, RE2020) :

```
avant 1948, 1948-1974, 1975-1977, 1978-1982, 1983-1988,
1989-2000, 2001-2005, 2006-2012, 2013-2021, après 2021
```

Ce ne sont ni des dates ni des valeurs qui se trient correctement par ordre alphabétique ("après 2021" se classerait avant "avant 1948"). Toute analyse qui groupe ou trie par période doit donc passer par un ordre explicite plutôt qu'un `ORDER BY periode_construction` brut, par exemple :

```sql
-- Part de logements F-G par période de construction, dans l'ordre chronologique
SELECT periode_construction,
       COUNT(*) AS nb_diagnostics,
       ROUND(100.0 * COUNT(*) FILTER (WHERE etiquette_dpe IN ('F','G')) / COUNT(*), 1) AS pct_f_g
FROM diagnostic_dpe
GROUP BY periode_construction
ORDER BY CASE periode_construction
    WHEN 'avant 1948'  THEN 0  WHEN '1948-1974'  THEN 1
    WHEN '1975-1977'   THEN 2  WHEN '1978-1982'  THEN 3
    WHEN '1983-1988'   THEN 4  WHEN '1989-2000'  THEN 5
    WHEN '2001-2005'   THEN 6  WHEN '2006-2012'  THEN 7
    WHEN '2013-2021'   THEN 8  WHEN 'après 2021' THEN 9
END;
```

Hors périmètre de l'audit (aucune anomalie associée), mais vérifiée à titre d'illustration — le résultat confirme que `periode_construction` est directement exploitable et pertinent :

| periode_construction | nb_diagnostics | % F-G |
|---|---|---|
| avant 1948 | 67 870 | 17,7 |
| 1948-1974 | 100 922 | 10,5 |
| 1975-1977 | 11 448 | 2,9 |
| 1978-1982 | 15 989 | 1,7 |
| 1983-1988 | 16 570 | 0,7 |
| 1989-2000 | 38 865 | 0,3 |
| 2001-2005 | 15 540 | 0,1 |
| 2006-2012 | 38 284 | 0,1 |
| 2013-2021 | 36 467 | 0,0 |
| après 2021 | 10 004 | 0,0 |

Décroissance monotone, cohérente avec le durcissement progressif des réglementations thermiques (RT1974 → RE2020) : la part de "passoires énergétiques" chute de 17,7 % pour le bâti d'avant 1948 à 0,0 % pour le bâti post-2021.

## Recontrôle

Script [sql/07_audit_qualite.sql](../sql/07_audit_qualite.sql) ré-exécuté à l'identique après [sql/08_nettoyage.sql](../sql/08_nettoyage.sql), sur la base réelle (351 959 diagnostics, 79 315 transactions, 207 communes, pipeline TP2 tourné à ~350k lignes dans `diagnostic_dpe_flux`). Les deux anomalies corrigées passent à 0, les cinq décisions "aucune correction" restent inchangées à l'identique (preuve que les corrections 1 et 2 sont ciblées et n'ont pas d'effet de bord sur le reste de l'audit).

## Comment reproduire

[sql/08_nettoyage.sql](../sql/08_nettoyage.sql) est monté dans `docker-entrypoint-initdb.d` (`docker-compose.yml`, service `db`), juste après l'import des données réelles : les deux corrections s'appliquent **automatiquement** au premier `docker compose up -d`, sans étape manuelle — vérifié en repartant d'un volume vide (`docker compose down -v && docker compose up -d`), logs de `db` :

```
running /docker-entrypoint-initdb.d/04_nettoyage.sql
UPDATE 46
UPDATE 34
UPDATE 0   -- diagnostic_dpe_flux, vide à ce stade de l'initialisation (cf. note ci-dessous)
```

Pour rejouer l'audit à la main (avant/après, ou pour nettoyer `diagnostic_dpe_flux` une fois qu'elle contient des données — alimentée en continu après le démarrage, sa correction au moment de l'init ne porte que sur ce qui existe déjà, cf. décision "audit ponctuel" ci-dessus) :

```bash
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # avant
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/08_nettoyage.sql        # corrections
docker exec -i tp_audit_44_pg psql -U postgres -d audit_immo_energie_44 < sql/07_audit_qualite.sql   # après
```
