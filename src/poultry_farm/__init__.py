"""
Poultry Farm Model - Gestion optimale d'une ferme avicole
=========================================================

Ce package implémente un modèle mathématique de dynamique de population
pour une ferme avicole, avec :
- Deux populations : saine (X) et retardée (Y)
- Âge et masse comme variables d'état
- Schéma numérique aux différences finies
- Fonctions d'optimisation et de visualisation

Auteur : Université de Bertoua
Version : 1.0.0
"""

# ============================================================
# Export des fonctions principales du modèle
# ============================================================

# Fonction de création des paramètres par défaut
from .parameters import create_default_parameters

# Classe principale du modèle continu
from .continuous_model import ContinuousPoultryModel

# ============================================================
# Export des fonctions de visualisation
# ============================================================

from .visualization import (
    # Graphiques de base
    plot_populations,           # Courbes X(t) et Y(t)
    plot_economic_potential,    # Profit instantané
    plot_population_comparison,  # Comparaison en barres
    plot_age_distribution,      # Histogramme des âges
    plot_mass_distribution,     # Histogramme des masses
    plot_combined_results,      # Synthèse (3 graphiques)
    
    # Visualisation de la grille (âge × masse)
    plot_grid_heatmap,          # Carte de chaleur à un instant t
    plot_dual_grid_heatmaps,    # X et Y côte à côte
    plot_grid_at_times,         # Grille à plusieurs instants
    animate_grid_evolution,     # Animation de l'évolution
)

# ============================================================
# Métadonnées du package
# ============================================================

__version__ = "1.0.0"
__author__ = "Université de Bertoua"

# Liste des éléments exportés (bonne pratique)
__all__ = [
    # Modèle
    "create_default_parameters",
    "ContinuousPoultryModel",
    
    # Visualisation
    "plot_populations",
    "plot_economic_potential",
    "plot_population_comparison",
    "plot_age_distribution",
    "plot_mass_distribution",
    "plot_combined_results",
    "plot_grid_heatmap",
    "plot_dual_grid_heatmaps",
    "plot_grid_at_times",
    "animate_grid_evolution",
]