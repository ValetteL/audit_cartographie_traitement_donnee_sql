-- TP2 : table cible du pipeline temps réel (Kafka -> agrégation -> Data Lake -> PySpark -> ici)
-- Chaque ligne = un diagnostic DPE (flux, backfill ou live), enrichi du prix moyen au m²
-- de sa commune (DVF, déjà en base depuis le TP1) au moment de son traitement.

CREATE TABLE IF NOT EXISTS diagnostic_dpe_flux (
    numero_dpe                  VARCHAR(20) PRIMARY KEY,
    code_insee                  CHAR(5) NOT NULL REFERENCES commune(code_insee),
    date_reception_dpe          DATE,
    etiquette_dpe                CHAR(1) CHECK (etiquette_dpe IN ('A','B','C','D','E','F','G')),
    etiquette_ges                CHAR(1) CHECK (etiquette_ges IN ('A','B','C','D','E','F','G')),
    surface_habitable_logement   NUMERIC(8,2) CHECK (surface_habitable_logement >= 0),
    prix_m2_commune_reference    NUMERIC(10,2),
    source_flux                  VARCHAR(10) NOT NULL CHECK (source_flux IN ('backfill', 'live')),
    traite_le                    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dpe_flux_code_insee ON diagnostic_dpe_flux(code_insee);
CREATE INDEX IF NOT EXISTS idx_dpe_flux_traite_le ON diagnostic_dpe_flux(traite_le);
