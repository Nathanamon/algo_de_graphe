import numpy as np

INF = np.inf

#les villes de la cartographie

villes = ["Rennes","Caen","Paris","Nantes","Bordeaux","Lille","Dijon","Nancy","Grenoble","Lyon"]

#Creation de la matrice des distances entres les villes

M = np.array([
    # Re   Ca   Pa   Na   Bo   Li   Di   Na   Gr   Ly

    [  0,  75, 110,  45, 130, INF, INF, INF, INF, INF],  # Rennes
    [ 75,   0,  50, INF, INF,  65, INF, INF, INF, INF],  # Caen
    [110,  50,   0,  80, 150,  70,  60, INF, INF, INF],  # Paris
    [ 45, INF,  80,   0,  90, INF, INF, INF, INF, INF],  # Nantes
    [130, INF, 150,  90,   0, INF, INF, INF, INF, 100],  # Bordeaux
    [INF,  65,  70, INF, INF,   0, 120, 100, INF, INF],  # Lille
    [INF, INF,  60, INF, INF, 120,   0,  75,  75,  70],  # Dijon
    [INF, INF, INF, INF, INF, 100,  75,   0,  80,  90],  # Nancy
    [INF, INF, INF, INF, INF, INF,  75,  80,   0,  40],  # Grenoble
    [INF, INF, INF, INF, 100, INF,  70,  90,  40,   0]   # Lyon

])