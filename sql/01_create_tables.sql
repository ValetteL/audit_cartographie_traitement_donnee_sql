-- TP Audit & cartographie des données — Immobilier x Énergie, département 44
-- Création des tables (cf. docs/05_modele_logique.md)

DROP TABLE IF EXISTS diagnostic_dpe CASCADE;
DROP TABLE IF EXISTS transaction_dvf CASCADE;
DROP TABLE IF EXISTS commune CASCADE;

CREATE TABLE commune (
    code_insee   CHAR(5)      PRIMARY KEY,
    nom_commune  VARCHAR(100) NOT NULL,
    code_postal  CHAR(5),
    epci_code    VARCHAR(15),
    epci_nom     VARCHAR(150),
    dep_code     CHAR(2)      NOT NULL,
    dep_nom      VARCHAR(50),
    reg_code     CHAR(2),
    reg_nom      VARCHAR(50)
);

CREATE TABLE transaction_dvf (
    id_transaction             BIGSERIAL PRIMARY KEY,
    id_mutation                VARCHAR(20) NOT NULL,
    date_mutation               DATE NOT NULL,
    nature_mutation             VARCHAR(50),
    valeur_fonciere             NUMERIC(12,2) NOT NULL CHECK (valeur_fonciere >= 0),
    code_insee                  CHAR(5) NOT NULL REFERENCES commune(code_insee),
    type_local                  VARCHAR(50),
    surface_reelle_bati         NUMERIC(8,2) CHECK (surface_reelle_bati >= 0),
    nombre_pieces_principales   SMALLINT,
    surface_terrain             NUMERIC(10,2) CHECK (surface_terrain >= 0),
    longitude                   NUMERIC(9,6),
    latitude                    NUMERIC(9,6)
);

CREATE TABLE diagnostic_dpe (
    numero_dpe                  VARCHAR(20) PRIMARY KEY,
    code_insee                  CHAR(5) NOT NULL REFERENCES commune(code_insee),
    date_etablissement_dpe      DATE,
    etiquette_dpe                CHAR(1) CHECK (etiquette_dpe IN ('A','B','C','D','E','F','G')),
    etiquette_ges                CHAR(1) CHECK (etiquette_ges IN ('A','B','C','D','E','F','G')),
    annee_construction           INTEGER,
    periode_construction         VARCHAR(20),
    type_batiment                 VARCHAR(30),
    surface_habitable_logement   NUMERIC(8,2) CHECK (surface_habitable_logement >= 0),
    adresse                       VARCHAR(255)
);

CREATE INDEX idx_transaction_code_insee ON transaction_dvf(code_insee);
CREATE INDEX idx_transaction_date ON transaction_dvf(date_mutation);
CREATE INDEX idx_dpe_code_insee ON diagnostic_dpe(code_insee);
CREATE INDEX idx_dpe_etiquette ON diagnostic_dpe(etiquette_dpe);
