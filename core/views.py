from django.shortcuts import render
from django.http import JsonResponse
import json
import ast
import numpy as np

# Importation des algorithmes
from . import dijkstra, bellmanford, Floyd_Warshall, Matrice, MethodePert

def index(request):
    """Affiche la page principale avec la matrice par défaut."""
    # Préparation des données par défaut pour le JS
    context = {
        'default_matrix': json.dumps(Matrice.M.tolist()),
        'default_villes': json.dumps(Matrice.villes)
    }
    return render(request, 'index.html', context)

def calculer(request):
    """API qui reçoit les données du graphe et renvoie le résultat de l'algorithme."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            algo = data.get('algo')
            depart = data.get('depart', '').strip()
            arrivee = data.get('arrivee', '').strip()
            
            # Récupération et nettoyage des données brutes
            raw_matrix = data.get('matrix', '')
            raw_labels = data.get('labels', '')

            if not raw_matrix or not raw_labels:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Matrice et labels requis'
                }, status=400)

            # Conversion string -> structure Python
            # Nettoyage pour gérer 'inf' correctement
            clean_matrix = raw_matrix.replace('inf', 'float("inf")').replace('Infinity', 'float("inf")')
            
            try:
                matrix = ast.literal_eval(clean_matrix)
            except (ValueError, SyntaxError) as e:
                return JsonResponse({
                    'status': 'error',
                    'error': f'Format de matrice invalide: {str(e)}'
                }, status=400)
            
            # Traitement des labels
            labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
            
            if not labels:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Veuillez fournir au moins un label'
                }, status=400)

            # Validation: taille de la matrice doit correspondre au nombre de labels
            if len(matrix) != len(labels) or any(len(row) != len(labels) for row in matrix):
                return JsonResponse({
                    'status': 'error',
                    'error': f'La matrice doit être carrée {len(labels)}x{len(labels)}'
                }, status=400)

            resultat = {}
            path_nodes = []

            # --- AIGUILLAGE DES ALGORITHMES ---
            
            if algo == 'dijkstra':
                if not depart or not arrivee:
                    return JsonResponse({
                        'status': 'error',
                        'error': 'Nœuds de départ et d\'arrivée requis pour Dijkstra'
                    }, status=400)
                
                if depart not in labels or arrivee not in labels:
                    return JsonResponse({
                        'status': 'error',
                        'error': f'Nœuds invalides. Nœuds disponibles: {", ".join(labels)}'
                    }, status=400)
                
                res = dijkstra.dijkstra(depart, arrivee, matrix=matrix, labels=labels)
                
                if isinstance(res, dict):
                    resultat = res
                    path_nodes = res['chemin'].split(' -> ')
                else:
                    resultat = {'message': str(res)}

            elif algo == 'bellman':
                if not depart:
                    return JsonResponse({
                        'status': 'error',
                        'error': 'Nœud de départ requis pour Bellman-Ford'
                    }, status=400)
                
                if depart not in labels:
                    return JsonResponse({
                        'status': 'error',
                        'error': f'Nœud de départ invalide. Nœuds disponibles: {", ".join(labels)}'
                    }, status=400)
                
                res = bellmanford.bellman_ford(depart, matrix=matrix, labels=labels)
                
                # Si c'est une liste d'indices (cycle détecté)
                if isinstance(res, list) and len(res) > 0 and isinstance(res[0], int):
                    cycle_names = [labels[i] for i in res]
                    path_nodes = cycle_names
                    resultat = {
                        'message': "⚠️ Cycle négatif détecté !",
                        'cycle': " → ".join(cycle_names) + " → " + cycle_names[0],
                        'type': 'cycle_negatif'
                    }
                
                # Si c'est une liste de distances
                elif isinstance(res, list) and len(res) > 0:
                    distances_dict = {}
                    for i, dist in enumerate(res):
                        if dist != float('inf'):
                            distances_dict[labels[i]] = dist
                    
                    resultat = {
                        'depart': depart,
                        'distances': distances_dict,
                        'message': f"Distances minimales depuis {depart}"
                    }
                    
                    # Si arrivée est spécifiée, mettre en évidence le chemin
                    if arrivee and arrivee in labels:
                        idx_arr = labels.index(arrivee)
                        resultat['distance_vers_arrivee'] = res[idx_arr]
                else:
                    resultat = {'message': str(res)}

            elif algo == 'floyd':
                dist_matrix = Floyd_Warshall.floyd_warshall(matrix=matrix, labels=labels)
                
                # Conversion en format lisible
                readable_matrix = []
                for i in range(len(labels)):
                    row = []
                    for j in range(len(labels)):
                        val = dist_matrix[i][j]
                        if val == float('inf'):
                            row.append('∞')
                        else:
                            row.append(round(val, 2))
                    readable_matrix.append(row)
                
                # Trouver le nœud le plus central (somme des distances minimale)
                centralite = []
                for i in range(len(labels)):
                    somme = sum(d for d in dist_matrix[i] if d != float('inf'))
                    centralite.append((labels[i], somme))
                
                centralite.sort(key=lambda x: x[1])
                noeud_central = centralite[0][0] if centralite else None
                
                resultat = {
                    'matrice_distances': readable_matrix,
                    'labels': labels,
                    'noeud_plus_central': noeud_central,
                    'centralite_score': round(centralite[0][1], 2) if centralite else None,
                    'message': f"Toutes les distances calculées. Nœud le plus central: {noeud_central}"
                }

            elif algo == 'pert':
                # Pour PERT, on utilise les données par défaut ou on pourrait parser un format spécial
                # Ici on utilise le projet par défaut
                chemin_critique = MethodePert.calcul_pert()
                
                resultat = {
                    'chemin_critique': chemin_critique,
                    'message': f"Chemin critique: {' → '.join(chemin_critique)}",
                    'note': 'Utilisation du projet par défaut (construction maison). Consultez la console pour les détails.'
                }
                
                path_nodes = chemin_critique
            
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': f'Algorithme inconnu: {algo}'
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'result': resultat,
                'path': path_nodes
            })

        except json.JSONDecodeError as e:
            return JsonResponse({
                'status': 'error',
                'error': f'JSON invalide: {str(e)}'
            }, status=400)
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'error': 'Méthode non autorisée. Utilisez POST.'
    }, status=405)