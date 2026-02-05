from .Matrice import villes as default_villes, M as default_M

def bfs(ville_depart, matrix=None, labels=None):
    """
    Parcours en Largeur (BFS).
    Renvoie les arêtes de l'arbre de découverte pour un affichage correct.
    """
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    try:
        start_idx = labels.index(ville_depart)
    except ValueError:
        return {"error": f"Ville de départ inconnue : {ville_depart}"}

    n = len(labels)
    visited = [False] * n
    queue = [start_idx]
    visited[start_idx] = True
    
    parcours = []           # Ordre simple (pour info texte)
    discovery_edges = []    # Arêtes de l'arbre (pour le dessin)

    while queue:
        u = queue.pop(0)
        parcours.append(labels[u])

        for v in range(n):
            weight = matrix[u][v]
            # Si on trouve un voisin non visité
            if weight != 0 and weight != float('inf') and not visited[v]:
                visited[v] = True
                queue.append(v)
                # C'est ici qu'on capture le lien "u a découvert v"
                discovery_edges.append((labels[u], labels[v]))

    return {
        "parcours": parcours,
        "edges": discovery_edges
    }

def dfs(ville_depart, matrix=None, labels=None):
    """
    Parcours en Profondeur (DFS).
    """
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    try:
        start_idx = labels.index(ville_depart)
    except ValueError:
        return {"error": f"Ville de départ inconnue : {ville_depart}"}

    n = len(labels)
    visited = [False] * n
    parcours = []
    discovery_edges = []

    def _dfs_recursive(u):
        visited[u] = True
        parcours.append(labels[u])
        
        for v in range(n):
            weight = matrix[u][v]
            if weight != 0 and weight != float('inf') and not visited[v]:
                # On note l'arête AVANT de plonger récursivement
                discovery_edges.append((labels[u], labels[v]))
                _dfs_recursive(v)

    _dfs_recursive(start_idx)
    
    return {
        "parcours": parcours,
        "edges": discovery_edges
    }