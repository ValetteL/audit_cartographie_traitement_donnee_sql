# 5. Modèle logique (MLD)

Traduction du modèle conceptuel ([04_modele_conceptuel.md](04_modele_conceptuel.md)) en tables relationnelles. Script de création correspondant : [sql/01_create_tables.sql](../sql/01_create_tables.sql).

## commune

| Colonne | Type | Contrainte |
|---|---|---|
| code_insee | CHAR(5) | **PK** |
| nom_commune | VARCHAR(100) | NOT NULL |
| code_postal | CHAR(5) | |
| epci_code | VARCHAR(15) | |
| epci_nom | VARCHAR(150) | |
| dep_code | CHAR(2) | NOT NULL |
| dep_nom | VARCHAR(50) | |
| reg_code | CHAR(2) | |
| reg_nom | VARCHAR(50) | |

## transaction_dvf

| Colonne | Type | Contrainte |
|---|---|---|
| id_transaction | BIGSERIAL | **PK** |
| id_mutation | VARCHAR(20) | NOT NULL |
| date_mutation | DATE | NOT NULL |
| nature_mutation | VARCHAR(50) | |
| valeur_fonciere | NUMERIC(12,2) | NOT NULL, CHECK ≥ 0 |
| code_insee | CHAR(5) | **FK** → commune(code_insee), NOT NULL |
| type_local | VARCHAR(50) | |
| surface_reelle_bati | NUMERIC(8,2) | CHECK ≥ 0 |
| nombre_pieces_principales | SMALLINT | |
| surface_terrain | NUMERIC(10,2) | CHECK ≥ 0 |
| longitude | NUMERIC(9,6) | |
| latitude | NUMERIC(9,6) | |

Notation : `transaction_dvf` porte une clé primaire technique (`id_transaction`) car une même mutation DVF (`id_mutation`) peut apparaître sur plusieurs lignes du fichier source (un lot/parcelle par ligne) — `id_mutation` est donc conservé comme attribut, pas comme clé.

## diagnostic_dpe

| Colonne | Type | Contrainte |
|---|---|---|
| numero_dpe | VARCHAR(20) | **PK** |
| code_insee | CHAR(5) | **FK** → commune(code_insee), NOT NULL |
| date_etablissement_dpe | DATE | |
| etiquette_dpe | CHAR(1) | CHECK IN (A..G) |
| etiquette_ges | CHAR(1) | CHECK IN (A..G) |
| annee_construction | INTEGER | |
| periode_construction | VARCHAR(20) | |
| type_batiment | VARCHAR(30) | |
| surface_habitable_logement | NUMERIC(8,2) | CHECK ≥ 0 |
| adresse | VARCHAR(255) | |

## diagnostic_dpe_flux

Table ajoutée en TP2 (pipeline temps réel), absente du modèle initial ci-dessus — reprise ici lors de la vérification du schéma cible en TP3 ([09_tp3_audit_qualite.md](09_tp3_audit_qualite.md)). Script de création : [sql/06_create_flux_table.sql](../sql/06_create_flux_table.sql).

| Colonne | Type | Contrainte |
|---|---|---|
| numero_dpe | VARCHAR(20) | **PK** |
| code_insee | CHAR(5) | **FK** → commune(code_insee), NOT NULL |
| date_reception_dpe | DATE | |
| etiquette_dpe | CHAR(1) | CHECK IN (A..G) |
| etiquette_ges | CHAR(1) | CHECK IN (A..G) |
| surface_habitable_logement | NUMERIC(8,2) | CHECK ≥ 0 |
| prix_m2_commune_reference | NUMERIC(10,2) | |
| source_flux | VARCHAR(10) | NOT NULL, CHECK IN (backfill, live) |
| traite_le | TIMESTAMP | NOT NULL, DEFAULT now() |

Volontairement plus étroite que `diagnostic_dpe` (pas d'`annee_construction`, `periode_construction`, `type_batiment`, `adresse`) : ne reprend que les champs utiles au flux temps réel et à son enrichissement (prix au m² de la commune, calculé côté pipeline TP2).

## Relations (clés étrangères)

- `transaction_dvf.code_insee` → `commune.code_insee`
- `diagnostic_dpe.code_insee` → `commune.code_insee`
- `diagnostic_dpe_flux.code_insee` → `commune.code_insee`

## Index

- `commune` : PK sur `code_insee` (index automatique)
- `transaction_dvf` : index sur `code_insee` (jointures), index sur `date_mutation`
- `diagnostic_dpe` : index sur `code_insee` (jointures), index sur `etiquette_dpe`
- `diagnostic_dpe_flux` : index sur `code_insee`, index sur `traite_le`
