from .Matrice import villes as default_villes, M as default_M
import copy

def bellman_ford(ville_depart, matrix=None, labels=None):
    """
    Exécute l'algorithme de Bellman-Ford.
    Détecte les cycles négatifs.
    """
    # 1. Gestion des valeurs par défaut
    if matrix is None:
        matrix = default_M
    if labels is None:
        labels = default_villes

    n = len(labels)
    try:
        src = labels.index(ville_depart)
    except ValueError:
        return f"Ville inconnue : {ville_depart}"

    # Initialisation
    distances = [float('inf')] * n
    distances[src] = 0
    predecesseurs = [-1] * n

    # Création d'une liste d'arêtes (u, v, poids)
    aretes = []
    for i in range(n):
        for j in range(n):
            # On considère qu'il y a une arête si le poids n'est pas 0 et pas infini
            # (Note: Bellman-Ford gère les poids négatifs, donc on vérifie juste != 0 et != inf)
            if matrix[i][j] != 0 and matrix[i][j] != float('inf'):
                aretes.append((i, j, matrix[i][j]))

    # Relâchement des arêtes n-1 fois
    for _ in range(n - 1):
        change = False
        for u, v, poids in aretes:
            if distances[u] != float('inf') and distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids
                predecesseurs[v] = u
                change = True
        # Petite optimisation : si rien ne change dans une itération, on peut arrêter
        if not change:
            break

    # Détection ET identification du cycle négatif
    sommet_dans_cycle = None
    for u, v, poids in aretes:
        if distances[u] != float('inf') and distances[u] + poids < distances[v]:
            sommet_dans_cycle = v
            break

    # Pas de cycle
    if sommet_dans_cycle is None:
        return distances  
    
    # Remonter pour trouver le cycle complet
    for _ in range(n):
        sommet_dans_cycle = predecesseurs[sommet_dans_cycle]
    
    # Reconstruire le cycle
    cycle_indices = [sommet_dans_cycle]
    v = predecesseurs[sommet_dans_cycle]
    while v != sommet_dans_cycle:
        cycle_indices.append(v)
        v = predecesseurs[v]
    cycle_indices.reverse()
    
    # Afficher le cycle avec les labels corrects
    noms_cycle = [labels[i] for i in cycle_indices]
    print(f"Cycle négatif trouvé : {' → '.join(noms_cycle)} → {labels[cycle_indices[0]]}")
    
    return cycle_indices