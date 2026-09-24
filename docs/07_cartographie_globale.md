# 7. Cartographie globale

Vue d'ensemble du cheminement, des données brutes à la base PostgreSQL.

```
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ DVF géolocalisée (44)    │  │ DPE Logements existants  │  │ COG — communes           │
│ DGFiP / Etalab            │  │ ADEME (API data-fair)    │  │ INSEE                    │
│ files.data.gouv.fr/geo-dvf│  │ data.ademe.fr             │  │ data.gouv.fr              │
│ 79 949 lignes brutes       │  │ 351 959 lignes brutes     │  │ 207 communes du 44        │
└────────────┬─────────────┘  └────────────┬─────────────┘  └────────────┬─────────────┘
             │                              │                             │
             ▼                              ▼                             ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Audit qualité + nettoyage (pandas)                                     │
   │  filtrage code_insee absent du COG 44, valeurs manquantes, doublons,    │
   │  types (cf. docs/annexe_audit_qualite.md)                               │
   └───────────────────────────────────┬──────────────────────────────────┘
                                        ▼
                          data/staging/{commune,transaction_dvf,diagnostic_dpe}.csv
                                        │
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Modélisation : MCD (docs/04) → MLD (docs/05)                          │
   │  commune ──1─N── transaction_dvf                                        │
   │  commune ──1─N── diagnostic_dpe                                         │
   └───────────────────────────────────┬──────────────────────────────────┘
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Base PostgreSQL (docs/06)                                              │
   │  sql/01_create_tables.sql → sql/03_import_donnees_reelles.sql           │
   │  207 communes / 79 315 transactions / 351 959 diagnostics importés      │
   └───────────────────────────────────┬──────────────────────────────────┘
                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Analyse (sql/05_requetes_analyse.sql)                                  │
   │  prix moyen au m² × part de logements F-G, par commune                 │
   │  → réponse à la problématique (docs/01_presentation_sujet.md)          │
   └────────────────────────────────────────────────────────────────────────┘
```

## Lecture du schéma

1. **Trois sources hétérogènes** (formats et organisations différentes) sont ramenées à un périmètre commun : le département 44.
2. **L'audit qualité** filtre et nettoie chaque source indépendamment avant toute jointure, en s'appuyant sur une clé géographique commune fiable (`code_insee`).
3. **La modélisation** choisit délibérément une architecture "en étoile" simple (deux tables de faits reliées uniquement par la dimension commune) plutôt qu'un rapprochement fin transaction ↔ diagnostic, jugé trop incertain avec les clés disponibles (cf. justification dans [04_modele_conceptuel.md](04_modele_conceptuel.md)).
4. **La base PostgreSQL** matérialise ce modèle et a été testée de bout en bout avec les données réelles (0 ligne orpheline).
5. **L'analyse finale** répond à la problématique initiale à l'échelle communale, après correction d'un biais de calcul sur les mutations DVF multi-lots (cf. [annexe_audit_qualite.md](annexe_audit_qualite.md)), avec ses limites restantes documentées (petits effectifs sur les communes rurales, corrélation ≠ causalité).
