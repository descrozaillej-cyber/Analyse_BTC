# Backtest des règles de sortie BTC (13/11/2026)

Question de départ : la méthode sait-elle dire quand vendre (sommet de cycle, choc) ?

## Méthode
- Données Coin Metrics quotidiennes (prix, MVRV), 2016 à 23/05/2026. Décision sur les données du jour, exécution à la clôture du lendemain, frais 0,1 % par ordre, ventes en stablecoin (rendement nul).
- Base de comparaison : DCA hebdomadaire selon le régime du cadre v5, sans vente (achat-garde). Mesure : patrimoine final par euro investi, et pire baisse.
- Réglage sur 2016-2020, test sur 2021-2026 avec les réglages fixés. Fenêtres de 3 ans tous les 60 jours (13 en réglage, 15 en test, chevauchantes), plus suivi mois par mois d'un investisseur continu.
- Rachat : en Accumulation (rang MVRV < 20 %) sur 4 ou 12 semaines, ou au retour au-dessus de la SMA200.

## Résultats
| Règle | Réglage 2016-2020 | Test 2021-2026 |
|---|---|---|
| Paliers : vendre 10 %/semaine si rang MVRV > 95 % | +24 % | +0,1 % (ne se déclenche presque pas) |
| Paliers dès 80 % (vente 2 à 10 %/semaine) | -30 à +6 % | -3 à +2 % (signe instable) |
| Sortie de tendance : tout vendre sous la SMA200 dans les 180 j après une Euphorie | +69 % | -18 % (vendu à 58k en juillet 2024, avant 124k) |
| Combinée | +58 % | -17 % |
| Pi Cycle Top (MM111 > 2 x MM350) : vendre 25/50/100 %, rachat en Accumulation | toujours en avance | +1 / +2 / +4 %, jamais en retard |

- Le sommet de 2025 n'a atteint qu'un rang MVRV de 84 % (124 824 $ le 06/10/2025) : les règles de paliers au-dessus de 85 % ne se sont jamais déclenchées sur ce cycle.
- Pi Cycle : croisements 06/04/2013, 05/12/2013, 16/12/2017 (jour du sommet), 12/04/2021 (59 906 $, 6 % sous le sommet d'avril ; le sommet de novembre 2021 était plus haut). Aucun croisement en 2024-2025 : aucune protection contre la baisse de 124k à 63k.
- Le Pi Cycle a été publié en 2019 avec 2013 et 2017 sous les yeux : seuls 2021 (réussi) et 2025 (manqué) sont hors échantillon.

## Conclusion
- Aucune règle de sortie testée ne repère le sommet de façon fiable. Les règles qui brillent sur 2016-2020 doivent tout au cycle 2017 et échouent ensuite.
- Le Pi Cycle est la seule règle jamais perdante sur les deux périodes, parce qu'elle se déclenche rarement et ne s'est déclenchée que près d'un sommet. Elle reste une alarme qui peut ne pas sonner (2025).
- Choc ponctuel (hack) : aucune règle testée ; un bilan quotidien est trop lent pour y réagir. Protection pertinente : garde hors plateforme.

## Comparaison avec l'existant (skills et outils publics, 13/11/2026)
- tradermonty market-top-detector : actions américaines, pas de crypto ; score heuristique, sans calibration mesurée.
- tradermonty crypto-regime-analyzer : score de risque crypto, ne donne pas de signal de vente, seuils non backtestés.
- star23 btc-bottom-model : score 0-100 sur 13 indicateurs, conseils de prise de profits au-dessus de 71 ; aucun backtest publié.
- CBBI (zaczero/cbbi, AGPL) : agrégat de 9 indicateurs de sommet ; plusieurs ont échoué en 2025 selon Bitcoin Magazine Pro (01/12/2025).
- signallord (serveur MCP) : probabilité composite de sommet, formule et validation non publiées.

Limites : 2 à 4 sommets seulement, fenêtres chevauchantes, clôtures quotidiennes.
