"""
Visualisation des résultats du modèle
======================================

Ce fichier contient plusieurs fonctions pour tracer des graphiques
à partir des résultats d'une simulation (historique des populations X et Y).

Fonctions disponibles :
- plot_populations() : courbes X(t) et Y(t)
- plot_economic_potential() : profit instantané
- plot_population_comparison() : barres comparatives
- plot_age_distribution() : histogramme des âges
- plot_mass_distribution() : histogramme des masses
- plot_combined_results() : synthèse (3 graphiques)
- plot_grid_heatmap() : carte de chaleur (grille âge×masse) à un instant t
- plot_dual_grid_heatmaps() : X et Y côte à côte
- plot_grid_at_times() : grille à plusieurs instants
- animate_grid_evolution() : animation complète
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional


def plot_populations(
    history_X: List[np.ndarray],
    history_Y: List[np.ndarray],
    times: List[float],
    save_path: Optional[str] = None
):
    """
    Trace l'évolution des populations totales X (saine) et Y (retardée).
    
    Paramètres
    ----------
    history_X, history_Y : list of ndarray
        Historiques des populations
    times : list of float
        Temps correspondants (jours)
    save_path : str, optional
        Chemin pour sauvegarder la figure
    """
    # Calcul des populations totales à chaque instant
    total_X = [np.sum(X) for X in history_X]
    total_Y = [np.sum(Y) for Y in history_Y]

    plt.figure(figsize=(10, 6))
    plt.plot(times, total_X, 'b-', linewidth=2, label='Population saine (X)')
    plt.plot(times, total_Y, 'r--', linewidth=2, label='Population retardée (Y)')
    plt.xlabel('Temps (jours)')
    plt.ylabel('Nombre de poulets')
    plt.title('Évolution des populations')
    plt.legend()
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_economic_potential(
    economic_history: List[float],
    times: List[float],
    save_path: Optional[str] = None
):
    """
    Trace l'évolution du potentiel économique (profit instantané).
    Affiche une ligne rouge à 0 (seuil) et des zones colorées.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(times, economic_history, 'g-', linewidth=2, label='Potentiel économique')
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Seuil de rentabilité')

    economic_array = np.array(economic_history)
    plt.fill_between(times, economic_array, 0,
                     where=economic_array >= 0,
                     color='green', alpha=0.3, label='Profit')
    plt.fill_between(times, economic_array, 0,
                     where=economic_array < 0,
                     color='red', alpha=0.3, label='Perte')

    plt.xlabel('Temps (jours)')
    plt.ylabel('Potentiel économique (FCFA)')
    plt.title('Évolution du potentiel économique')
    plt.legend()
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_population_comparison(
    history_X: List[np.ndarray],
    history_Y: List[np.ndarray],
    times: List[float],
    n_points: int = 10,
    save_path: Optional[str] = None
):
    """
    Compare X et Y avec des barres (quelques instants seulement).
    """
    total_X = [np.sum(X) for X in history_X]
    total_Y = [np.sum(Y) for Y in history_Y]

    # Sélection de quelques instants (n_points)
    indices = np.linspace(0, len(times) - 1, n_points, dtype=int)

    x_pos = np.arange(n_points)
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x_pos - width/2, [total_X[i] for i in indices], width,
                   label='Saine (X)', color='blue')
    bars2 = ax.bar(x_pos + width/2, [total_Y[i] for i in indices], width,
                   label='Retardée (Y)', color='red')

    ax.set_xlabel('Temps')
    ax.set_ylabel('Nombre de poulets')
    ax.set_title('Comparaison des populations')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{times[i]:.0f} j' for i in indices])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_age_distribution(
    X: np.ndarray,
    a_grid: np.ndarray,
    time: float,
    save_path: Optional[str] = None
):
    """
    Histogramme de la distribution par âge à un instant donné.
    """
    age_dist = np.sum(X, axis=1)  # Somme sur la masse

    plt.figure(figsize=(10, 6))
    plt.bar(a_grid, age_dist, width=1.0, color='blue', alpha=0.7)
    plt.xlabel('Âge (jours)')
    plt.ylabel('Nombre de poulets')
    plt.title(f'Distribution par âge à t = {time:.0f} jours')
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_mass_distribution(
    X: np.ndarray,
    m_grid: np.ndarray,
    time: float,
    save_path: Optional[str] = None
):
    """
    Histogramme de la distribution par masse à un instant donné.
    """
    mass_dist = np.sum(X, axis=0)  # Somme sur l'âge

    plt.figure(figsize=(10, 6))
    plt.bar(m_grid, mass_dist, width=0.03, color='green', alpha=0.7)
    plt.xlabel('Masse (kg)')
    plt.ylabel('Nombre de poulets')
    plt.title(f'Distribution par masse à t = {time:.0f} jours')
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_combined_results(
    model,
    history_X: List[np.ndarray],
    history_Y: List[np.ndarray],
    times: List[float],
    save_path: Optional[str] = None
):
    """
    Synthèse : 3 graphiques (populations, potentiel économique, profit cumulé).
    """
    total_X = [np.sum(X) for X in history_X]
    total_Y = [np.sum(Y) for Y in history_Y]
    economic = [model.get_economic_potential(X, t) for X, t in zip(history_X, times)]
    cumulative_profit = np.cumsum(economic) * model.h_t

    fig, axes = plt.subplots(3, 1, figsize=(12, 12))

    # 1. Populations
    axes[0].plot(times, total_X, 'b-', linewidth=2, label='Saine (X)')
    axes[0].plot(times, total_Y, 'r--', linewidth=2, label='Retardée (Y)')
    axes[0].set_ylabel('Nombre de poulets')
    axes[0].set_title('Évolution des populations')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 2. Potentiel économique
    axes[1].plot(times, economic, 'g-', linewidth=2)
    axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[1].fill_between(times, economic, 0,
                         where=np.array(economic) >= 0,
                         color='green', alpha=0.3)
    axes[1].fill_between(times, economic, 0,
                         where=np.array(economic) < 0,
                         color='red', alpha=0.3)
    axes[1].set_ylabel('Potentiel économique (FCFA)')
    axes[1].set_title('Évolution du potentiel économique')
    axes[1].grid(True, alpha=0.3)

    # 3. Profit cumulé
    axes[2].plot(times, cumulative_profit, 'purple', linewidth=2)
    axes[2].set_xlabel('Temps (jours)')
    axes[2].set_ylabel('Profit cumulé (FCFA)')
    axes[2].set_title('Profit cumulé sur la période')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


# ============================================================
# VISUALISATION DE LA GRILLE (âge × masse)
# ============================================================

def plot_grid_heatmap(
    X: np.ndarray,
    a_grid: np.ndarray,
    m_grid: np.ndarray,
    time: float,
    title: str = "Population saine",
    save_path: Optional[str] = None
):
    """
    Affiche la grille (âge, masse) sous forme de heatmap (carte de chaleur).
    Chaque cellule contient le nombre de poulets à cet âge et cette masse.
    """
    plt.figure(figsize=(12, 8))

    # Transposition pour que l'axe des masses soit vertical
    # extent = [a_min, a_max, m_min, m_max] pour bien positionner les axes
    im = plt.imshow(
        X.T,
        origin='lower',
        aspect='auto',
        extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
        cmap='viridis'
    )

    plt.colorbar(im, label='Nombre de poulets')
    plt.xlabel('Âge (jours)')
    plt.ylabel('Masse (kg)')
    plt.title(f'{title} à t = {time:.1f} jours')
    plt.grid(False)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_dual_grid_heatmaps(
    X: np.ndarray,
    Y: np.ndarray,
    a_grid: np.ndarray,
    m_grid: np.ndarray,
    time: float,
    save_path: Optional[str] = None
):
    """
    Affiche côte à côte les heatmaps de X (saine) et Y (retardée).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # X
    im1 = ax1.imshow(
        X.T,
        origin='lower',
        aspect='auto',
        extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
        cmap='Blues'
    )
    ax1.set_xlabel('Âge (jours)')
    ax1.set_ylabel('Masse (kg)')
    ax1.set_title('Population saine (X)')
    plt.colorbar(im1, ax=ax1, label='Nombre de poulets')

    # Y
    im2 = ax2.imshow(
        Y.T,
        origin='lower',
        aspect='auto',
        extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
        cmap='Reds'
    )
    ax2.set_xlabel('Âge (jours)')
    ax2.set_ylabel('Masse (kg)')
    ax2.set_title('Population retardée (Y)')
    plt.colorbar(im2, ax=ax2, label='Nombre de poulets')

    plt.suptitle(f'Répartition spatiale à t = {time:.1f} jours')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_grid_at_times(
    history_X: List[np.ndarray],
    history_Y: List[np.ndarray],
    times: List[float],
    a_grid: np.ndarray,
    m_grid: np.ndarray,
    selected_times: Optional[List[float]] = None,
    save_dir: Optional[str] = None
):
    """
    Affiche la grille à plusieurs instants sélectionnés (sous-figures).
    Par défaut, prend 4 instants bien répartis.
    """
    # Déterminer les indices à afficher
    if selected_times is None:
        indices = np.linspace(0, len(times) - 1, 4, dtype=int)
    else:
        indices = [min(range(len(times)), key=lambda i: abs(times[i] - t)) for t in selected_times]

    n_frames = len(indices)
    fig, axes = plt.subplots(2, n_frames, figsize=(4 * n_frames, 8))

    if n_frames == 1:
        axes = axes.reshape(2, 1)

    for idx, i in enumerate(indices):
        t = times[i]
        X = history_X[i]
        Y = history_Y[i]

        # X
        im1 = axes[0, idx].imshow(
            X.T,
            origin='lower',
            aspect='auto',
            extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
            cmap='Blues'
        )
        axes[0, idx].set_xlabel('Âge (jours)')
        axes[0, idx].set_ylabel('Masse (kg)')
        axes[0, idx].set_title(f'X à t = {t:.1f} j')
        plt.colorbar(im1, ax=axes[0, idx], label='Nb poulets')

        # Y
        im2 = axes[1, idx].imshow(
            Y.T,
            origin='lower',
            aspect='auto',
            extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
            cmap='Reds'
        )
        axes[1, idx].set_xlabel('Âge (jours)')
        axes[1, idx].set_ylabel('Masse (kg)')
        axes[1, idx].set_title(f'Y à t = {t:.1f} j')
        plt.colorbar(im2, ax=axes[1, idx], label='Nb poulets')

    plt.suptitle('Évolution de la répartition spatiale')
    plt.tight_layout()

    if save_dir:
        import os
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(os.path.join(save_dir, 'grid_evolution.png'), dpi=150, bbox_inches='tight')
    plt.show()


def animate_grid_evolution(
    history_X: List[np.ndarray],
    history_Y: List[np.ndarray],
    times: List[float],
    a_grid: np.ndarray,
    m_grid: np.ndarray,
    interval: int = 200,
    save_path: Optional[str] = None
):
    """
    Crée une animation de l'évolution de la grille au cours du temps.
    Nécessite matplotlib avec backend d'animation.
    """
    from matplotlib.animation import FuncAnimation

    # Calcul des valeurs max pour l'échelle de couleur
    vmax_X = max(np.max(h) for h in history_X)
    vmax_Y = max(np.max(h) for h in history_Y)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Première frame
    im1 = ax1.imshow(
        history_X[0].T,
        origin='lower',
        aspect='auto',
        extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
        cmap='Blues',
        vmin=0,
        vmax=vmax_X
    )
    ax1.set_xlabel('Âge (jours)')
    ax1.set_ylabel('Masse (kg)')
    ax1.set_title('Population saine (X)')
    plt.colorbar(im1, ax=ax1, label='Nombre de poulets')

    im2 = ax2.imshow(
        history_Y[0].T,
        origin='lower',
        aspect='auto',
        extent=[a_grid[0], a_grid[-1], m_grid[0], m_grid[-1]],
        cmap='Reds',
        vmin=0,
        vmax=vmax_Y
    )
    ax2.set_xlabel('Âge (jours)')
    ax2.set_ylabel('Masse (kg)')
    ax2.set_title('Population retardée (Y)')
    plt.colorbar(im2, ax=ax2, label='Nombre de poulets')

    time_text = fig.suptitle(f't = {times[0]:.1f} jours')

    def update(frame):
        im1.set_array(history_X[frame].T)
        im2.set_array(history_Y[frame].T)
        time_text.set_text(f't = {times[frame]:.1f} jours')
        return [im1, im2, time_text]

    anim = FuncAnimation(fig, update, frames=len(times), interval=interval, blit=True)

    if save_path:
        anim.save(save_path, writer='pillow', fps=5)
    plt.show()