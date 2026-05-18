

---

## 📄 `README.md`

```markdown
# 🐔 Poultry Farm Model

**Modélisation mathématique de la dynamique d'une ferme avicole**  
Approche en temps continu avec deux populations (saine et retardée)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Description

Ce package implémente un **modèle mathématique** pour simuler et optimiser la gestion d'une ferme avicole. Il prend en compte :

- L'**âge** (en jours) et la **masse** (en kg) des poulets
- Deux populations : **saine (X)** et **à croissance retardée (Y)**
- La **mortalité**, les **ventes**, l'**approvisionnement** en poussins
- La **compétition** pour les ressources (capacité limite)
- L'**optimisation économique** (maximisation du profit)

Le modèle est basé sur un système d'**équations aux dérivées partielles** (EDP) de transport, résolu par un **schéma numérique aux différences finies**.

---

## 🚀 Installation

### Depuis PyPI (recommandé)

```bash
pip install poultry-farm-model
```

### Depuis GitHub (pour le développement)

```bash
git clone https://github.com/mad965/poultry-farm-model.git
cd poultry-farm-model
pip install -e .
```

---

## 📊 Utilisation rapide

```python
from poultry_farm import create_default_parameters, ContinuousPoultryModel
from poultry_farm import plot_combined_results, plot_grid_at_times

# 1. Création des paramètres par défaut
params = create_default_parameters()

# 2. Création du modèle
model = ContinuousPoultryModel(params)

# 3. Simulation sur 45 jours
X_hist, Y_hist, times = model.simulate(T=45.0)

# 4. Affichage des résultats
print(f"Population saine finale : {X_hist[-1].sum():.0f}")
print(f"Population retardée finale : {Y_hist[-1].sum():.0f}")

# 5. Visualisation
plot_combined_results(model, X_hist, Y_hist, times)
plot_grid_at_times(X_hist, Y_hist, times, model.a_grid, model.m_grid)
```

---

## 📁 Structure du package

```
poultry_farm_model/
├── src/poultry_farm/
│   ├── __init__.py           # Point d'entrée
│   ├── parameters.py         # Paramètres et fonctions biologiques
│   ├── continuous_model.py   # Cœur du modèle (schéma numérique)
│   └── visualization.py      # Fonctions de visualisation
├── examples/
│   └── basic_simulation.py   # Exemple complet
├── requirements.txt          # Dépendances
├── setup.py                  # Installation
└── README.md                 # Ce fichier
```

---

## 📈 Fonctions de visualisation disponibles

| Fonction | Description |
|----------|-------------|
| `plot_populations()` | Courbes d'évolution des populations X et Y |
| `plot_economic_potential()` | Profit instantané |
| `plot_population_comparison()` | Comparaison en barres |
| `plot_age_distribution()` | Histogramme des âges |
| `plot_mass_distribution()` | Histogramme des masses |
| `plot_combined_results()` | Synthèse (3 graphiques) |
| `plot_grid_heatmap()` | Carte de chaleur (grille âge × masse) |
| `plot_dual_grid_heatmaps()` | Comparaison X et Y côte à côte |
| `plot_grid_at_times()` | Grille à plusieurs instants |
| `animate_grid_evolution()` | Animation complète |

---

## 🧠 Modèle mathématique

### Variables d'état

- `X(t, a, m)` : densité de poulets sains
- `Y(t, a, m)` : densité de poulets à croissance retardée

avec `t` = temps (jours), `a` = âge (jours), `m` = masse (kg)

### Équations principales

```
(∂/∂t + ∂/∂a + γ₁ ∂/∂m) X = -(d + s + ρ) X
(∂/∂t + ∂/∂a + γ₂ ∂/∂m) Y = -(d + s) Y + ρ X
```

- `γ₁(a)` : taux de croissance normal (kg/jour) – polynôme donné
- `γ₂(a) = ρ × γ₁(a)` : taux de croissance retardé
- `d(a)` : mortalité (1/jour) – définie par morceaux
- `s(a,m)` : taux de vente (1/jour) 
- `ρ` : taux de ratage/transfert X → Y

---

## 📥 Paramètres personnalisables

Lors de l'appel à `create_default_parameters()`, tu peux modifier :

```python
params = create_default_parameters(
    h_t=0.05,          # pas de temps (jours)
    h_m=0.2,           # pas en masse (kg)
    h_a=1.0,           # pas en âge (jours)
    a_min=0.01,        # âge minimal (jours, >0)
    a_max=45.0,        # âge maximal (jours)
    m_min=0.01,        # masse minimale (kg, >0)
    m_max=3.0,         # masse maximale (kg)
    age_s=30.0,        # âge minimal de vente (jours)
    m_s=1.5,           # masse minimale de vente (kg)
    rho=0.05/7.0,      # taux de ratage (1/jour)
    # ... paramètres économiques
)
```

---

## 🧪 Exécution de l'exemple

```bash
cd poultry_farm_model
python examples/basic_simulation.py
```

Cela générera :
- `combined_results.png` : synthèse des résultats
- `grid_evolution.png` : évolution de la grille
- `final_dual_grid.png` : grille finale (X et Y)
- `evolution.gif` : animation complète

---

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

---

## 👥 Auteurs

- **Université de Bertoua** - Laboratoire de Mathématiques et d'Informatique


---

## 🙏 Remerciements

- Aux chercheurs du laboratoire pour leurs conseils
- Aux éleveurs avicoles du Cameroun pour leurs retours terrain

---

**Lien du projet :** [github.com/mad965/poultry-farm-model](https://github.com/mad965/poultry-farm-model)
```

---

## ✅ Ce README contient :

- Une **description claire** du projet
- Les **instructions d'installation** (PyPI et GitHub)
- Un **exemple d'utilisation** rapide
- La **structure du package**
- La **liste des fonctions de visualisation** (y compris la grille)
- Le **rappel du modèle mathématique**
- Les **paramètres personnalisables**
- La **procédure pour l'exemple**
- La **licence** et les **auteurs**

---
