# TP — Audit & cartographie des données

Sujet : **Immobilier × Énergie**, performance énergétique et marché immobilier en **Loire-Atlantique (44)**.

Croisement de trois sources ouvertes (DVF, DPE ADEME, COG INSEE) pour passer de données réelles à une modélisation structurée, puis à une base PostgreSQL.

## Documentation

Chaque étape du TP est documentée dans [docs/](docs/) :

1. [00_cadrage.md](docs/00_cadrage.md) — cadrage, choix du sujet et du périmètre
2. [01_sources.md](docs/01_sources.md) — sources de données identifiées et documentées
3. [02_audit_qualite.md](docs/02_audit_qualite.md) — audit de la qualité des données
4. [03_modelisation.md](docs/03_modelisation.md) — MCD / MPD
5. [04_base_postgresql.md](docs/04_base_postgresql.md) — création de la base PostgreSQL et import

## Structure du dépôt

```
docs/    documentation de chaque étape du TP
data/    extraits de données (département 44) — non versionnés si volumineux
sql/     scripts DDL / import / requêtes d'analyse
tp_bdd.pdf   énoncé original (export tronqué, cf. docs/00_cadrage.md)
```

## Note sur l'énoncé

`tp_bdd.pdf` est un export web tronqué (une seule page, coupé en cours de section 2). Voir [docs/00_cadrage.md](docs/00_cadrage.md) pour le détail.
