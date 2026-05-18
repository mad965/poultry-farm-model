"""
Paramètres par défaut et fonctions biologiques du modèle
=========================================================

Ce fichier contient :
- Les fonctions de taux de croissance γ₁(a) et γ₂(a)
- La fonction de mortalité d(a)
- La fonction de vente s(a,m)
- La fonction create_default_parameters() qui construit le dictionnaire des paramètres

UNITÉS :
- Âge a : jours
- Masse m : kg
- Temps t : jours
- γ₁, γ₂ : kg/jour
- d, s, ρ : 1/jour
- Monnaie : FCFA (1 € = 655,96 FCFA)
"""

import math
import numpy as np

# ============================================================
# Conversion Euro → FCFA (taux de change fixe)
# ============================================================
# 1 euro = 655,96 francs CFA (environ)
EUR_TO_FCFA = 655.96


# ============================================================
# 1. Taux de croissance γ₁(a) (kg/jour) – a en jours
# ============================================================

def gamma1(a: float) -> float:
    """
    Taux de croissance normal (kg/jour) pour les poulets sains.

    Ce polynôme a été fourni directement par l'utilisateur.
    Il donne le taux de croissance en kg/jour pour un âge a en jours.

    Paramètre
    ---------
    a : float
        Âge en jours (0 < a ≤ 45)

    Retour
    ------
    float : taux de croissance en kg/jour
    """
    return (2.475851e-08 * a**4 +      # Terme en a^4 (très petit)
            -3.077103e-06 * a**3 +     # Terme en a^3
            8.117112e-05 * a**2 +      # Terme en a^2
            1.764936e-03 * a +         # Terme en a
            9.531633e-03)              # Constante (croissance à la naissance)


def gamma2(a: float, rho: float) -> float:
    """
    Taux de croissance retardé (kg/jour) pour les poulets qui ont raté leur croissance.

    Formule : γ₂(a) = ρ × γ₁(a)
    Les poulets retardés grossissent moins vite (facteur ρ < 1).

    Paramètres
    ----------
    a : float
        Âge en jours
    rho : float
        Taux de ratage (1/jour)

    Retour
    ------
    float : taux de croissance retardé en kg/jour
    """
    return rho * gamma1(a)


# ============================================================
# 2. Taux de mortalité d(a) (1/jour) – définie pour 0 < a ≤ 45
# ============================================================

def mortality(a: float) -> float:
    """
    Taux de mortalité (1/jour) - ne dépend que de l'âge a.

    Cette fonction est définie par morceaux (intervalles d'âge) :
    - 0 < a < 3  : (a+1) × 0.000275    (augmentation progressive)
    - 3 ≤ a ≤ 4  : 0.05                (pic de mortalité)
    - 4 < a ≤ 10 : -0.00075*a + 0.008  (descente vers la stabilisation)
    - 10 < a ≤ 31: 0.00005             (stabilisation basse)
    - 31 < a ≤ 45: 0.0005 × (a/5.4 + 1) (remontée lente)

    Paramètre
    ---------
    a : float
        Âge en jours (doit être dans ]0, 45])

    Retour
    ------
    float : taux de mortalité (1/jour)

    Exception
    ---------
    ValueError : si a est en dehors de l'intervalle ]0, 45]
    """
    # Vérification que l'âge est dans l'intervalle de définition
    if a <= 0 or a > 45:
        raise ValueError(f"Âge {a} hors de l'intervalle de définition de d(a) : ]0,45]")

    # Intervalle 1 : de 0 à 3 jours (augmentation progressive vers le pic)
    if a < 3:
        return (a + 1) * 0.000275

    # Intervalle 2 : de 3 à 4 jours (pic de mortalité)
    if a <= 4:
        return 0.05

    # Intervalle 3 : de 4 à 10 jours (descente vers la stabilisation)
    if a <= 10:
        return -0.00075 * a + 0.008

    # Intervalle 4 : de 10 à 31 jours (stabilisation basse)
    if a <= 31:
        return 0.00005

    # Intervalle 5 : de 31 à 45 jours (remontée lente)
    return 0.0005 * (a / 5.4 + 1)


# ============================================================
# 3. Taux de vente s(a,m) (1/jour) – avec seuils age_s et m_s
# ============================================================

def sale_rate(a: float, m: float, age_s: float, m_s: float) -> float:
    """
    Taux de vente (1/jour) pour les poulets commercialisables.

    Règles :
    - Si l'âge est inférieur à age_s OU la masse inférieure à m_s : pas de vente (0)
    - Sinon : s(a,m) = sqrt((a²+m²)/(age_s²+m_s²))

    Paramètres
    ----------
    a : float
        Âge en jours
    m : float
        Masse en kg
    age_s : float
        Âge minimal de vente (jours)
    m_s : float
        Masse minimale de vente (kg)

    Retour
    ------
    float : taux de vente (1/jour)
    """
    # Condition de seuil : on ne vend pas en dessous des seuils
    if a < age_s or m < m_s:
        return 0.0

    # Dénominateur : racine carrée de (age_s² + m_s²)
    denom = math.sqrt(age_s**2 + m_s**2)

    # Taux de vente proportionnel à l'âge et à la masse
    return math.sqrt(a**2 + m**2) / denom


# ============================================================
# 4. Fonction de création des paramètres par défaut
# ============================================================

def create_default_parameters(
    # --- Paramètres de discrétisation (grille de calcul) ---
    h_t: float = 0.05,      # Pas de temps (jours)
    h_m: float = 0.2,       # Pas en masse (kg)
    h_a: float = 1.0,       # Pas en âge (jours)
    a_min: float = 0.01,    # Âge minimal (jours) - strictement > 0
    a_max: float = 45.0,    # Âge maximal (jours) - doit être ≤ 45
    m_min: float = 0.01,    # Masse minimale (kg) - strictement > 0
    m_max: float = 3.0,     # Masse maximale (kg)

    # --- Paramètres biologiques ---
    rho: float = 0.05 / 7.0,          # Taux de ratage (1/jour)
    competition_coeff: float = 0.00015,  # Coefficient de compétition κ (1/poulet)

    # --- Paramètres de gestion ---
    supply_rate=None,                 # Fonction d'approvisionnement e(t)
    age_s: float = 30.0,              # Âge minimal de vente (jours)
    m_s: float = 1.5,                 # Masse minimale de vente (kg)

    # --- Paramètres économiques (en FCFA) ---
    fixed_cost: float = (1000.0 / 7.0) * EUR_TO_FCFA,  # Coût fixe par jour
    chick_cost: float = 2.0 * EUR_TO_FCFA,             # Coût d'un poussin
    feed_cost: float = ((0.5 + 0.1 * (30/7)) / 7) * EUR_TO_FCFA,  # Coût alimentaire
    death_cost: float = 1.0 * EUR_TO_FCFA,              # Coût à la mort
    sale_price: float = (8.0 + 0.1 * (30/7)) * EUR_TO_FCFA,  # Prix de vente

    # --- Demande du marché (poulets/jour) ---
    demand: float = 200.0 / 7.0,

    # --- Population initiale ---
    initial_chicks: float = 100.0,    # Nombre de poussins au temps t=0
):
    """
    Crée un dictionnaire contenant tous les paramètres du modèle.

    Paramètres
    ----------
    Tous les paramètres ci-dessus (avec leurs valeurs par défaut)

    Retour
    ------
    dict : dictionnaire des paramètres
    """
    # Valeur par défaut pour supply_rate si non fournie
    # Cette fonction donne 100 poussins par semaine (arrivage le lundi)
    if supply_rate is None:
        def supply_rate(t):
            return (100.0 / 7.0) if (t % 7 < 0.1) else 0.0

    # --- Construction de la grille en âge ---
    # Nombre de points en âge : (a_max - a_min) / h_a + 1
    n_a = int((a_max - a_min) / h_a) + 1
    a_grid = np.linspace(a_min, a_max, n_a)

    # --- Construction de la grille en masse ---
    n_m = int((m_max - m_min) / h_m) + 1
    m_grid = np.linspace(m_min, m_max, n_m)

    # --- Poids de quadrature (méthode des trapèzes 2D) ---
    # Ces poids servent à calculer les intégrales ∫∫ f(a,m) da dm
    w = np.ones((n_a, n_m))        # Initialisation : tous les poids à 1
    w[0, :] = 0.5                  # Bord gauche (âge minimal)
    w[-1, :] = 0.5                 # Bord droit (âge maximal)
    w[:, 0] = 0.5                  # Bord bas (masse minimale)
    w[:, -1] = 0.5                 # Bord haut (masse maximale)
    # Les coins sont déjà à 0.25 (0.5 × 0.5)
    quad_weights = w * h_a * h_m    # Multiplication par le produit des pas

    # --- Construction et retour du dictionnaire ---
    return {
        # Discrétisation
        'h_t': h_t,
        'h_m': h_m,
        'h_a': h_a,
        'n_a': n_a,
        'n_m': n_m,
        'a_min': a_min,
        'a_max': a_max,
        'm_min': m_min,
        'm_max': m_max,
        'a_grid': a_grid,
        'm_grid': m_grid,
        'quad_weights': quad_weights,

        # Fonctions biologiques
        'gamma1': gamma1,                                    # Taux de croissance normal
        'gamma2': lambda a: gamma2(a, rho),                  # Taux de croissance retardé (ρ × γ₁)
        'mortality': mortality,                              # Taux de mortalité
        'sale_rate': lambda a, m: sale_rate(a, m, age_s, m_s),  # Taux de vente
        'rho': rho,                                          # Taux de ratage / transfert
        'age_s': age_s,                                      # Âge minimal de vente (pour info)
        'm_s': m_s,                                          # Masse minimale de vente (pour info)

        # Paramètres économiques
        'fixed_cost': fixed_cost,    # Coût fixe (FCFA/jour)
        'chick_cost': chick_cost,    # Coût d'un poussin (FCFA/poussin)
        'feed_cost': feed_cost,      # Coût alimentaire (FCFA/jour)
        'death_cost': death_cost,    # Coût à la mort (FCFA/poulet)
        'sale_price': sale_price,    # Prix de vente (FCFA/poulet)

        # Demande du marché
        'demand': demand,            # Demande (poulets/jour)

        # Gestion
        'supply_rate': supply_rate,  # Taux d'approvisionnement e(t)
        'competition': lambda a, m: competition_coeff,  # Compétition κ (constant)

        # Population initiale
        'initial_chicks': initial_chicks,  # Nombre de poussins au départ
    }