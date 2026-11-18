# Analyse BTC

Skill Claude pour suivre le bitcoin en investisseur particulier : DCA modulé par le régime de marché, alarme de vente, scénarios à 7 jours et trading de range à blanc. Chaque règle a été backtestée sans biais d'anticipation (seules les données antérieures à chaque date sont utilisées).

*English summary: a Claude skill (in French) for a retail bitcoin investor. Regime-based DCA, a Pi Cycle sell alarm, 7-day scenarios and paper range trading. Every rule is backtested without look-ahead bias. Critiques and pull requests welcome.*

**Ce n'est pas un conseil en investissement.** Les backtests couvrent deux à quatre cycles seulement ; les résultats passés ne garantissent rien.

## Ce que la méthode sait faire, et ce qu'elle ne sait pas

| Composant | Règle | Résultat du backtest |
|---|---|---|
| DCA par régime | x1,5 si le MVRV est sous son 20e percentile sur 4 ans, x0,5 au-dessus du 80e ou sous la SMA200, x1 sinon | Coût par BTC -8,5 % vs DCA constant (fenêtres de 2 ans, 2018-2024), sur les deux sous-périodes |
| Alarme de vente | Pi Cycle Top (MM111 > 2 x MM350) : vendre 25 %, racheter en zone d'accumulation | Jamais derrière l'achat-garde de 2016 à 2026, mais gain faible (+1 % sur 2021-2026) et aucun signal en 2024-2025 |
| Jeu de scénarios 7 jours | Simulation de premier franchissement sur la volatilité 30 jours | À peine meilleur que la statistique historique (Brier 0,479 contre 0,489) |
| Range (à blanc) | Efficiency ratio < 0,25 et clôture sous la bande de Bollinger basse | Non concluant : perdant 2016-2020, légèrement gagnant 2021-2026 |
| Règles rejetées | Paliers de vente sur le MVRV, sortie de tendance, filtre de cassure, DCA en paliers | Ne tiennent pas hors de la période de réglage |

Aucun indicateur testé n'annonce les retournements de cycle. Le détail est en annexe B du [SKILL.md](skill/analyse-btc/SKILL.md) et dans [docs/backtest-sorties.md](docs/backtest-sorties.md).

## Contenu du dépôt

- `skill/analyse-btc/SKILL.md` : la méthode (procédure, sources, format du bilan, résultats des backtests, script en annexe).
- `skill/analyse-btc/scripts/btc_calc.py` : tous les calculs (régime, probabilités, Bollinger, efficiency ratio, Pi Cycle). `selftest.py` le vérifie.
- `evals/` : quatre cas de test au format skill-creator (données, consigne, critères de réussite).
- `backtests/` : les scripts de backtest (voir [backtests/README.md](backtests/README.md)).
- `docs/` : rapports.

## Utiliser le skill

1. Copier le dossier `skill/analyse-btc` dans vos skills Claude (Claude Code : `~/.claude/skills/analyse-btc`) ou l'importer comme skill dans l'application Claude.
2. Remplacer les identifiants Google Drive entre chevrons dans `SKILL.md` par les vôtres (dossiers Investissement, Bilans, Journal ; document Situation ; classeur Portefeuille). Le cadre chiffré (`BTC_vN.md`) et les leçons sont lus sur Drive.
3. Connecteurs utilisés : CoinGecko, CoinMarketCap, Crypto.com, Google Drive et Google Sheets.
4. Vérifier le script : `python3 skill/analyse-btc/scripts/selftest.py` doit répondre `OK` (Python 3 et numpy).

## Contribuer

Les critiques sont le but de ce dépôt.

- **Une erreur, une faiblesse, un biais** : ouvrir une *issue* en décrivant le problème et, si possible, comment le vérifier.
- **Une amélioration** : proposer une *pull request*. Toute règle nouvelle ou modifiée doit être backtestée sans biais d'anticipation, réglée sur une période et testée sur une autre (par exemple 2016-2020 puis 2021-2026), avec les chiffres des deux périodes. Trois corrections qui marchaient sur la période de réglage n'ont pas tenu ensuite : c'est la raison de cette règle.

Pistes ouvertes : une règle de sortie qui aurait fonctionné en 2025, des seuils MVRV à jour (les données publiques Coin Metrics s'arrêtent au 23/05/2026), un vrai test du trading de range en données intrajournalières.

## Licence

MIT, voir [LICENSE](LICENSE).
