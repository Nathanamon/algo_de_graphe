from .Matrice import villes as default_villes, M as default_M

def floyd_warshall(matrix=None, labels=None):
    """
    Exécute l'algorithme de Floyd-Warshall.
    Si matrix et labels ne sont pas fournis, utilise ceux de Matrice.py.
    """
    # 1. Gestion des valeurs par défaut
    if matrix is None:
        matrix = default_M
    if labels is None:
        labels = default_villes

    n = len(labels)
    # Initialisation de la matrice des distances
    # On crée une copie pour ne pas modifier la matrice originale si c'est une liste de listes
    dist = [[float('inf')] * n for _ in range(n)]
    
    for i in range(n):
        dist[i][i] = 0
        for j in range(n):
            # On vérifie > 0 pour s'assurer qu'il y a une arête (et éviter les INF si présents dans matrix)
            # Attention : matrix peut être numpy ou liste de listes
            if matrix[i][j] > 0 and matrix[i][j] != float('inf'):
                dist[i][j] = matrix[i][j]

    # Algorithme principal (3 boucles imbriquées)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist