from .Matrice import villes as default_villes, M as default_M

def bellman_ford(ville_depart, matrix=None, labels=None):
    """
    Exécute Bellman-Ford.
    Retourne un dictionnaire avec distances, prédécesseurs, ou le cycle détecté.
    """
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    n = len(labels)
    try:
        src = labels.index(ville_depart)
    except ValueError:
        return {"error": f"Ville inconnue : {ville_depart}"}

    distances = [float('inf')] * n
    distances[src] = 0
    predecesseurs = [-1] * n

    # Liste d'arêtes
    aretes = []
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0 and matrix[i][j] != float('inf'):
                aretes.append((i, j, matrix[i][j]))

    # Relâchement
    for _ in range(n - 1):
        change = False
        for u, v, poids in aretes:
            if distances[u] != float('inf') and distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids
                predecesseurs[v] = u
                change = True
        if not change: break

    # Détection cycle négatif
    sommet_cycle = None
    for u, v, poids in aretes:
        if distances[u] != float('inf') and distances[u] + poids < distances[v]:
            sommet_cycle = v
            break

    if sommet_cycle is not None:
        # Reconstruction du cycle
        for _ in range(n): sommet_cycle = predecesseurs[sommet_cycle]
        cycle = [sommet_cycle]
        v = predecesseurs[sommet_cycle]
        while v != sommet_cycle:
            cycle.append(v)
            v = predecesseurs[v]
        cycle.reverse()
        return {"type": "cycle", "cycle": cycle}

    # Retourne les résultats complets
    return {
        "type": "distances",
        "distances": distances,
        "predecesseurs": predecesseurs
    }