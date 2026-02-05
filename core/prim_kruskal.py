from .Matrice import villes as default_villes, M as default_M
import heapq

def prim(ville_depart, matrix=None, labels=None):
    """Algorithme de Prim pour l'Arbre Couvrant Minimum (MST)."""
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    try:
        start_node = labels.index(ville_depart)
    except ValueError:
        return {"error": f"Ville inconnue: {ville_depart}"}

    n = len(labels)
    visited = [False] * n
    min_heap = [(0, start_node, -1)]  # (poids, noeud_actuel, parent)
    mst_edges = []
    total_weight = 0

    while min_heap:
        weight, u, parent = heapq.heappop(min_heap)

        if visited[u]:
            continue

        visited[u] = True
        if parent != -1:
            mst_edges.append((labels[parent], labels[u]))
            total_weight += weight

        for v in range(n):
            w = matrix[u][v]
            if w != 0 and w != float('inf') and not visited[v]:
                heapq.heappush(min_heap, (w, v, u))

    return {"edges": mst_edges, "weight": total_weight}

def kruskal(matrix=None, labels=None):
    """Algorithme de Kruskal pour l'Arbre Couvrant Minimum."""
    if matrix is None: matrix = default_M
    if labels is None: labels = default_villes

    n = len(labels)
    edges = []
    # Récupérer toutes les arêtes
    for i in range(n):
        for j in range(i + 1, n): # Triangle supérieur pour ne pas doublonner
            w = matrix[i][j]
            if w != 0 and w != float('inf'):
                edges.append((w, i, j))
    
    # Trier par poids
    edges.sort()

    parent = list(range(n))
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    mst_edges = []
    total_weight = 0

    for w, u, v in edges:
        if union(u, v):
            mst_edges.append((labels[u], labels[v]))
            total_weight += w

    return {"edges": mst_edges, "weight": total_weight}