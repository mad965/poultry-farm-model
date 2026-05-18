"""
Exemple complet d'utilisation du package poultry-farm-model.

Ce script montre comment :
1. Définir tous les paramètres utilisateur (discrétisation, biologie, gestion, économie, demande)
2. Créer le modèle avec ces paramètres
3. Lancer une simulation
4. Visualiser les résultats (courbes, grille, animation)

Tous les paramètres sont modifiables en tête du script.
"""

# ============================================================
# IMPORTATIONS
# ============================================================

import sys
import os

# Ajout du chemin pour trouver le package (utile en développement)
# Cela permet d'importer le package depuis le dossier src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np

# Importation des fonctions depuis le package
from src.poultry_farm import (
    create_default_parameters,      # Fonction de création des paramètres
    ContinuousPoultryModel,          # Classe principale du modèle
    plot_combined_results,           # Graphique de synthèse
    plot_grid_at_times,              # Grille à plusieurs instants
    plot_dual_grid_heatmaps,         # Comparaison X et Y à un instant
    animate_grid_evolution,          # Animation complète
)


# ============================================================
# 1. DÉFINITION DES PARAMÈTRES PAR L'UTILISATEUR
# ============================================================

# --- 1.1 Paramètres de discrétisation (grille de calcul) ---
# Ces paramètres définissent la finesse de la grille et la précision des calculs

h_a = 1.0          # Pas en âge (jours) - doit être > h_m
h_m = 0.2          # Pas en masse (kg) - doit être < h_a
h_t = 0.05         # Pas de temps (jours) - doit vérifier h_t/h_a + h_t/h_m ≤ 1

a_min = 0.01       # Âge minimal (jours) - strictement > 0 (pour éviter division par zéro)
a_max = 45.0       # Âge maximal (jours) - doit être ≤ 45 pour que d(a) soit définie

m_min = 0.01       # Masse minimale (kg) - strictement > 0
m_max = 3.0        # Masse maximale (kg)

# --- 1.2 Paramètres biologiques ---

# ρ (rho) : taux de ratage / transfert X → Y (1/jour)
# 0.05 par semaine → divisé par 7 pour avoir par jour
rho = 0.05 / 7.0

# κ (kappa) : coefficient de compétition (1/poulet)
# Valeur constante ici, mais pourrait dépendre de l'âge et de la masse
competition_coeff = 0.00015

# --- 1.3 Paramètres de gestion (contrôle) ---

# e(t) : taux d'approvisionnement (poussins/jour)
# Ici : 100 poussins par semaine, arrivage le lundi (t multiple de 7)
def supply_rate(t):
    """Fonction d'approvisionnement en poussins"""
    return (100.0 / 7.0) if (t % 7 < 0.1) else 0.0

# Seuils de vente (un poulet est vendable s'il dépasse ces seuils)
age_s = 30.0       # Âge minimal de vente (jours)
m_s = 1.5          # Masse minimale de vente (kg)

# --- 1.4 Paramètres économiques (FCFA) ---

# Taux de conversion Euro → FCFA (1 € = 655,96 FCFA)
EUR_TO_FCFA = 655.96

# Coût fixe (FCFA/jour) : 1000 € par semaine → divisé par 7
fixed_cost = (1000.0 / 7.0) * EUR_TO_FCFA

# Coût d'un poussin (FCFA/poussin) : 2 € par poussin
chick_cost = 2.0 * EUR_TO_FCFA

# Coût alimentaire (FCFA/jour)
# Formule : (0.5 + 0.1 × âge_en_semaines) / 7 euros par jour
# On prend l'âge de vente (30 jours = 30/7 semaines) comme référence
feed_cost = ((0.5 + 0.1 * (30/7)) / 7) * EUR_TO_FCFA

# Coût à la mort (FCFA/poulet) : 1 € par poulet mort
death_cost = 1.0 * EUR_TO_FCFA

# Prix de vente (FCFA/poulet) : 8 € + 0.1 € par semaine d'âge
# On prend l'âge de vente (30 jours = 30/7 semaines) comme référence
sale_price = (8.0 + 0.1 * (30/7)) * EUR_TO_FCFA

# --- 1.5 Demande du marché (poulets/jour) ---
# 200 poulets par semaine → divisé par 7 pour avoir par jour
demand = 200.0 / 7.0

# --- 1.6 Population initiale ---
# Nombre de poussins présents dans la ferme au temps t = 0
initial_chicks = 100.0


# ============================================================
# 2. CRÉATION DES PARAMÈTRES POUR LE MODÈLE
# ============================================================

# Affichage de l'en-tête
print("=" * 60)
print("POULTRY FARM MODEL - SIMULATION EXEMPLE")
print("=" * 60)

print("\n1. Création des paramètres...")

# Appel de la fonction create_default_parameters avec tous les paramètres
params = create_default_parameters(
    # Discrétisation
    h_a=h_a,
    h_m=h_m,
    h_t=h_t,
    a_min=a_min,
    a_max=a_max,
    m_min=m_min,
    m_max=m_max,

    # Biologiques
    rho=rho,
    competition_coeff=competition_coeff,

    # Gestion
    supply_rate=supply_rate,    # La fonction d'approvisionnement
    age_s=age_s,
    m_s=m_s,

    # Économiques
    fixed_cost=fixed_cost,
    chick_cost=chick_cost,
    feed_cost=feed_cost,
    death_cost=death_cost,
    sale_price=sale_price,

    # Demande
    demand=demand,

    # Population initiale
    initial_chicks=initial_chicks,
)

# Affichage des informations sur la grille et les paramètres
print(f"   Grille : {params['n_a']} âges × {params['n_m']} masses")
print(f"   Pas : h_a={params['h_a']} j, h_m={params['h_m']} kg, h_t={params['h_t']} j")
print(f"   Âges : [{params['a_min']}, {params['a_max']}] jours")
print(f"   Masses : [{params['m_min']}, {params['m_max']}] kg")
print(f"   Seuils de vente : âge ≥ {params['age_s']} j, masse ≥ {params['m_s']} kg")
print(f"   ρ = {params['rho']:.6f} /jour")
print(f"   κ = {competition_coeff} (constant)")
print(f"   Population initiale : {params['initial_chicks']} poussins")


# ============================================================
# 3. CRÉATION DU MODÈLE ET SIMULATION
# ============================================================

print("\n2. Initialisation du modèle...")
model = ContinuousPoultryModel(params)

print(f"\n3. Simulation sur {params['a_max']} jours...")

# Lancement de la simulation
# T = durée totale (a_max)
# initial_chicks = nombre de poussins au départ
# record_every = on enregistre toutes les 10 étapes
X_hist, Y_hist, times = model.simulate(
    T=params['a_max'],
    initial_chicks=params['initial_chicks'],
    record_every=10
)


# ============================================================
# 4. AFFICHAGE DES RÉSULTATS NUMÉRIQUES
# ============================================================

print("\n4. Résultats numériques :")

# Population saine finale : somme de tous les éléments de la dernière matrice X
final_X = np.sum(X_hist[-1])

# Population retardée finale
final_Y = np.sum(Y_hist[-1])

# Population totale
final_total = final_X + final_Y

print(f"   Population saine finale : {final_X:.0f} poulets")
print(f"   Population retardée finale : {final_Y:.0f} poulets")
print(f"   Population totale finale : {final_total:.0f} poulets")


# ============================================================
# 5. VISUALISATION DES RÉSULTATS
# ============================================================

print("\n5. Génération des graphiques...")

# 5.1 Graphique de synthèse (3 sous-graphiques)
# - Évolution des populations X et Y
# - Potentiel économique
# - Profit cumulé
plot_combined_results(model, X_hist, Y_hist, times, save_path="combined_results.png")
print("   - combined_results.png")

# 5.2 Grille à plusieurs instants (heatmaps)
# Affiche la répartition (âge, masse) à 10, 20, 30 et 45 jours
plot_grid_at_times(
    X_hist, Y_hist, times,
    model.a_grid, model.m_grid,
    selected_times=[10, 20, 30, 45],
    save_dir="./"
)
print("   - grid_evolution.png")

# 5.3 Comparaison X et Y au dernier instant
# Deux heatmaps côte à côte (X à gauche, Y à droite)
plot_dual_grid_heatmaps(
    X_hist[-1], Y_hist[-1],
    model.a_grid, model.m_grid,
    times[-1],
    save_path="final_dual_grid.png"
)
print("   - final_dual_grid.png")

# 5.4 Animation (optionnelle, peut être lente)
# Crée un fichier GIF montrant l'évolution des heatmaps
print("\n6. Génération de l'animation (peut prendre quelques secondes)...")
animate_grid_evolution(
    X_hist, Y_hist, times,
    model.a_grid, model.m_grid,
    interval=200,
    save_path="evolution.gif"
)
print("   - evolution.gif")


# ============================================================
# 6. FIN
# ============================================================

print("\n" + "=" * 60)
print("SIMULATION TERMINÉE AVEC SUCCÈS")
print("=" * 60)