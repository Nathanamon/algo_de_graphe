from .Matrice import villes as default_villes, M as default_M

def bfs(ville_depart, matrix=None, labels=None):
    """Parcours en Largeur (Breadth-First Search)."""
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
    parcours = []

    while queue:
        u = queue.pop(0)
        parcours.append(labels[u])

        for v in range(n):
            # Si il y a une arête et que le noeud n'est pas visité
            if matrix[u][v] != 0 and matrix[u][v] != float('inf') and not visited[v]:
                visited[v] = True
                queue.append(v)

    return parcours

def dfs(ville_depart, matrix=None, labels=None):
    """Parcours en Profondeur (Depth-First Search)."""
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    try:
        start_idx = labels.index(ville_depart)
    except ValueError:
        return {"error": f"Ville de départ inconnue : {ville_depart}"}

    n = len(labels)
    visited = [False] * n
    parcours = []

    def _dfs_recursive(u):
        visited[u] = True
        parcours.append(labels[u])
        for v in range(n):
            if matrix[u][v] != 0 and matrix[u][v] != float('inf') and not visited[v]:
                _dfs_recursive(v)

    _dfs_recursive(start_idx)
    return parcours