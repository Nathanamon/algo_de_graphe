from django.shortcuts import render
from django.http import JsonResponse
import json
import ast
import numpy as np

# Importation de tes algorithmes situés dans le même dossier
from . import dijkstra, bellmanford, Floyd_Warshall, Matrice, MethodePert

def index(request):
    """Affiche la page principale avec la matrice par défaut."""
    # On prépare les données par défaut pour le JS
    # .tolist() est nécessaire car JSON ne comprend pas les tableaux numpy
    context = {
        'default_matrix': json.dumps(Matrice.M.tolist()),
        'default_villes': json.dumps(Matrice.villes)
    }
    return render(request, 'index.html', context)

def calculer(request):
    """API qui reçoit les données du graphe et renvoie le résultat de l'algo."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            algo = data.get('algo')
            depart = data.get('depart')
            arrivee = data.get('arrivee')
            
            # Récupération et nettoyage des données brutes
            raw_matrix = data.get('matrix')
            raw_labels = data.get('labels')

            # Conversion string -> structure Python
            # ast.literal_eval est plus sûr que eval()
            matrix = ast.literal_eval(raw_matrix)
            labels = raw_labels.split(',')
            labels = [l.strip() for l in labels] # Enlever les espaces inutiles

            resultat = {}
            path_nodes = [] # Liste des villes à colorier en rouge

            # --- AIGUILLAGE DES ALGORITHMES ---
            
            if algo == 'dijkstra':
                # Appel de ta fonction modifiée
                res = dijkstra.dijkstra(depart, arrivee, matrix=matrix, labels=labels)
                
                if isinstance(res, dict):
                    resultat = res
                    # Si le chemin est "A -> B -> C", on veut ['A', 'B', 'C']
                    path_nodes = res['chemin'].split(' -> ')
                else:
                    resultat = {'message': res} # Cas d'erreur (ex: pas de chemin)

            elif algo == 'bellman':
                res = bellmanford.bellman_ford(depart, matrix=matrix, labels=labels)
                
                # Si c'est un cycle (liste de villes)
                if isinstance(res, list) and isinstance(res[0], str): # Adaptation selon ton retour bellman
                     path_nodes = res
                     resultat = {'message': "Cycle négatif détecté !", 'cycle': " -> ".join(res)}
                
                # Si c'est une liste de distances (cas normal sans cycle)
                elif isinstance(res, list):
                    try:
                        idx_arr = labels.index(arrivee)
                        dist = res[idx_arr]
                        resultat = {
                            'distance_totale': dist, 
                            'message': f"Distance min de {depart} à {arrivee}"
                        }
                        # Note: Bellman-Ford classique ne reconstruit pas le chemin facilement sans modif,
                        # donc on ne colorie rien ou juste départ/arrivée pour l'instant.
                    except ValueError:
                         resultat = {'error': "Ville d'arrivée inconnue"}
                else:
                    resultat = {'message': res}

            # Tu pourras ajouter ici les blocs pour Floyd-Warshall, PERT, etc.

            return JsonResponse({
                'status': 'success',
                'result': resultat,
                'path': path_nodes
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)