# 4. Modèle conceptuel (MCD)

## Entités

- **COMMUNE** — référentiel géographique (COG), restreint au département 44 (207 communes).
- **TRANSACTION** — une transaction immobilière (mutation DVF), rattachée à une commune.
- **DIAGNOSTIC_DPE** — un diagnostic de performance énergétique, rattaché à une commune.
- **DIAGNOSTIC_DPE_FLUX** — même nature que DIAGNOSTIC_DPE, alimentée en continu par le pipeline temps réel du TP2 plutôt qu'importée une fois ; ajoutée au modèle à cette occasion (absente du diagramme dbdiagram.io ci-dessous, réalisé avant le TP2 — cf. [05_modele_logique.md](05_modele_logique.md) pour son schéma logique à jour).

## Relations et cardinalités

```
COMMUNE 1 ───── N TRANSACTION
COMMUNE 1 ───── N DIAGNOSTIC_DPE
COMMUNE 1 ───── N DIAGNOSTIC_DPE_FLUX
```

Une **commune** est concernée par **0 à N transactions**, **0 à N diagnostics DPE** et **0 à N lignes du flux temps réel** ; chaque **transaction** et chaque **diagnostic** (statique ou temps réel) appartient à **exactement 1 commune**. Même justification de rattachement que DIAGNOSTIC_DPE ci-dessous — DIAGNOSTIC_DPE_FLUX en hérite sans changement de logique.

## Justification des choix

- **Pas de lien direct TRANSACTION ↔ DIAGNOSTIC_DPE** : les deux sources n'ont pas de clé fiable au niveau du logement (DVF identifie une parcelle, le DPE une adresse géocodée). Le rapprochement se fait donc **au niveau commune**, seule clé fiable aux deux sources, suffisante pour répondre à la problématique.
- **Entité COMMUNE séparée** plutôt que dupliquer les infos géographiques dans chaque table : évite la redondance et garantit une source de vérité unique (le COG), en contrainte d'intégrité référentielle sur les deux autres tables.

## Diagramme

Réalisé sur [dbdiagram.io](https://dbdiagram.io) :

![Modèle conceptuel — dbdiagram.io](assets/modele_conceptuel_dbdiagram.png){width=90%}
