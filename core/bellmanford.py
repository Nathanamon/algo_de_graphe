try:
    from .Matrice import villes as default_villes, M as default_M
except ImportError:
    # Fallback pour exécution standalone (tests)
    import numpy as np
    default_villes = ["Rennes","Caen","Paris","Nantes","Bordeaux","Lille","Dijon","Nancy","Grenoble","Lyon"]
    INF = np.inf
    default_M = np.array([
        [  0,  75, 110,  45, 130, INF, INF, INF, INF, INF],
        [ 75,   0,  50, INF, INF,  65, INF, INF, INF, INF],
        [110,  50,   0,  80, 150,  70,  60, INF, INF, INF],
        [ 45, INF,  80,   0,  90, INF, INF, INF, INF, INF],
        [130, INF, 150,  90,   0, INF, INF, INF, INF, 100],
        [INF,  65,  70, INF, INF,   0, 120, 100, INF, INF],
        [INF, INF,  60, INF, INF, 120,   0,  75,  75,  70],
        [INF, INF, INF, INF, INF, 100,  75,   0,  80,  90],
        [INF, INF, INF, INF, INF, INF,  75,  80,   0,  40],
        [INF, INF, INF, INF, 100, INF,  70,  90,  40,   0]
    ])


def bellman_ford(ville_depart, matrix=None, labels=None):
    """
    Algorithme de Bellman-Ford pour le calcul des plus courts chemins.
    
    Permet de détecter les cycles de poids négatif et de calculer les distances
    minimales depuis un sommet source vers tous les autres sommets, même en
    présence d'arêtes de poids négatif.
    
    Args:
        ville_depart (str): Nom de la ville de départ
        matrix (list[list[float]], optional): Matrice d'adjacence. 
            Si None, utilise la matrice par défaut.
        labels (list[str], optional): Liste des noms de villes.
            Si None, utilise les labels par défaut.
    
    Returns:
        dict: Dictionnaire contenant soit :
            - En cas de cycle négatif : {'type': 'cycle', 'cycle': list[str]}
            - En cas de succès : {
                'type': 'distances',
                'distances': list[float],
                'predecesseurs': list[int],
                'distances_dict': dict[str, float]
              }
            - En cas d'erreur : {'error': str}
    
    Complexity:
        Temps : O(V × E) où V = nombre de sommets, E = nombre d'arêtes
        Espace : O(V)
    
    Example:
        >>> result = bellman_ford("Paris")
        >>> print(result['distances_dict'])
        {'Paris': 0, 'Lyon': 130, 'Bordeaux': 150, ...}
    """
    # 1. Gestion des valeurs par défaut
    if matrix is None:
        matrix = default_M
    if labels is None:
        labels = default_villes

    n = len(labels)
    
    # 2. Validation de la ville de départ
    try:
        src = labels.index(ville_depart)
    except ValueError:
        return {
            "error": f"Ville de départ inconnue : '{ville_depart}'. "
                    f"Villes disponibles : {', '.join(labels)}"
        }

    # 3. Initialisation des structures de données
    distances = [float('inf')] * n
    distances[src] = 0
    predecesseurs = [-1] * n  # -1 signifie "pas de prédécesseur"

    # 4. Construction de la liste d'arêtes
    # On extrait toutes les arêtes valides du graphe
    aretes = []
    for i in range(n):
        for j in range(n):
            poids = matrix[i][j]
            # Une arête est valide si elle n'est ni nulle ni infinie
            # On accepte les poids négatifs (c'est le but de Bellman-Ford)
            if poids != 0 and poids != float('inf') and poids is not None:
                aretes.append((i, j, float(poids)))

    # 5. Relâchement des arêtes (n-1 itérations maximum)
    # Principe : À chaque itération, on améliore les distances en "relâchant"
    # toutes les arêtes. Après k itérations, on a les plus courts chemins
    # utilisant au plus k arêtes.
    for iteration in range(n - 1):
        changed = False
        
        for u, v, poids in aretes:
            # Si on peut améliorer la distance vers v en passant par u
            if distances[u] != float('inf') and distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids
                predecesseurs[v] = u
                changed = True
        
        # Optimisation : si aucune distance n'a changé, on peut arrêter
        if not changed:
            break

    # 6. Détection de cycle négatif
    # Si on peut encore améliorer une distance après n-1 itérations,
    # c'est qu'il existe un cycle négatif accessible depuis la source
    sommet_dans_cycle = None
    
    for u, v, poids in aretes:
        if distances[u] != float('inf') and distances[u] + poids < distances[v]:
            # On a trouvé un sommet affecté par un cycle négatif
            sommet_dans_cycle = v
            # On met à jour pour la reconstruction du cycle
            predecesseurs[v] = u
            break

    # 7. Reconstruction du cycle négatif (si détecté)
    if sommet_dans_cycle is not None:
        # Pour trouver le cycle, on remonte les prédécesseurs
        # jusqu'à retomber sur un sommet déjà visité
        visited = set()
        current = sommet_dans_cycle
        
        # Étape 1 : Remonter jusqu'à entrer dans le cycle
        # (on fait n remontées pour être sûr d'être dans le cycle)
        for _ in range(n):
            current = predecesseurs[current]
        
        # Étape 2 : Reconstruire le cycle
        cycle_sommets = []
        start_cycle = current
        
        while True:
            cycle_sommets.append(current)
            current = predecesseurs[current]
            if current == start_cycle:
                break
            # Sécurité : éviter boucle infinie
            if len(cycle_sommets) > n:
                break
        
        # Inverser pour avoir l'ordre correct
        cycle_sommets.reverse()
        cycle_noms = [labels[i] for i in cycle_sommets]
        
        # Calculer le poids total du cycle
        poids_cycle = 0
        for i in range(len(cycle_sommets)):
            u = cycle_sommets[i]
            v = cycle_sommets[(i + 1) % len(cycle_sommets)]
            poids_cycle += matrix[u][v]
        
        return {
            "type": "cycle",
            "cycle": cycle_noms,
            "cycle_indices": cycle_sommets,
            "poids_cycle": poids_cycle,
            "message": f"⚠️ Cycle négatif détecté de poids {poids_cycle}"
        }

    # 8. Formatage des résultats (pas de cycle négatif)
    # Création d'un dictionnaire ville -> distance pour faciliter l'affichage
    distances_dict = {}
    for i, ville in enumerate(labels):
        dist = distances[i]
        distances_dict[ville] = dist if dist != float('inf') else "∞"

    return {
        "type": "distances",
        "distances": distances,
        "predecesseurs": predecesseurs,
        "distances_dict": distances_dict,
        "ville_depart": ville_depart,
        "nombre_iterations": min(iteration + 1, n - 1) if 'iteration' in locals() else n - 1
    }


def reconstruire_chemin(ville_depart, ville_arrivee, predecesseurs, labels):
    """
    Reconstruit le chemin entre deux villes à partir du tableau des prédécesseurs.
    
    Args:
        ville_depart (str): Ville de départ
        ville_arrivee (str): Ville d'arrivée
        predecesseurs (list[int]): Tableau des prédécesseurs calculé par Bellman-Ford
        labels (list[str]): Liste des noms de villes
    
    Returns:
        dict: {'chemin': list[str], 'existe': bool, 'distance': float}
    """
    try:
        idx_depart = labels.index(ville_depart)
        idx_arrivee = labels.index(ville_arrivee)
    except ValueError as e:
        return {'existe': False, 'erreur': f"Ville inconnue : {e}"}
    
    # Vérifier qu'un chemin existe
    if predecesseurs[idx_arrivee] == -1 and idx_arrivee != idx_depart:
        return {
            'existe': False,
            'chemin': [],
            'message': f"Aucun chemin de {ville_depart} vers {ville_arrivee}"
        }
    
    # Reconstruction du chemin en remontant les prédécesseurs
    chemin_indices = []
    current = idx_arrivee
    
    while current != -1:
        chemin_indices.insert(0, current)
        if current == idx_depart:
            break
        current = predecesseurs[current]
        
        # Sécurité anti-boucle infinie
        if len(chemin_indices) > len(labels):
            return {'existe': False, 'erreur': "Erreur dans le tableau des prédécesseurs"}
    
    chemin_noms = [labels[i] for i in chemin_indices]
    
    return {
        'existe': True,
        'chemin': chemin_noms,
        'chemin_indices': chemin_indices
    }