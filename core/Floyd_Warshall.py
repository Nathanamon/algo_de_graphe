from .Matrice import villes as default_villes, M as default_M

def floyd_warshall(matrix=None, labels=None):
    """
    Exécute l'algorithme de Floyd-Warshall.
    Si matrix et labels ne sont pas fournis, utilise ceux de Matrice.py.
    
    Returns:
        list[list[float]]: Matrice des distances minimales entre toutes paires
    """
    # 1. Gestion des valeurs par défaut
    if matrix is None:
        matrix = default_M
    if labels is None:
        labels = default_villes

    n = len(labels)
    
    # Initialisation de la matrice des distances
    dist = [[float('inf')] * n for _ in range(n)]
    
    for i in range(n):
        dist[i][i] = 0  # Distance de i à i = 0
        for j in range(n):
            # ✅ CORRECTION : Accepter tous les poids non-nuls (y compris négatifs)
            if matrix[i][j] != 0 and matrix[i][j] != float('inf'):
                dist[i][j] = matrix[i][j]

    # Algorithme principal (3 boucles imbriquées)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # Relaxation : peut-on améliorer dist[i][j] en passant par k ?
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist