# Script de soutenance TP3

Sep 28, 2026 · @Ruben

Ce script suit les 16 diapos de la présentation pour tenir 15 minutes : pour chaque diapo, ce qu'il faut dire, en langage simple, et la phrase qui mène à la suivante.

## Mode d'emploi

Un tiers de la présentation chacun, environ 5 minutes par orateur. Cette répartition est une proposition, à ajuster entre vous.

| Diapos | Partie | Durée | Orateur proposé |
| --- | --- | --- | --- |
| 1 à 6 | Problématique et cheminement | 5 min | Ruben |
| 7 à 11 | Résultats et début de l'audit | 5 min | Alexis |
| 12 à 16 | Fin de l'audit et conclusion | 5 min | Louis |

Trois conseils :

- Ne lisez pas les diapos : elles montrent les chiffres, vous expliquez ce qu'ils veulent dire.
- Une idée par diapo. Si vous êtes en retard, raccourcissez les diapos 5, 8 et 12.
- Chaque orateur annonce le suivant avec la phrase de transition, pour que le passage de relais soit fluide.

## Partie 1 · Problématique

### Diapo 1 — Titre (30 s, Ruben)

**À dire :** « Bonjour. Nous sommes Ruben, Alexis et Louis, et nous allons vous présenter le TP3 : l'audit qualité et le nettoyage des données de notre projet Immobilier × Énergie en Loire-Atlantique. On va suivre quatre temps : la problématique, le chemin parcouru sur les trois TP, nos résultats, puis une conclusion centrée sur l'audit qualité. »

### Diapo 2 — La question de départ (1 min, Ruben)

**Message clé :** on veut savoir si la performance énergétique d'un logement se voit dans son prix.

**À dire :** « Depuis 2021, le diagnostic de performance énergétique, le DPE, pèse sur la décision d'achat. On s'est donc posé une question simple : en Loire-Atlantique, est-ce que les logements énergivores, classés F ou G, se vendent moins cher que les logements performants, classés A, B ou C ? Et est-ce que ça change d'une commune à l'autre ? On a choisi le 44 parce qu'il mélange une grande ville, Nantes, du littoral et des zones rurales, avec 207 communes, donc un volume de données raisonnable. Pour répondre, il fallait croiser les prix de vente et les diagnostics dans une base SQL. »

**Transition :** « Voyons d'abord avec quelles données on a travaillé. »

## Partie 2 · Cheminement

### Diapo 3 — Trois sources ouvertes (30 s, Ruben)

**À dire :** « On a croisé trois sources publiques : les 207 communes de l'INSEE, 79 315 ventes immobilières issues de DVF, et 351 959 diagnostics DPE de l'ADEME. Elles sont toutes reliées par un seul identifiant, le code INSEE de la commune. Le dernier chiffre, environ 350 000, ce sont les diagnostics qui repassent par notre flux temps réel du TP2. »

### Diapo 4 — Trois TP, trois étapes (1 min, Ruben)

**Message clé :** une seule base, enrichie à chaque TP.

**À dire :** « Le projet s'est construit en trois étapes. Au TP1, on a structuré : dictionnaire de données, modèle conceptuel puis logique, et la base PostgreSQL avec nos premières requêtes d'analyse. Au TP2, on a alimenté la base en continu : Kafka transporte les données, Spark les nettoie, Grafana surveille le pipeline et Metabase affiche les résultats. Au TP3, qui est le sujet d'aujourd'hui, on a fiabilisé : on a audité la qualité des données, corrigé ce qui devait l'être et vérifié le résultat. »

### Diapo 5 — Le modèle en étoile (1 min, Ruben)

**Message clé :** tout passe par la commune, la seule clé commune fiable.

**À dire :** « Voici le schéma de la base. Au centre, la table commune. Autour, les tables de faits : les ventes DVF, les diagnostics DPE, et la table du flux temps réel ajoutée au TP2. Pourquoi passer par la commune ? Parce que DVF identifie une parcelle et le DPE une adresse : il n'y a pas de clé fiable au niveau du logement. En vérifiant ce schéma au TP3, on a d'ailleurs vu que la table du flux manquait dans notre modèle logique : on l'a ajoutée. »

### Diapo 6 — La méthode d'audit (1 min, Ruben)

**Message clé :** préparer, mesurer, corriger, vérifier, avec le même script avant et après.

**À dire :** « L'audit a suivi trois temps. Préparer : on revérifie la cartographie, puis on définit une matrice de contrôles sur cinq dimensions : complétude, unicité, validité, cohérence et intégrité. Mesurer : on lance l'audit en SQL et on classe les anomalies par importance. Corriger et vérifier : on nettoie en justifiant chaque choix, puis on relance exactement le même script. C'est la flèche du bas : mêmes requêtes, mêmes seuils, donc une comparaison avant/après honnête. »

**Transition (passage à Alexis) :** « Avant de détailler l'audit, Alexis va vous montrer ce que les données nous ont appris. »

## Partie 3 · Résultats

### Diapo 7 — Les communes chères ont moins de passoires (1 min 15, Alexis)

**Message clé :** un lien apparaît entre prix et énergie, mais c'est une corrélation.

**À dire :** « Premier résultat, qui répond à la problématique. On a calculé le prix moyen au mètre carré et la part de logements F-G, commune par commune. Les communes les plus chères, La Baule à 6 536 euros le mètre carré, Pornichet et Nantes, ont une part de passoires plus faible. À l'inverse, Juigné-des-Moutiers, à 892 euros le mètre carré, compte presque 36 % de logements F ou G. Deux précautions : les petites communes rurales ont peu de ventes, donc leurs chiffres sont fragiles. Et une corrélation n'est pas une causalité : la localisation, littoral contre rural, joue aussi beaucoup. »

### Diapo 8 — L'époque de construction (1 min, Alexis)

**Message clé :** plus le logement est ancien, plus il a de chances d'être une passoire.

**À dire :** « Deuxième résultat : la part de passoires dépend fortement de l'époque de construction. Près de 18 % pour le bâti d'avant 1948, 10 % entre 1948 et 1974, puis presque zéro après 2000. C'est cohérent avec les réglementations thermiques successives, de 1974 jusqu'à la RE2020. Ça explique aussi en partie le résultat précédent : les communes rurales ont un parc plus ancien. »

### Diapo 9 — Le tableau de bord Metabase (1 min, Alexis)

**Message clé :** les résultats sont visibles directement dans notre outil de visualisation.

**À dire :** « Voici notre tableau de bord Metabase, branché sur la base au TP2. Le premier graphique montre que les trois quarts des logements du département sont classés C ou D, et environ 4,5 % sont classés F. Au centre, les 350 000 diagnostics sont tous passés par notre pipeline temps réel. En bas, on retrouve les dix communes les plus chères, avec La Baule en tête : c'est cohérent avec la diapo précédente. Ce tableau de bord se configure automatiquement au démarrage du projet. »

**Transition :** « Ces résultats ne valent que si les données sont fiables. C'est tout l'objet de l'audit qualité. »

## Partie 4 · Audit qualité

### Diapo 10 — Le bilan (30 s, Alexis)

**À dire :** « En une phrase : nos données sont globalement fiables. On a analysé six anomalies sur les quatre tables. Deux ont été corrigées, soit 80 lignes. Les quatre autres ont été volontairement conservées, avec une justification pour chacune. Et aucune ligne ne pointe vers une commune qui n'existe pas. »

### Diapo 11 — Six anomalies classées (1 min 15, Alexis)

**Message clé :** l'importance d'une anomalie, c'est son volume multiplié par son risque de fausser l'analyse.

**À dire :** « Voici les six anomalies, avec leur volume et leur importance. Les deux premières sont de vraies erreurs : 46 maisons ou appartements avec zéro pièce, et 34 appartements de plus de 400 mètres carrés. On les a corrigées. Les autres ne sont pas des erreurs. La dernière ligne fait peur, 66 % de surfaces manquantes, mais ce sont des ventes de terrains nus ou de dépendances : elles n'ont tout simplement pas de surface bâtie. Sur les maisons et appartements, le taux tombe à 0 %. »

**Transition (passage à Louis) :** « Louis va vous montrer deux fausses alertes, puis ce qu'on a corrigé. »

### Diapo 12 — Deux fausses alertes (1 min, Louis)

**Message clé :** deux intuitions naïves se sont révélées fausses.

**À dire :** « Première fausse alerte : en calculant le prix au mètre carré ligne par ligne, on obtient jusqu'à 566 000 euros le mètre carré. En réalité, quand une vente porte sur plusieurs lots, DVF répète le prix total sur chaque ligne. Il faut donc regrouper par vente avant de diviser. Deuxième fausse alerte : on pourrait croire que deux DPE à la même adresse et la même date sont des doublons. Mais un immeuble peut avoir des centaines de logements diagnostiqués le même jour, jusqu'à 869 ici. Chaque DPE a son propre numéro : ce ne sont pas des doublons. »

### Diapo 13 — Les deux corrections (1 min, Louis)

**Message clé :** on remplace le faux par NULL plutôt que par une valeur inventée.

**À dire :** « Les deux corrections tiennent en deux requêtes UPDATE. Zéro pièce est impossible pour un logement, alors que c'est normal pour une dépendance, qu'on ne touche pas. Un appartement de plus de 400 mètres carrés, c'est très probablement la surface de tout l'immeuble saisie par erreur. Dans les deux cas, on met la valeur à NULL. Pourquoi pas la moyenne ? Parce qu'on ne connaît pas la vraie valeur, et inventer un chiffre fausserait les calculs futurs. Un NULL dit simplement : on ne sait pas. »

### Diapo 14 — Ne pas corriger est aussi une décision (1 min 15, Louis)

**Message clé :** rare ne veut pas dire faux.

**À dire :** « C'est le point le plus important de ce TP : corriger n'est pas toujours la bonne réponse. Les années de construction avant 1700 : il existe de vieux bâtiments en Loire-Atlantique, rien ne prouve que ce soit faux. Les prix au-dessus de 15 000 euros le mètre carré : chaque valeur est plausible, on les exclut simplement des moyennes. Les 34 % d'années manquantes : c'est trop pour les remplacer sans biais, et la période de construction, complète à 100 %, suffit pour nos analyses. Enfin, les surfaces vides des terrains nus sont normales : on filtre dans la requête, pas dans la table. »

### Diapo 15 — Avant / après (45 s, Louis)

**Message clé :** les corrections sont ciblées, rien d'autre n'a bougé.

**À dire :** « Après le nettoyage, on relance exactement le même script d'audit. Les deux anomalies corrigées passent à zéro, et tous les autres indicateurs restent identiques. On a modifié 80 lignes sur plus de 430 000, sans effet de bord. »

**Transition :** « Pour conclure… »

## Conclusion

### Diapo 16 — Une réponse fondée sur des données vérifiées (1 min, Louis)

**À dire :** « Pour répondre à notre question de départ : oui, un lien apparaît entre prix et performance énergétique. Les communes chères, sur le littoral et à Nantes, ont moins de passoires que les communes rurales. Mais c'est une corrélation, et la localisation compte beaucoup. Côté audit, les données sont fiables : très peu d'erreurs réelles, 80 lignes corrigées, et chaque décision est justifiée. La leçon qu'on retient : une valeur rare n'est pas forcément fausse. La limite de notre travail, c'est que l'audit est ponctuel alors que le flux temps réel continue d'arriver. La suite logique serait d'intégrer ces contrôles directement dans le job Spark du TP2. Merci pour votre attention, nous sommes prêts pour vos questions. »

## Questions probables du jury

| Question | Réponse courte |
| --- | --- |
| Pourquoi le seuil de 15 000 €/m² ? | Environ 1,7 fois le 99e percentile observé (≈ 8 800 €/m²). La marge est large pour ne pas signaler le haut de gamme légitime du littoral. Attention : le commentaire de sql/07 dit « trois fois », ce qui est faux. |
| Pourquoi 400 m² pour un appartement ? | Les plus grands appartements individuels du marché dépassent rarement 300 à 400 m². Au-delà, c'est très probablement la surface de l'immeuble. |
| Pourquoi NULL plutôt que supprimer la ligne ? | Le reste de la ligne est juste (prix, commune, étiquette). Supprimer ferait perdre de l'information valide pour une seule valeur fausse. |
| Pourquoi ne pas remplacer par la moyenne ? | On ne connaît pas la vraie valeur. Une valeur inventée fausserait les moyennes et les répartitions futures. |
| Pourquoi ne pas imputer les 34 % d'années manquantes ? | Le volume est trop grand pour le faire sans biais. La période de construction, complète à 100 %, suffit pour nos analyses. |
| Pourquoi relier DVF et DPE par la commune ? | Il n'existe pas de clé fiable au niveau du logement : DVF identifie une parcelle, le DPE une adresse. |
| Pourquoi 350 182 DPE dans Metabase et 351 959 ailleurs ? | La capture a été prise pendant le rejeu du flux. Une fois le rejeu terminé, la table contient les 351 959 lignes. |
| Où est la part de G dans Metabase ? | Metabase regroupe A et G dans « Other » (4,01 %). C'est pour ça que la diapo n'affiche que le F. |
| Comment rejouer l'audit ? | docker compose up applique les corrections automatiquement. À la main : sql/07 (audit), sql/08 (nettoyage), puis sql/07 à nouveau. |
| Quelle est la principale limite ? | L'audit est ponctuel : les données qui arrivent par le flux après le nettoyage ne sont pas contrôlées. Il faudrait intégrer les contrôles au job Spark. |
