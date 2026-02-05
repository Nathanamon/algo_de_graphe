import heapq
from .Matrice import villes as default_villes, M as default_M

def dijkstra(ville_depart, ville_arrive, matrix=None, labels=None):
    """
    Calcule le plus court chemin entre deux villes.
    Utilise matrix et labels s'ils sont fournis, sinon ceux de Matrice.py.
    """
    # 1. Gestion des valeurs par défaut
    if matrix is None:
        matrix = default_M
    if labels is None:
        labels = default_villes

    n = len(labels)

    # Recherche des index
    try:
        dep = labels.index(ville_depart)
        arr = labels.index(ville_arrive)
    except ValueError:
        return f"Erreur : Une des villes ({ville_depart}, {ville_arrive}) n'existe pas dans la liste des labels."

    # Initialisation
    distances = [float('inf')] * n
    distances[dep] = 0
    predecesseurs = [-1] * n
    
    # File de priorité : (distance, index_ville)
    file_prioritaire = [(0, dep)]

    while file_prioritaire:
        dist_actuelle, u = heapq.heappop(file_prioritaire)

        # Si on a déjà trouvé un chemin plus court, on ignore
        if dist_actuelle > distances[u]:
            continue
            
        # Si on a atteint la destination (Optimisation)
        if u == arr:
            break

        # Exploration des voisins
        for v in range(n):
            poids = matrix[u][v]
            # On vérifie que le poids est positif et n'est pas infini
            if poids > 0 and poids != float('inf'): 
                distance = dist_actuelle + poids
                
                # Si un chemin plus court est trouvé
                if distance < distances[v]:
                    distances[v] = distance
                    predecesseurs[v] = u
                    heapq.heappush(file_prioritaire, (distance, v))

    # Reconstruction du chemin 
    if distances[arr] == float('inf'):
        return f"Aucun chemin entre {ville_depart} et {ville_arrive}"

    chemin = []
    etape = arr
    while etape != -1:
        chemin.insert(0, labels[etape])
        etape = predecesseurs[etape]

    return {
        "chemin": " -> ".join(chemin),
        "distance_totale": distances[arr]
    }