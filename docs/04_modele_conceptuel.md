# 4. Modèle conceptuel (MCD)

## Entités et attributs

### COMMUNE
Table de référence géographique, issue du COG, restreinte au département 44 (207 communes).

- `code_insee` (identifiant)
- `nom_commune`
- `code_postal`
- `epci_code`, `epci_nom`
- `dep_code`, `dep_nom`
- `reg_code`, `reg_nom`

### TRANSACTION
Une transaction immobilière (mutation DVF), rattachée à une commune.

- `id_transaction` (identifiant)
- `id_mutation`
- `date_mutation`
- `nature_mutation`
- `valeur_fonciere`
- `type_local`
- `surface_reelle_bati`
- `nombre_pieces_principales`
- `surface_terrain`
- `longitude`, `latitude`

### DIAGNOSTIC_DPE
Un diagnostic de performance énergétique, rattaché à une commune.

- `numero_dpe` (identifiant)
- `date_etablissement_dpe`
- `etiquette_dpe`
- `etiquette_ges`
- `annee_construction`
- `periode_construction`
- `type_batiment`
- `surface_habitable_logement`
- `adresse`

## Relations et cardinalités

```
COMMUNE 1 ───── N TRANSACTION
COMMUNE 1 ───── N DIAGNOSTIC_DPE
```

- Une **commune** est concernée par **0 à N transactions** ; une **transaction** appartient à **exactement 1 commune**.
- Une **commune** est concernée par **0 à N diagnostics DPE** ; un **diagnostic** porte sur **exactement 1 commune**.

## Justification des choix

**Pourquoi ne pas relier directement TRANSACTION et DIAGNOSTIC_DPE ?**
Les deux sources ne partagent pas de clé fiable au niveau du logement individuel : DVF identifie une parcelle cadastrale (`id_parcelle`), le DPE une adresse géocodée (`adresse_ban`). Un rapprochement adresse-à-adresse est possible mais nécessite un géocodage/appariement flou (fuzzy matching), hors du périmètre d'un MCD simple. Le rapprochement est donc fait **au niveau commune**, la seule clé strictement commune et fiable aux deux sources (`code_insee`), ce qui suffit pour répondre à la problématique (comparer prix et performance énergétique par commune).

**Pourquoi une entité COMMUNE séparée plutôt que dupliquer les infos géographiques dans chaque table ?**
Pour éviter la redondance (nom de commune, département, région répétés sur des dizaines de milliers de lignes) et garantir la cohérence : une seule source de vérité pour le référentiel géographique (COG), utilisée en contrainte d'intégrité référentielle sur les deux autres tables.

## Diagramme (dbdiagram.io)

Schéma DBML prêt à coller sur [dbdiagram.io](https://dbdiagram.io) :

```dbml
Table commune {
  code_insee char(5) [pk]
  nom_commune varchar(100)
  code_postal char(5)
  epci_code varchar(15)
  epci_nom varchar(150)
  dep_code char(2)
  dep_nom varchar(50)
  reg_code char(2)
  reg_nom varchar(50)
}

Table transaction_dvf {
  id_transaction bigint [pk, increment]
  id_mutation varchar(20)
  date_mutation date
  nature_mutation varchar(50)
  valeur_fonciere numeric(12,2)
  code_insee char(5) [ref: > commune.code_insee]
  type_local varchar(50)
  surface_reelle_bati numeric(8,2)
  nombre_pieces_principales smallint
  surface_terrain numeric(10,2)
  longitude numeric(9,6)
  latitude numeric(9,6)
}

Table diagnostic_dpe {
  numero_dpe varchar(20) [pk]
  code_insee char(5) [ref: > commune.code_insee]
  date_etablissement_dpe date
  etiquette_dpe char(1)
  etiquette_ges char(1)
  annee_construction integer
  periode_construction varchar(20)
  type_batiment varchar(30)
  surface_habitable_logement numeric(8,2)
  adresse varchar(255)
}
```
