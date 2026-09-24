-- Données de test (quelques lignes manuelles, indépendantes de l'import réel)
-- À exécuter après 01_create_tables.sql

INSERT INTO commune (code_insee, nom_commune, code_postal, epci_code, epci_nom, dep_code, dep_nom, reg_code, reg_nom) VALUES
('44109', 'Nantes',        '44000', '244400404', 'Nantes Métropole',              '44', 'Loire-Atlantique', '52', 'Pays de la Loire'),
('44184', 'Saint-Nazaire', '44600', '244400323', 'CARENE',                        '44', 'Loire-Atlantique', '52', 'Pays de la Loire'),
('44143', 'Rezé',          '44400', '244400404', 'Nantes Métropole',              '44', 'Loire-Atlantique', '52', 'Pays de la Loire');

INSERT INTO transaction_dvf (id_mutation, date_mutation, nature_mutation, valeur_fonciere, code_insee, type_local, surface_reelle_bati, nombre_pieces_principales, surface_terrain, longitude, latitude) VALUES
('2025-563765', '2025-01-03', 'Vente', 115000, '44109', 'Appartement', 43, 3, NULL, -1.538267, 47.232243),
('2025-570012', '2025-02-14', 'Vente', 245000, '44184', 'Maison',      98, 5, 620,  -2.213500, 47.273300),
('2025-571890', '2025-03-02', 'Vente', 189000, '44143', 'Appartement', 65, 3, NULL, -1.550100, 47.183900);

INSERT INTO diagnostic_dpe (numero_dpe, code_insee, date_etablissement_dpe, etiquette_dpe, etiquette_ges, annee_construction, periode_construction, type_batiment, surface_habitable_logement, adresse) VALUES
('2644E0039039K', '44109', '2026-01-07', 'C', 'C', 2020, '2013-2021', 'appartement', 64.3, '20 Route de Carquefou 44300 Nantes'),
('2244E0139144L', '44143', '2022-01-19', 'C', 'A', 2008, '2006-2012', 'appartement', 56.7, '21 Rue Benoît Chupiet 44400 Rezé'),
('2344E0200001A', '44184', '2023-06-10', 'F', 'F', 1975, 'avant 1978', 'maison',      98.0, '5 Rue de la Plage 44600 Saint-Nazaire');
