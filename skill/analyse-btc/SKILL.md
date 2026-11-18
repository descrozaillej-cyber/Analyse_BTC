---
name: analyse-btc
description: Méthode d'analyse du bitcoin pour un investisseur particulier - bilan quotidien de 08h, régime de marché et multiplicateur DCA, alarme de vente Pi Cycle, jeu de scénarios 7 jours avec ré-ancrage, structurel 4 semaines, trading de range en mode Test, recommandations tranchées, avec calculs faits par script. Utiliser pour tout bilan BTC, toute question sur le prix, la tendance, un scénario, un achat, une vente, un sommet ou un top de cycle, le Pi Cycle, un DCA, une range, un bull ou bear market du bitcoin, même formulée en passant ("ça dit quoi le BTC ?", "j'achète cette semaine ?"), et avant toute modification de la méthode BTC.
---

# Analyse BTC

Ce skill encode la **méthode** (procédure, sources, calculs, garde-fous). Les **données** restent sur Google Drive : paramètres chiffrés, leçons, bilans, journal. En cas d'écart sur un paramètre, Drive prime ; en cas d'écart sur la procédure, signaler l'écart à l'utilisateur plutôt que de choisir en silence.

L'utilisateur décide seul. Claude analyse et recommande de façon tranchée ; il n'est pas conseiller agréé (une mention suffit, pas dans chaque message).

## Ce que la méthode sait faire, et ce qu'elle ne sait pas

Tout le dispositif a été backtesté sans biais d'anticipation (2016-2026, détail en annexe B). À garder en tête pour ne pas survendre :
- **Régime + DCA modulé** : seul apport mesuré et robuste. Coût moyen par BTC -8,5 % vs DCA constant, sur deux sous-périodes. Le gain vient d'acheter moins cher, pas d'investir plus : investir davantage en Prudence augmente le patrimoine final seulement parce que le bitcoin a monté sur la plupart des fenêtres testées (pari d'exposition).
- **Jeu 7 jours** : bien calibré en moyenne, mais à peine meilleur que la statistique historique (environ 70 % de range, 15 % de sortie de chaque côté). Il informe, il ne justifie pas un achat.
- **Vente** : une seule règle de sortie tient sur les deux périodes, l'alarme Pi Cycle (vendre 25 %, racheter en Accumulation). Elle ne s'est déclenchée qu'à proximité de sommets (2013, 2017, avril 2021), mais n'a pas sonné en 2024-2025 : elle peut manquer un sommet. Les paliers sur le MVRV et la sortie de tendance ont été rejetés.
- **Choc ponctuel** (hack, faillite de plateforme) : aucune règle ; un bilan quotidien arrive trop tard. La protection est la garde hors plateforme, pas une vente.
- **Retournements de cycle** : aucun indicateur testé ne les annonce. La zone basse du MVRV a précédé les creux de 1 à 6 mois (avec 34 à 46 % de baisse supplémentaire) ; la tendance confirme avec 1 à 3 mois de retard.
- **Range** : non concluant (perdant 2016-2020, légèrement gagnant 2021-2026). D'où le mode Test.

Si l'utilisateur demande une prédiction plus forte que ce que les données soutiennent, le dire franchement, puis donner ce qui est mesurable.

## Où sont les fichiers (Google Drive)

Configuration : remplacer les identifiants entre chevrons par ceux de vos propres fichiers Google Drive.

- Dossier Investissement `<ID_DOSSIER_INVESTISSEMENT>` : cadre `BTC_vN.md` (prendre la version la plus haute ; il contient les seuils de rang MVRV et le notionnel des trades à blanc), `Lecons.md` et `Lecons_ajout_*.md`, rapports de backtest.
- Dossier Bilans `<ID_DOSSIER_BILANS>` : le jeu de scénarios actif est celui du fichier le plus récent par date de création (bilan ou réancrage), en ignorant les titres contenant `_test`.
- Dossier Journal `<ID_DOSSIER_JOURNAL>` : décisions et trades à blanc.
- Situation financière (Doc) `<ID_DOC_SITUATION>` : montant de base du DCA, fonds de sécurité.
- Portefeuille (Sheet) `<ID_SHEET_PORTEFEUILLE>` : onglets Positions, Post-mortems, Paramètres.

Le connecteur Drive crée des fichiers mais ne modifie pas un .md existant : toute mise à jour est un nouveau fichier (version numérotée ou ajout daté).

## Procédure

### 1. Lire avant d'analyser
Les leçons (`Lecons*.md`), le cadre le plus récent, le jeu actif et le bilan précédent (relevé de la veille), le Journal, la Situation. Les leçons existent parce que chaque erreur listée a déjà été commise une fois.

### 2. Collecter les données
Priorité aux connecteurs, parce qu'ils sont horodatés et ne dépendent pas d'articles :
- **Relevé** : clôture de la bougie 1h Crypto.com `BTC_USDT` qui se termine à 08h00 Paris (07:00 UTC en hiver, 06:00 en été), recoupée par CoinGecko `get-coin-markets` (écart inférieur à 0,5 %). En conversation, prendre le dernier prix et donner son heure.
- **Clôtures quotidiennes** : Crypto.com `get_candlestick BTC_USDT 1D` (50 bougies ; exclure la bougie du jour, incomplète).
- **SMA200 et indicateurs** : CoinMarketCap `get_crypto_technical_analysis` id `1`.
- **Dérivés** : CoinMarketCap `get_global_crypto_derivatives_metrics` (sans horodatage : le dire).
- **Cause du mouvement** : CoinMarketCap `btc_price_move_attribution` 24h, recoupé par au moins une source web datée.
- **MVRV** : WebSearch "axeladlerjr bitcoin MVRV ratio" puis WebFetch d'une page datée ; à défaut, prix / prix réalisé daté (le prix réalisé bouge lentement, environ 54k fin 2026). Les seuils de rang du cadre viennent de Coin Metrics : si le prix réalisé implicite d'une autre source (prix / MVRV) s'écarte de plus de 3 % de celui de Coin Metrics, donner les deux bascules Accumulation et dire que les sources ne sont pas comparables (au test du 14/11 : 64 100 $ contre 66 600 $).
- **Prix en euros** : Crypto.com `get_ticker BTC_EUR`.
- **Série 365 jours (Pi Cycle)** : CoinGecko `get-coin-market-chart` id `bitcoin`, days `365` (120 points régulièrement espacés). La passer telle quelle au script (`serie_365j` : startTs, endTs, prices).
- **Web** : flux ETF, FedWatch, Polymarket, calendrier (CPI, emploi, FOMC), avec deux sources datées. WebFetch n'ouvre que des URL apparues dans un WebSearch.

Pourquoi tant de rigueur : une donnée sans heure a déjà fait présenter un prix vieux de plusieurs heures comme une "clôture". Toute donnée sans date est exclue du raisonnement et listée comme non vérifiée. Ne jamais inventer une donnée ou une source ; si une donnée manque, le dire.

### 3. Calculer avec le script
Ne pas recoder les calculs à la main : écrire un JSON d'entrée et lancer `python3 scripts/btc_calc.py entree.json`. Si le dossier `scripts/` n'existe pas (skill installé sans ses fichiers), écrire le code de l'annexe C dans `btc_calc.py` à l'identique et l'utiliser. Le script donne la volatilité 30 jours, le choc éventuel, les probabilités de base du jeu (simulation de premier franchissement), les probabilités de toucher des niveaux, l'intervalle 80 % à 4 semaines (volatilité x1,3), le régime et ses bascules, l'efficiency ratio et les bandes de Bollinger, la largeur minimale de A et le ratio Pi Cycle. Format d'entrée en tête du script. En cas de doute sur l'environnement, lancer d'abord `python3 scripts/selftest.py` s'il existe (doit répondre OK) ; sinon, vérifier l'annexe C sur les valeurs de référence qui y sont données.

### 4. Régime de marché et DCA
| Régime | Condition | DCA |
|---|---|---|
| Accumulation | MVRV sous son 20e percentile sur 4 ans | x1,5 |
| Euphorie | MVRV au-dessus de son 80e percentile | x0,5 |
| Haussier | entre les deux, prix au-dessus de la SMA200 | x1 |
| Prudence | entre les deux, prix sous la SMA200 | x0,5 |
Seuils de rang : lire le cadre sur Drive (les signaler comme datés s'ils n'ont pas été recalculés). Toujours donner les bascules chiffrées : niveau de la SMA200, prix correspondant aux rangs 20 % et 80 %. La réserve n'est pas redéployée automatiquement : la redéployer en Accumulation n'a presque rien apporté au backtest (+3,7 % de patrimoine contre +5,5 % sans redéploiement).

**Pourquoi acheter moins en Prudence alors que le prix baisse.** L'utilisateur a déjà posé la question : un prix sous la SMA200 paraît « faible ». Réponse chiffrée à donner quand le sujet revient :
- « Faible » est relatif au sommet, pas à la valeur : en Prudence le MVRV est au milieu de son historique, et les vrais creux (2018, 2020, 2022) ont eu lieu avec un MVRV de 0,69 à 0,88.
- Les jours en Prudence ont été suivis, à 180 jours, d'une baisse médiane de 14 % (42 % de cas positifs).
- Par euro investi, comparé à un DCA constant du même montant total : x0,5 +9,6 %, x1 +7,4 %, x1,5 +5,8 % (fenêtres de 2 ans, 2018-2024).
- En patrimoine total à budget fixe, x1,5 fait mieux (+8,8 % contre +5,5 %) parce qu'il investit 113 % du budget au lieu de 88 %.
Multiplicateur retenu : x0,5 (le plus performant par euro investi). L'utilisateur fixe lui-même les montants selon ses finances : donner le multiplicateur et ses raisons, sans juger le montant. Un changement de multiplicateur crée une nouvelle version du cadre.

### 5. Alarme de vente Pi Cycle (réel)
- **Alarme** : sortie `pi_cycle.alarme` du script (MM111 au-dessus de 2 x MM350), et aucune fiche Journal `*_BTC_vente_picycle.md` dans les 90 jours précédents (les moyennes peuvent se recroiser plusieurs fois en quelques jours ; en 2021, deux croisements à 3 jours d'écart).
- **Recommandation** : "Recommandation vente : vendre 25 % de la position BTC contre un stablecoin." Rappeler : non imposable en France tant qu'on ne repasse pas en euros ; risque d'émetteur et de plateforme. Condition qui changerait l'avis : aucune, la règle est mécanique ; mais dire qu'elle n'a qu'un succès hors échantillon (2021) et un raté (2025).
- **Rachat** : en régime Accumulation, réinvestir le produit de la vente en 12 achats hebdomadaires égaux ; suspendre hors Accumulation, reprendre au retour. Le DCA hebdomadaire continue selon le régime pendant ce temps (c'est ce que le backtest a simulé : vente et DCA ensemble).
- **Tenue** : à l'alarme, fiche Journal `AAAA-MM-JJ_BTC_vente_picycle.md` (actif, classe Bitcoin, enveloppe, mode Réel, date et prix, taille 25 %, thèse en deux phrases, critères remplis, scénario central et alternatif, horizon : jusqu'au rachat, invalidation, frais, benchmark : conserver le BTC). Portefeuille/Positions n'est modifié que quand l'utilisateur confirme avoir vendu, avec la quantité réelle.
- **Approximation** : sur 120 points, le ratio oscille autour de 1 pendant quelques jours près d'un croisement (avril 2021 : 1,001 puis 0,998 puis 1,001). Un seul jour à 1 ou plus suffit ; le verrou de 90 jours évite les doublons.
- **Chaque jour, hors alarme** : donner le ratio MM111 / (2 x MM350) et la hausse de la MM111 nécessaire (`hausse_mm111_pour_alarme`). Le 13/11/2026 : ratio 0,50.

### 6. Jeu tactique 7 jours
- **Résolution d'abord** : si un relevé est sorti de la range A, si une cible est atteinte, si l'échéance est passée ou si le prix est hors de toutes les conditions, le jeu est **résolu**. Le clore, noter le résultat et sa probabilité initiale (pour la calibration), puis construire un nouveau jeu le jour même. Une condition remplie n'est jamais "90 % probable" : elle est réalisée. C'est l'erreur qui a fait citer une range 74-82k avec un prix à 69k.
- **Construction** : bornes de A = premiers niveaux de structure sous et au-dessus du prix, mais jamais plus près que `largeur_min_A` du script (0,8 écart-type sur 7 jours, la largeur du backtest) ; sinon prendre le niveau suivant. Niveaux de structure : plus bas et plus hauts récents, anciennes zones de consolidation, SMA et EMA 200, retracements. Une range trop étroite donne un favori A artificiellement faible et un jeu résolu en un jour. Le prix du jour doit être dans A. B et C ont des cibles progressives : la première est le niveau le plus proche au-delà de la borne (souvent l'ancien support cassé), jamais une cible lointaine en premier.
- **Probabilités** : base du script, puis ajustements justifiés par des données datées (macro, flux, dérivés, survente), 15 points au plus au total, plafond 80 % sur 7 jours sauf événement majeur daté (hack, décision surprise). Écrire la variation vs la veille ; "inchangé" exige une phrase de justification.
- Un jeu actif non résolu plus étroit que `largeur_min_A` (créé avant la règle) est conservé tel quel jusqu'à sa résolution : ne pas changer les conditions d'un jeu en cours ; le signaler, et appliquer la largeur minimale au jeu suivant.
- Une seule invalidation, la même dans le message et dans le tableau.

### 7. Événements
Calendrier 72 h : pour chaque événement, l'attendu (consensus, FedWatch, Polymarket), ce qui est déjà intégré au prix, et l'effet conditionnel chiffré sur A, B, C. Pour un événement passé : résultat vs attendu et réaction du prix. Lister un événement sans effet n'apporte rien.

### 8. Range en mode Test
Détail des règles et de la tenue du Journal et du Portefeuille : annexe A. En résumé : signal si efficiency ratio sous 0,25 et dernière clôture sous la bande basse ; trade à blanc de 100 € (ou le notionnel du cadre) ; sortie au-dessus de la SMA20, sous le stop ou au 20e jour ; jamais d'argent réel, jamais de short. Un filtre « pas d'entrée juste après une cassure » a été testé et rejeté (pire sur les deux sous-périodes) : ne pas le réintroduire sans nouveau backtest.

### 9. Recommandations
Format : "Recommandation :" puis l'action, la taille, les niveaux et la condition qui changerait l'avis. L'utilisateur a jugé les formulations "cohérent avec" inutilisables : trancher. Ne recommander qu'une règle au backtest favorable ; sinon écrire "aucune recommandation (règle non validée)". Si le montant de base du DCA ou le fonds de sécurité ne sont pas fixés dans la Situation, le dire.

## Format du bilan quotidien

Message de 300 mots maximum (compter avec `wc -w` avant d'envoyer), en français, sans tiret cadratin (préférence de l'utilisateur), sans formule de remplissage, sans renvoi "voir fichier".

Lisibilité : l'utilisateur a trouvé la première version difficile à lire parce que des chiffres se suivaient sans ponctuation. Donc :
- une idée par ligne, chaque rubrique sur sa propre ligne avec son titre en gras ;
- chaque nombre accompagné de son unité et de ce qu'il mesure (« SMA200 : 73 081 $ », pas « 73081 ») ; espace pour les milliers, virgule décimale ;
- jamais deux nombres côte à côte sans mot ou signe entre eux ; les variations entre parenthèses avec leur signe (« A 45 % (+3 pts) ») ;
- les abréviations (ER, MVRV, SMA200) sont suivies de leur valeur et, si elle compte, de son seuil (« ER 0,37, range si < 0,25 »).

Rubriques :
1. Prix du relevé, heure, source, variation vs la veille.
2. Régime : nom, prix vs SMA200, MVRV (date) et rang, bascules chiffrées.
3. Cause du mouvement, fait distingué de l'hypothèse.
4. Calendrier 72 h avec effets conditionnels.
5. Jeu : "Jeu clos : X réalisé (proba initiale Y %). Nouveau jeu :" si ré-ancrage ; A, B, C avec probabilité (variation), condition, première cible ; biais, confiance, échéance ; "Rappel : ce jeu 7 jours bat à peine la statistique historique."
6. Structurel 4 semaines : médiane, intervalle 80 %, niveaux clés et probabilités de les toucher.
7. "Recommandation DCA :" multiplicateur du régime, puis "Pourquoi :" en une ou deux phrases (ce que disent le régime et le backtest), puis "Ce qui changerait l'avis :" avec les prix de bascule chiffrés (SMA200, rang 20 %, rang 80 %).
8. "Sortie (Pi Cycle) :" ratio et hausse nécessaire ; à l'alarme, "Recommandation vente :" en tête du message.
9. "Range (test) :" efficiency ratio, signal, trade à blanc ouvert ou clos.
10. Invalidation.

Archiver dans Bilans `AAAA-MM-JJ_bilan.md` (message, régime et entrées, jeu structuré avec base et ajustements, jeu clos et résultat, ratio Pi Cycle, état du range, relevé et sources, données non vérifiées). Un test manuel crée un seul fichier, avec `_test` dans le titre, pour ne pas polluer le jeu actif.

En conversation, même méthode et mêmes calculs, mais répondre à la question posée, plus court ; pas d'archivage sauf demande.

## Modifier la méthode

Toute règle nouvelle ou modifiée est backtestée avant adoption : données antérieures à chaque date seulement, paramètres fixés d'avance ou réglés sur une période et testés sur une autre, fenêtres chevauchantes signalées. Trois corrections qui marchaient en 2018-2022 n'ont pas tenu en 2023-2026 ; c'est pour ça que la règle existe. Données historiques : `https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv` (prix et MVRV quotidiens, arrêtées au 23/05/2026). Une erreur de méthode reconnue est consignée le jour même dans `Lecons_ajout_AAAA-MM-JJ.md` et, s'il existe, dans le projet Claude associé.

## Annexe A : range en mode Test

Pourquoi le mode Test : le backtest (2016-2026, clôtures quotidiennes) n'est pas concluant. Perdant en 2016-2020 (-52 à -60 % cumulés), légèrement gagnant en 2021-2026 (+13 à +15 %). En régime de tendance, la règle perd toujours. Les trades à blanc servent à mesurer le résultat en conditions réelles avant tout argent réel.

### Règle
- Données : clôtures quotidiennes complètes Crypto.com BTC_USDT (exclure la bougie du jour).
- Régime de range : efficiency ratio 30 jours sous 0,25 (ER = |clôture J - clôture J-30| / somme des |variations quotidiennes|).
- Signal : régime de range et dernière clôture sous la bande de Bollinger basse (SMA20 moins 2 écarts-types de population).
- Entrée à blanc au relevé, en euros (Crypto.com get_ticker BTC_EUR). Notionnel : celui du cadre sur Drive (100 € par défaut). Frais 0,1 % par côté.
- Stop : prix d'entrée moins (SMA20 - bande basse) au jour du signal, converti en euros au taux implicite BTC_EUR / BTC_USDT.
- Sortie : première clôture quotidienne au-dessus de la SMA20 du jour, ou sous le stop, ou au 20e jour.
- Un seul trade ouvert à la fois. Pas de short. En tendance, aucun trade.
- Pas de filtre de cassure : testé et rejeté (annexe B).

### Tenue des fichiers
Un trade est ouvert s'il existe une fiche `*_BTC_test_range.md` sans fiche `*_cloture.md` correspondante.

Ouverture :
1. Fiche Journal `AAAA-MM-JJ_BTC_test_range.md` : actif, classe Bitcoin, enveloppe Test, mode Test, date et prix d'entrée, taille, thèse en deux phrases, critères remplis (oui, non, inconnu), scénario central et alternatif, horizon 20 jours, invalidation (le stop), frais, benchmark (bitcoin acheté en une fois à la date d'entrée).
2. Ligne dans Portefeuille/Positions : lire l'en-tête d'abord. Colonnes saisies : ID, Mode "Test", Actif, Classe, Enveloppe "Test", Date d'entrée, Prix d'entrée, Quantité, Frais, Montant investi, Prix actuel, Date du prix, Benchmark, Statut "Ouvert", Fiche Journal. Colonnes dérivées en formules sur la ligne (séparateur point-virgule, locale fr_FR) : Valeur actuelle = Quantité x Prix actuel ; Plus-value latente = Valeur actuelle - Montant investi ; Plus-value (%) = Plus-value latente / Montant investi. Ne jamais écrire un résultat calculé à la main dans une cellule dérivée.

Chaque jour : mettre à jour Prix actuel et Date du prix de la ligne ouverte.

Clôture :
1. Fiche `AAAA-MM-JJ_BTC_test_range_cloture.md` : prix et motif de sortie, résultat en % et en R (gain divisé par le risque initial), comparaison au benchmark.
2. Positions : Statut "Clos", prix et date de sortie.
3. Post-mortems : une ligne (thèse fausse, indicateur négligé, aléa ou conforme). Si un indicateur a été négligé, proposer une modification des Critères.

## Annexe B : résultats des backtests

Données Coin Metrics quotidiennes, 2016 ou 2018 à mai 2026. Chaque décision n'utilise que les données antérieures. Rapports complets dans le dossier Investissement sur Drive (Backtest_BTC_v3, Backtest_BTC_v4, Backtest_regimes, Backtest_range, Backtest_sorties).

### Jeu tactique 7 jours (v3 mécanisée, 497 jeux)
- Prédit vs réalisé : A 62 / 69 %, B 19 / 17 %, C 19 / 14 %.
- Brier 0,479 contre 0,489 pour la simple statistique historique : gain d'environ 2 %.
- Aux 16 moments clés (sommets, creux, krachs), le favori A n'était juste que 2 fois.
- Rejeté faute de tenir hors période de réglage : correction du range, persistance après résolution, autres volatilités.

### Structurel 4 semaines
- Toucher +10 % : prédit 45,7, réalisé 45,8. Toucher -10 % : prédit 41,6, réalisé 35,3 (baisses surestimées).
- Intervalle 80 % : couverture 74 à 76 % avec la volatilité 30 jours, 81 à 83 % avec x1,3.
- Dérive conditionnelle au MVRV : rejetée (pas d'amélioration sur 2022-2026).

### Régime et DCA (fenêtres de 2 ans, 2018-2024)
- MVRV seul (rang sur 4 ans, x1,5 / x0,5) : coût par BTC -6,8 % vs DCA constant, meilleur dans 100 % des fenêtres.
- Régime (MVRV + SMA200) : -8,5 %, meilleur dans 97 % des fenêtres, 88 % du budget investi. 2018-2020 : -10,7 % ; 2021-2024 : -6,5 %.
- DCA en paliers : aucun apport (+0,2 % vs achat unique).
- Multiplicateur en Prudence (fenêtres de 2 ans 2018-2024, comparé à un DCA constant du même montant total) : x0,5 +9,6 % (meilleur 97 % des fenêtres, 88 % du budget investi), x1 +7,4 % (100 %, 100 % du budget), x1,5 +5,8 % (97 %, 113 % du budget).
- Même question en patrimoine total à budget d'épargne fixe, réserve comptée en cash : x1,5 +8,8 % (meilleur 88 %), x0,5 sans redéploiement +5,5 % (67 %), x0,5 avec réserve redéployée en Accumulation +3,7 % (63 %). L'avantage de x1,5 vient de l'exposition plus forte, pas du point d'entrée.
- Jours en Prudence 2018-2026 : rendement 180 jours médian -14 %, 42 % positif ; 39 % suivis d'une phase Accumulation dans les 90 jours.

### Indicateurs de régime (2016-2026)
- Rendement 180 jours : prix au-dessus de la SMA200 +36 % médian (71 % positif) ; en dessous +15 % (55 %) ; rang MVRV sous 20 % +56 % (80 %) ; toutes dates +31 % (65 %).
- Creux de 2018, 2020 et 2022 : MVRV 0,69 à 0,88, prix / SMA200 de 0,51 à 0,71. Sommets : rang MVRV de 84 à 100 %, avec des MVRV de sommet en baisse à chaque cycle (4,25 en 2017 ; 2,29 en 2025).
- Aucune règle de détention ne bat l'achat-garde de façon stable ; elles réduisent les grosses baisses.

### Sorties (réglage 2016-2020, test 2021-2026)
- Paliers (vendre 10 %/semaine si rang MVRV > 95 %) : +24 % en réglage, +0,1 % en test. Le sommet de 2025 n'a atteint qu'un rang de 84 %.
- Paliers dès 80 % : signe instable (-30 à +6 % en réglage, -3 à +2 % en test).
- Sortie de tendance (tout vendre sous la SMA200 dans les 180 jours après une Euphorie) : +69 % en réglage, -18 % en test (vente à 58k en juillet 2024).
- Pi Cycle (MM111 > 2 x MM350), vente de 25 %, rachat en Accumulation : jamais derrière l'achat-garde, mois par mois, sur 2016-2026 et 2021-2026 (+1 % en 2021-2026). Croisements 2013 (deux), 16/12/2017, 12/04/2021 ; aucun en 2024-2025 (ratio maximal 0,74). Indicateur publié en 2019 : seuls 2021 et 2025 sont hors échantillon.
- Version sur 120 points CoinGecko : écart moyen du ratio 0,002, mêmes croisements à 4 jours près.

### Trades
- "Long en bas de range" sans filtre : 13 % de gagnants, -0,7 à -1,4 R par trade. Suspendu.
- Range filtré (efficiency ratio < 0,25) : voir annexe A.
- Filtre « pas d'entrée si la clôture est sous le plus bas des 20 clôtures précédentes » : rejeté. 2016-2020 : 5 trades, -3,5 % en moyenne. 2021-2026 : 6 trades, cumul -5 % contre +13 % sans filtre.

Limites communes : deux à trois cycles seulement, fenêtres chevauchantes, clôtures quotidiennes sans intraday.

## Annexe C : script btc_calc.py

À écrire à l'identique dans `btc_calc.py` si le dossier `scripts/` est absent. Vérification rapide : avec les clôtures du 25/09 au 12/11/2026, il doit donner un efficiency ratio de 0,369 et une bande basse de 71 982,52 $.

```python
#!/usr/bin/env python3
"""Calculs déterministes du cadre BTC (régime, jeu 7 jours, structurel 4 semaines, range).

Usage : python3 btc_calc.py entree.json > sortie.json

Entrée (JSON) :
  closes          clôtures quotidiennes BTC/USD, de la plus ancienne à la plus récente,
                  la dernière étant la DERNIÈRE JOURNÉE COMPLÈTE (au moins 31 valeurs)
  price           prix du relevé (USD)
  sma200          moyenne 200 jours (USD), ex. CoinMarketCap get_crypto_technical_analysis
  mvrv            MVRV du jour (ou de la veille, daté)
  mvrv_p20/p80    seuils de rang du MVRV sur 4 ans (lus dans le cadre BTC_vN.md sur Drive)
  game_low/high   bornes A du jeu 7 jours (optionnel ; sinon pas de probabilités de jeu).
                  Sortie largeur_min_A : bornes à ne pas resserrer (0,8 sigma x racine(7))
  levels          niveaux pour les probabilités de toucher sur 7 et 28 jours (optionnel)
  serie_365j      alarme Pi Cycle (optionnel) : sortie brute de CoinGecko get-coin-market-chart
                  bitcoin 365, soit {"startTs": ms, "endTs": ms, "prices": [...]} (points régulièrement
                  espacés, le dernier = maintenant). Sortie pi_cycle : MM111, 2 x MM350, ratio, alarme.
  seed, n         graine et nombre de tirages (défaut 1 et 200000)

Tout est calculé à partir de ces seules entrées : pas de réseau, pas de donnée future.
"""
import json, math, sys
import numpy as np


def sigma30(closes):
    r = np.diff(np.log(np.asarray(closes, float)))[-30:]
    return float(np.std(r, ddof=1)), float(abs(r[-1]))


def first_exit(price, low, high, sig, days, n, rng):
    paths = price * np.exp(np.cumsum(rng.standard_normal((n, days)) * sig, axis=1))
    up, dn = paths > high, paths < low
    fu = np.where(up.any(1), up.argmax(1), 10**6)
    fd = np.where(dn.any(1), dn.argmax(1), 10**6)
    b, c = float(np.mean(fu < fd)), float(np.mean(fd < fu))
    return {"A": 1 - b - c, "B": b, "C": c}


def touch(price, levels, sig, days, n, rng):
    paths = price * np.exp(np.cumsum(rng.standard_normal((n, days)) * sig, axis=1))
    mx, mn = paths.max(1), paths.min(1)
    out = {}
    for lv in levels:
        out[str(lv)] = float(np.mean(mx >= lv)) if lv >= price else float(np.mean(mn <= lv))
    return out, paths[:, -1]


def efficiency_ratio(closes, n=30):
    c = np.asarray(closes, float)[-(n + 1):]
    path = np.abs(np.diff(c)).sum()
    return float(abs(c[-1] - c[0]) / path) if path > 0 else 0.0


def bollinger(closes, n=20, k=2.0):
    c = np.asarray(closes, float)[-n:]
    mid, sd = float(c.mean()), float(c.std(ddof=0))
    return mid - k * sd, mid, mid + k * sd


def regime(price, sma200, mvrv, p20, p80):
    if mvrv < p20:
        return "Accumulation", 1.5
    if mvrv > p80:
        return "Euphorie", 0.5
    return ("Haussier", 1.0) if price > sma200 else ("Prudence", 0.5)


def pi_cycle(serie):
    """MM111 / (2 x MM350) sur une série régulièrement espacée couvrant au moins 350 jours.
    Validé sur Coin Metrics : avec 120 points sur 365 jours, écart moyen du ratio 0,002 (max 0,02),
    mêmes croisements que la version quotidienne à 4 jours près (2013, 2013, 2017, 2021)."""
    v = np.asarray(serie["prices"], float)
    span = (float(serie["endTs"]) - float(serie["startTs"])) / 86400000.0
    if span < 350 or len(v) < 100:
        return {"erreur": "série trop courte : il faut au moins 350 jours (CoinGecko get-coin-market-chart days 365)"}
    age = np.linspace(span, 0, len(v))
    m111, m350 = float(v[age < 111].mean()), float(v[age < 350].mean())
    ratio = m111 / (2 * m350)
    return {"mm111": m111, "deux_mm350": 2 * m350, "ratio": ratio, "alarme": ratio >= 1,
            "hausse_mm111_pour_alarme": 2 * m350 / m111 - 1}


def main():
    d = json.load(open(sys.argv[1]))
    closes, price = d["closes"], float(d["price"])
    if len(closes) < 31:
        sys.exit("Il faut au moins 31 clôtures quotidiennes.")
    n, rng = int(d.get("n", 200000)), np.random.default_rng(int(d.get("seed", 1)))
    sig, last_move = sigma30(closes)
    shock = last_move > 2 * sig
    out = {"volatilite_30j_quotidienne": sig, "volatilite_annualisee": sig * math.sqrt(365),
           "choc_dernier_jour": shock}

    # Largeur minimale de A (règle du backtest) : chaque borne à au moins 0,8 sigma x racine(7) du prix
    w = 0.8 * sig * math.sqrt(7)
    out["largeur_min_A"] = {"borne_basse_au_plus": price * math.exp(-w), "borne_haute_au_moins": price * math.exp(w)}

    # Jeu tactique 7 jours : base = moyenne (vol, vol x1,25) seulement après un choc
    if "game_low" in d and "game_high" in d:
        lo, hi = float(d["game_low"]), float(d["game_high"])
        if not lo < price < hi:
            out["jeu_7j"] = {"erreur": "prix hors de la range A : clore le jeu et ré-ancrer avant de calculer"}
        else:
            v1 = first_exit(price, lo, hi, sig, 7, n, rng)
            res = {"vol_30j": v1}
            if lo > price * math.exp(-w) or hi < price * math.exp(w):
                res["avertissement"] = ("range A trop étroite : élargir jusqu'au niveau de structure suivant "
                                        "au-delà de largeur_min_A")
            if shock:
                v2 = first_exit(price, lo, hi, sig * 1.25, 7, n, rng)
                res["vol_x1_25"] = v2
                res["base"] = {k: (v1[k] + v2[k]) / 2 for k in v1}
            else:
                res["base"] = v1
            out["jeu_7j"] = res

    # Structurel 4 semaines : probabilités de toucher avec vol x1, intervalle 80 % avec vol x1,3
    levels = [float(x) for x in d.get("levels", [])]
    if levels:
        t7, _ = touch(price, levels, sig, 7, n, rng)
        t28, _ = touch(price, levels, sig, 28, n, rng)
        out["toucher_7j"], out["toucher_28j"] = t7, t28
    _, final = touch(price, [price], sig * 1.3, 28, n, rng)
    q10, q50, q90 = np.quantile(final, [0.1, 0.5, 0.9])
    out["structurel_28j"] = {"mediane": float(q50), "intervalle_80": [float(q10), float(q90)]}

    # Régime et DCA
    p20, p80 = float(d["mvrv_p20"]), float(d["mvrv_p80"])
    mvrv = float(d["mvrv"])
    name, mult = regime(price, float(d["sma200"]), mvrv, p20, p80)
    realized = float(d.get("realized_price", price / mvrv))
    out["regime"] = {"nom": name, "multiplicateur_dca": mult, "prix_vs_sma200": price / float(d["sma200"]) - 1,
                     "prix_realise": realized,
                     "bascules": {"sma200": float(d["sma200"]), "prix_rang_20": realized * p20,
                                  "prix_rang_80": realized * p80}}

    # Range (mode Test) : sur clôtures quotidiennes complètes
    er = efficiency_ratio(closes)
    bl, bm, bh = bollinger(closes)
    last = float(closes[-1])
    signal = er < 0.25 and last < bl
    out["range"] = {"efficiency_ratio_30j": er, "regime_range": er < 0.25, "bande_basse": bl,
                    "sma20": bm, "bande_haute": bh, "derniere_cloture": last,
                    "cloture_sous_bande_basse": last < bl, "signal_entree": signal,
                    "distance_stop_usd": bm - bl}
    if "serie_365j" in d:
        out["pi_cycle"] = pi_cycle(d["serie_365j"])
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
```
