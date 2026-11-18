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
