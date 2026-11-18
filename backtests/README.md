# Backtests

Scripts de travail, gardés tels qu'ils ont servi pour que les résultats soient vérifiables. Règle commune : pour une décision à la date i, seules les données jusqu'à i sont utilisées ; l'exécution se fait à la clôture suivante quand c'est précisé.

## Données

Fichier quotidien Coin Metrics (prix et MVRV), arrêté au 23/05/2026 :

```
mkdir -p data
curl -L -o data/btc_cm.csv https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv
pip install numpy pandas
```

## Scripts

| Script | Ce qu'il teste | Commande (depuis `backtests/`) |
|---|---|---|
| `backtest.py`, `backtest_core.py` | Cadre v3 : jeu 7 jours, structurel 4 semaines, DCA, trades | `python3 backtest.py ../data/btc_cm.csv out` |
| `analyse.py` | Calibration et Brier à partir des sorties de `backtest.py` | `python3 analyse.py out` |
| `moments.py` | Le jeu 7 jours aux sommets, creux et krachs | `python3 moments.py` (après `backtest.py ... out`) |
| `variantes.py`, `v4.py` | Variantes du jeu (réglage 2018-2022, test 2023-2026) et cadre v4 | `python3 v4.py ../data/btc_cm.csv out` |
| `regimes.py` | Régimes de marché, DCA par régime, règles de détention | `python3 regimes.py ../data/btc_cm.csv` |
| `range_trading.py` | Trading de range (efficiency ratio, Bollinger) | `python3 range_trading.py ../data/btc_cm.csv` |
| `sorties.py`, `grille.py` | Règles de sortie (paliers MVRV, sortie de tendance, combinaison) : réglage 2016-2020, test 2021-2026 | `python3 grille.py ../data/btc_cm.csv` |

Limites : deux à quatre cycles, fenêtres chevauchantes, clôtures quotidiennes sans données intrajournalières, seuils et fenêtres choisis par l'auteur. Le test du Pi Cycle a été fait en session interactive ; une version scriptée serait une bonne première contribution.
