"""
Modèle continu pour la ferme avicole
====================================

Ce fichier contient la classe principale qui implémente le modèle mathématique.
Le modèle est une EDP de transport avec deux populations : X (saine) et Y (retardée).

Schéma numérique : différences finies explicites.
"""

# Importation de NumPy pour les calculs matriciels
import numpy as np

# Importation des types pour l'annotation des fonctions (facultatif)
from typing import Dict, Tuple, List


class ContinuousPoultryModel:
    """
    Classe principale du modèle continu.

    Cette classe contient toutes les méthodes nécessaires pour :
    - initialiser le modèle avec des paramètres donnés
    - effectuer un pas de temps (évolution des populations)
    - simuler sur une période donnée
    - calculer des grandeurs économiques
    """

    # ------------------------------------------------------------
    # Constructeur : initialisation du modèle à partir des paramètres
    # ------------------------------------------------------------

    def __init__(self, params: Dict):
        """
        Constructeur : reçoit un dictionnaire de paramètres et construit le modèle.

        Paramètre
        ---------
        params : dict
            Dictionnaire créé par create_default_parameters().
            Contient toutes les fonctions et valeurs nécessaires.
        """
        # On stocke les paramètres pour pouvoir y accéder plus tard
        self.params = params

        # --- Récupération des paramètres de discrétisation ---
        # h_t : pas de temps (jours) - intervalle entre deux pas de calcul
        self.h_t = params['h_t']

        # h_m : pas en masse (kg) - intervalle entre deux valeurs de masse
        self.h_m = params['h_m']

        # h_a : pas en âge (jours) - intervalle entre deux valeurs d'âge
        self.h_a = params['h_a']

        # Bornes du domaine (valeurs minimales et maximales)
        self.a_min = params['a_min']   # Âge minimal (jours)
        self.a_max = params['a_max']   # Âge maximal (jours)
        self.m_min = params['m_min']   # Masse minimale (kg)
        self.m_max = params['m_max']   # Masse maximale (kg)

        # --- Construction de la grille en âge ---
        # Calcul du nombre de points en âge :
        # (a_max - a_min) / h_a + 1
        # Exemple : (45 - 0.01) / 1 + 1 ≈ 45 points
        self.n_a = int((self.a_max - self.a_min) / self.h_a) + 1

        # Création du tableau des valeurs d'âge (régulièrement espacées)
        # Exemple : [0.01, 1.01, 2.01, ..., 45.0]
        self.a_grid = np.linspace(self.a_min, self.a_max, self.n_a)

        # --- Construction de la grille en masse ---
        # Calcul du nombre de points en masse
        self.n_m = int((self.m_max - self.m_min) / self.h_m) + 1

        # Création du tableau des valeurs de masse
        # Exemple : [0.01, 0.21, 0.41, ..., 3.0]
        self.m_grid = np.linspace(self.m_min, self.m_max, self.n_m)

        # --- Poids de quadrature pour les intégrales (méthode des trapèzes 2D) ---
        # Ces poids servent à calculer des intégrales du type ∫∫ f(a,m) da dm
        # On commence par une matrice de 1 (poids par défaut)
        self.quad_weights = np.ones((self.n_a, self.n_m))

        # Les bords ont un poids de 0.5 (car partagés entre deux cellules)
        self.quad_weights[0, :] = 0.5      # Bord gauche (âge minimal)
        self.quad_weights[-1, :] = 0.5     # Bord droit (âge maximal)
        self.quad_weights[:, 0] = 0.5      # Bord bas (masse minimale)
        self.quad_weights[:, -1] = 0.5     # Bord haut (masse maximale)

        # Les coins sont automatiquement à 0.25 (0.5 × 0.5)
        # On multiplie par le produit des pas pour avoir la vraie intégrale
        self.quad_weights = self.quad_weights * self.h_a * self.h_m

        # --- Initialisation des populations (valeurs None pour l'instant) ---
        self.X = None   # Population saine (sera initialisée plus tard)
        self.Y = None   # Population retardée

        # --- Historique pour la visualisation ---
        # Ces listes stockeront les états successifs de la simulation
        self.history_X = []     # Liste des matrices X enregistrées
        self.history_Y = []     # Liste des matrices Y enregistrées
        self.history_times = [] # Liste des temps correspondants

    # ------------------------------------------------------------
    # Méthodes auxiliaires pour le calcul des termes physiques
    # ------------------------------------------------------------

    def compute_competition(self) -> float:
        """
        Calcule le terme de compétition C(t).

        Formule : C(t) = ∫∫ κ(a,m) × (X(t,a,m) + Y(t,a,m)) da dm

        Ce terme représente l'occupation de la ferme.
        - S'il est proche de 0 : la ferme est vide
        - S'il est proche de 1 : la ferme est saturée
        """
        # Récupération de la fonction κ (compétition) depuis les paramètres
        kappa = self.params['competition']

        # Population totale (X + Y) en chaque point de la grille
        total_pop = self.X + self.Y

        # Création d'une matrice pour stocker κ(a,m) à chaque point
        kappa_matrix = np.zeros((self.n_a, self.n_m))

        # Boucle sur tous les points de la grille pour évaluer κ
        for j in range(self.n_a):          # j : indice de l'âge
            for l in range(self.n_m):      # l : indice de la masse
                a_val = self.a_grid[j]     # Valeur de l'âge au point (j,l)
                m_val = self.m_grid[l]     # Valeur de la masse au point (j,l)
                kappa_matrix[j, l] = kappa(a_val, m_val)  # Évaluation de κ

        # Intégrale discrète : somme pondérée de κ × (X+Y)
        integrand = kappa_matrix * total_pop

        # Somme de tous les termes pondérés par les poids de quadrature
        return np.sum(self.quad_weights * integrand)

    def compute_effective_supply(self, t: float) -> float:
        """
        Calcule le nombre réel de poussins qui entrent dans la ferme.

        Formule : e_effectif(t) = e(t) × (1 - C(t))

        Où :
        - e(t) est le taux d'approvisionnement souhaité par l'éleveur
        - C(t) est la compétition (occupation de la ferme)

        Paramètre
        ---------
        t : float
            Temps courant (jours)
        """
        # Taux d'approvisionnement souhaité par l'éleveur (fonction du temps)
        e_t = self.params['supply_rate'](t)

        # Compétition actuelle (occupation de la ferme)
        competition = self.compute_competition()

        # On ne peut pas avoir un facteur négatif (max(0, ...))
        # Si competition > 1, on prend 0
        return e_t * max(0.0, 1.0 - competition)

    def advection_age(self, U: np.ndarray, j: int, l: int) -> float:
        """
        Calcule la dérivée partielle ∂U/∂a au point (j, l).

        C'est le terme de vieillissement. Les poulets avancent en âge.
        On utilise un schéma aux différences finies :
        - Aux bords : décentré (car on n'a pas de points à gauche/droite)
        - À l'intérieur : centré (plus précis)

        Paramètres
        ----------
        U : ndarray
            Matrice de la population (X ou Y)
        j : int
            Indice en âge (ligne de la matrice)
        l : int
            Indice en masse (colonne de la matrice)
        """
        # Cas du bord gauche (âge minimal)
        if j == 0:
            # Différence avant : (U[1] - U[0]) / h_a
            return (U[1, l] - U[0, l]) / self.h_a

        # Cas du bord droit (âge maximal)
        elif j == self.n_a - 1:
            # Différence arrière : (U[-1] - U[-2]) / h_a
            return (U[-1, l] - U[-2, l]) / self.h_a

        # Cas intérieur (ni bord gauche ni bord droit)
        else:
            # Différence centrée : (U[j+1] - U[j-1]) / (2 × h_a)
            return (U[j+1, l] - U[j-1, l]) / (2 * self.h_a)

    def advection_mass(self, U: np.ndarray, j: int, l: int, gamma: float) -> float:
        """
        Calcule la dérivée partielle ∂(γU)/∂m au point (j, l).

        C'est le terme de croissance en masse. Les poulets grossissent.
        La forme ∂(γU)/∂m est plus générale que γ × ∂U/∂m.

        Paramètres
        ----------
        U : ndarray
            Matrice de la population (X ou Y)
        j : int
            Indice en âge
        l : int
            Indice en masse
        gamma : float
            Taux de croissance (γ₁ ou γ₂) au point (j, l)
        """
        # Cas du bord inférieur (masse minimale)
        if l == 0:
            # Différence avant : γ × (U[j,1] - U[j,0]) / h_m
            return gamma * (U[j, 1] - U[j, 0]) / self.h_m

        # Cas du bord supérieur (masse maximale)
        elif l == self.n_m - 1:
            # D'après l'équation (5) du PDF, γ = 0 à la masse maximale
            # Donc ∂(γU)/∂m = 0
            return 0.0

        # Cas intérieur (ni bord bas ni bord haut)
        else:
            # Différence centrée : γ × (U[j,l+1] - U[j,l-1]) / (2 × h_m)
            return gamma * (U[j, l+1] - U[j, l-1]) / (2 * self.h_m)

    # ------------------------------------------------------------
    # Méthode principale : un pas de temps
    # ------------------------------------------------------------

    def step(self, t: float):
        """
        Effectue un pas de temps (passe de l'instant t à t + h_t).

        C'est le cœur du modèle. On calcule les nouvelles populations
        X_new et Y_new à partir des populations courantes X et Y.

        Paramètre
        ---------
        t : float
            Temps courant (jours)
        """
        # --- 1. Copie des matrices pour les nouvelles valeurs ---
        # On part des valeurs courantes pour calculer les variations
        X_new = self.X.copy()
        Y_new = self.Y.copy()

        # --- 2. Pré-calcul des matrices de paramètres ---
        # Pour éviter de recalculer les mêmes valeurs à chaque point,
        # on pré-calcule des matrices une fois pour toutes.
        # C'est plus efficace (optimisation).

        # Matrice des taux de mortalité d(a)
        d_mat = np.zeros((self.n_a, self.n_m))

        # Matrice des taux de vente s(a,m)
        s_mat = np.zeros((self.n_a, self.n_m))

        # Matrice des taux de croissance γ₁(a)
        gamma1_mat = np.zeros((self.n_a, self.n_m))

        # Matrice des taux de croissance γ₂(a) = ρ × γ₁(a)
        gamma2_mat = np.zeros((self.n_a, self.n_m))

        # Boucle de remplissage des matrices
        for j in range(self.n_a):
            for l in range(self.n_m):
                # Valeur de l'âge au point (j,l)
                a_val = self.a_grid[j]

                # Valeur de la masse au point (j,l)
                m_val = self.m_grid[l]

                # Remplissage de d_mat : mortality ne dépend que de l'âge
                # On passe un seul argument : a_val
                d_mat[j, l] = self.params['mortality'](a_val)

                # Remplissage de s_mat : sale_rate dépend de a et m
                s_mat[j, l] = self.params['sale_rate'](a_val, m_val)

                # Remplissage de gamma1_mat : gamma1 ne dépend que de l'âge
                gamma1_mat[j, l] = self.params['gamma1'](a_val)

                # Remplissage de gamma2_mat : gamma2 ne dépend que de l'âge
                gamma2_mat[j, l] = self.params['gamma2'](a_val)

        # --- 3. Mise à jour pour chaque point de la grille ---
        for j in range(self.n_a):
            for l in range(self.n_m):
                # Récupération des valeurs au point (j,l)
                gamma1 = gamma1_mat[j, l]   # Taux de croissance sain
                gamma2 = gamma2_mat[j, l]   # Taux de croissance retardé
                d = d_mat[j, l]             # Taux de mortalité
                s = s_mat[j, l]             # Taux de vente

                # ----- Équation pour X (population saine) -----
                # Formule : ∂X/∂t = -∂X/∂a - ∂(γ₁X)/∂m - (d+s+ρ)X

                # Terme d'advection en âge (vieillissement)
                # Signe négatif car le terme est ∂X/∂a, mais on a -∂X/∂a
                adv_a = -self.advection_age(self.X, j, l)

                # Terme d'advection en masse (croissance)
                # Signe négatif car on a -∂(γ₁X)/∂m
                adv_m = -self.advection_mass(self.X, j, l, gamma1)

                # Terme de réaction (mortalité + vente + transfert ρ)
                # ρ est le taux de transfert X → Y
                reaction = -(d + s + self.params['rho']) * self.X[j, l]

                # Variation totale de X (dérivée temporelle)
                dXdt = adv_a + adv_m + reaction

                # Nouvelle valeur : ancienne + pas × variation (schéma d'Euler explicite)
                X_new[j, l] = self.X[j, l] + self.h_t * dXdt

                # ----- Équation pour Y (population retardée) -----
                # Formule : ∂Y/∂t = -∂Y/∂a - ∂(γ₂Y)/∂m - (d+s)Y + ρX

                adv_a_y = -self.advection_age(self.Y, j, l)
                adv_m_y = -self.advection_mass(self.Y, j, l, gamma2)
                reaction_y = -(d + s) * self.Y[j, l] + self.params['rho'] * self.X[j, l]

                dYdt = adv_a_y + adv_m_y + reaction_y
                Y_new[j, l] = self.Y[j, l] + self.h_t * dYdt

        # --- 4. Condition au bord (a_min, m_min) pour X ---
        # C'est le point où entrent les nouveaux poussins (équation 16 du PDF)
        # On traite ce point séparément car la formule est différente

        # Indices du coin en bas à gauche (âge et masse minimaux)
        j0, l0 = 0, 0

        # Valeurs des paramètres au point (0,0)
        gamma1_00 = gamma1_mat[0, 0]
        d00 = d_mat[0, 0]
        s00 = s_mat[0, 0]

        # Advection en âge : décentrée (pas de point à gauche)
        adv_a_bc = -(self.X[1, 0] - self.X[0, 0]) / self.h_a

        # Advection en masse : décentrée (pas de point en dessous)
        adv_m_bc = -gamma1_00 * (self.X[0, 1] - self.X[0, 0]) / self.h_m

        # Terme de réaction (mortalité + vente + transfert)
        reaction_bc = -(d00 + s00 + self.params['rho']) * self.X[0, 0]

        # Terme d'approvisionnement (converti en densité)
        # On divise par h_t car on ajoute ce terme à la dérivée
        supply_term = self.compute_effective_supply(t) / self.h_t

        # Variation totale au bord
        dXdt_bc = adv_a_bc + adv_m_bc + reaction_bc + supply_term

        # Nouvelle valeur au coin
        X_new[0, 0] = self.X[0, 0] + self.h_t * dXdt_bc

        # --- 5. Conditions aux limites supplémentaires ---
        # Sur le bord gauche (âge minimal), on impose X = 0 pour masse > 0
        # Car aucun poulet n'arrive avec un âge > 0 (seuls les poussins entrent)
        X_new[0, 1:] = 0.0

        # Sur le bord gauche, Y = 0 partout (y compris le coin)
        # Car les poulets retardés ne viennent jamais de l'extérieur
        Y_new[0, :] = 0.0

        # --- 6. Éviter les valeurs négatives ---
        # Par sécurité, on remplace les éventuelles valeurs négatives par 0
        # Cela peut arriver à cause des erreurs numériques
        self.X = np.maximum(X_new, 0.0)
        self.Y = np.maximum(Y_new, 0.0)

    # ------------------------------------------------------------
    # Méthodes d'initialisation et de simulation
    # ------------------------------------------------------------

    def initialize(self, initial_chicks: float = 0.0):
        """
        Initialise les populations à zéro (ferme vide) ou avec des poussins initiaux.

        Paramètre
        ---------
        initial_chicks : float
            Nombre initial de poussins (au temps t=0, au point a_min, m_min)
        """
        # Matrices de zéros (aucun poulet nulle part)
        self.X = np.zeros((self.n_a, self.n_m))
        self.Y = np.zeros((self.n_a, self.n_m))

        # Placement des poussins initiaux au point (a_min, m_min)
        # Ce point correspond à l'âge minimal et à la masse minimale
        # C'est l'endroit où entrent normalement les nouveaux poussins
        if initial_chicks > 0:
            self.X[0, 0] = initial_chicks   # Tous les poussins au même endroit

        # Vidage des historiques (pour repartir de zéro)
        self.history_X = []
        self.history_Y = []
        self.history_times = []

    def simulate(self, T: float, initial_chicks: float = 0.0, record_every: int = 10) -> Tuple[List[np.ndarray], List[np.ndarray], List[float]]:
        """
        Simule le modèle de t = 0 à t = T.

        Paramètres
        ----------
        T : float
            Durée totale de la simulation (jours)
        initial_chicks : float
            Nombre initial de poussins (au temps t=0)
        record_every : int
            Enregistre l'état toutes les 'record_every' étapes.
            Plus la valeur est grande, moins on utilise de mémoire.

        Retour
        ------
        tuple : (history_X, history_Y, times)
            - history_X : liste des matrices X enregistrées
            - history_Y : liste des matrices Y enregistrées
            - times : liste des temps correspondants
        """
        # Initialisation des populations (ferme vide + poussins initiaux)
        self.initialize(initial_chicks)

        # Enregistrement de l'état initial (t = 0)
        self.history_X.append(self.X.copy())
        self.history_Y.append(self.Y.copy())
        self.history_times.append(0.0)

        # Nombre total de pas de temps
        # Exemple : si T=45 jours et h_t=0.05, alors n_steps = 45/0.05 = 900
        n_steps = int(T / self.h_t)

        # Boucle principale de simulation
        for k in range(1, n_steps + 1):
            # Temps actuel (k-ième pas)
            t = k * self.h_t

            # Effectuer un pas de temps (mise à jour des populations)
            self.step(t)

            # Enregistrement périodique (pour la visualisation)
            # On ne sauvegarde pas tous les pas pour économiser la mémoire
            if k % record_every == 0:
                # On copie les matrices pour ne pas modifier l'historique après
                self.history_X.append(self.X.copy())
                self.history_Y.append(self.Y.copy())
                self.history_times.append(t)

        # Retourne les trois listes (pour visualisation et analyse)
        return self.history_X, self.history_Y, self.history_times

    # ------------------------------------------------------------
    # Méthodes économiques
    # ------------------------------------------------------------

    def get_economic_potential(self, X: np.ndarray, t: float) -> float:
        """
        Calcule le potentiel économique ε(t).

        Formule : ε(t) = ∫∫ Π(a,m,t) × X(t,a,m) da dm
        avec Π(a,m,t) = p_s(t) × 1_{a ≥ age_s et m ≥ m_s} - c_n(a,m)

        C'est le profit instantané (revenus - coûts) à l'instant t.

        Paramètres
        ----------
        X : ndarray
            Population saine à un instant donné
        t : float
            Temps correspondant (utilisé pour le prix de vente)

        Retour
        ------
        float : potentiel économique (FCFA)
        """
        # Récupération des seuils de commercialisation (définis par l'utilisateur)
        age_s = self.params['age_s']   # Âge minimal de vente (jours)
        m_s = self.params['m_s']       # Masse minimale de vente (kg)

        # Création de la matrice du profit unitaire Π
        profit_matrix = np.zeros((self.n_a, self.n_m))

        # Boucle sur tous les points de la grille pour calculer Π
        for j in range(self.n_a):
            for l in range(self.n_m):
                # Vérification si le poulet est commercialisable
                if self.a_grid[j] >= age_s and self.m_grid[l] >= m_s:
                    # Prix de vente à l'instant t (FCFA/poulet)
                    # Note : ici c'est une valeur constante, mais pourrait être une fonction
                    price = self.params['sale_price']

                    # Coût alimentaire à cet âge et cette masse (FCFA/jour)
                    cost = self.params['feed_cost']

                    # Profit unitaire = prix - coût
                    profit_matrix[j, l] = price - cost
                else:
                    # Pas commercialisable → profit nul
                    profit_matrix[j, l] = 0.0

        # Intégrale discrète : somme pondérée de Π × X
        integrand = profit_matrix * X

        # Somme pondérée par les poids de quadrature
        return np.sum(self.quad_weights * integrand)