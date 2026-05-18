"""
Fichier de configuration pour l'installation du package.
Permet d'installer le package avec pip.
"""

from setuptools import setup, find_packages

# Informations du package
setup(
    name="poultry-farm-model",           # Nom du package sur PyPI
    version="1.0.0",                     # Version
    author="Université de Bertoua",      # Auteur
    description="Modélisation mathématique d'une ferme avicole",  # Description courte
    package_dir={"": "src"},             # Dossier contenant le code source
    packages=find_packages(where="src"), # Trouve automatiquement les packages
    python_requires=">=3.8",             # Version minimale de Python
    install_requires=[                   # Dépendances nécessaires
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
)