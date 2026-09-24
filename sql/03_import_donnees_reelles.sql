-- Import des données réelles nettoyées (département 44) depuis data/staging/
-- À exécuter sur une base fraîchement créée (01_create_tables.sql), sans les données de test.

\copy commune(code_insee, nom_commune, code_postal, epci_code, epci_nom, dep_code, dep_nom, reg_code, reg_nom) FROM 'data/staging/commune.csv' WITH (FORMAT csv, HEADER true);

\copy transaction_dvf(id_mutation, date_mutation, nature_mutation, valeur_fonciere, code_insee, type_local, surface_reelle_bati, nombre_pieces_principales, surface_terrain, longitude, latitude) FROM 'data/staging/transaction_dvf.csv' WITH (FORMAT csv, HEADER true);

\copy diagnostic_dpe(numero_dpe, code_insee, date_etablissement_dpe, etiquette_dpe, etiquette_ges, annee_construction, periode_construction, type_batiment, surface_habitable_logement, adresse) FROM 'data/staging/diagnostic_dpe.csv' WITH (FORMAT csv, HEADER true);
