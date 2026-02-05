from django.shortcuts import render
from django.http import JsonResponse
import json
import ast
import traceback

from . import dijkstra, bellmanford, Floyd_Warshall, Matrice, MethodePert, bfs_dfs, prim_kruskal

def index(request):
    """Page d'accueil avec données par défaut."""
    # Nettoyage des inf pour le JSON
    matrix_list = Matrice.M.tolist()
    clean_matrix = [[(None if x == float('inf') else x) for x in row] for row in matrix_list]
    
    context = {
        'default_matrix': json.dumps(clean_matrix),
        'default_villes': json.dumps(Matrice.villes)
    }
    return render(request, 'index.html', context)

def parse_matrix(raw_string):
    """Convertit string -> liste en gérant inf/null."""
    if not raw_string: return None
    clean_str = raw_string.replace("inf", "None").replace("Infinity", "None").replace("null", "None")
    try:
        matrix = ast.literal_eval(clean_str)
        return [[(float('inf') if val is None else float(val)) for val in row] for row in matrix]
    except:
        raise ValueError("Format de matrice invalide")

def calculer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        algo = data.get('algo')
        depart = data.get('depart', '').strip()
        arrivee = data.get('arrivee', '').strip()
        
        # Récupération données
        try:
            matrix = parse_matrix(data.get('matrix'))
            raw_labels = data.get('labels', '')
            labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        except:
            matrix, labels = None, []

        resultat = {}
        path_nodes = []
        new_graph_data = None 

        # ==================== DIJKSTRA ====================
        if algo == 'dijkstra':
            if not depart or not arrivee:
                return JsonResponse({'status': 'error', 'error': 'Veuillez spécifier une ville de départ et d\'arrivée'})
            
            res = dijkstra.dijkstra(depart, arrivee, matrix=matrix, labels=labels)
            
            if isinstance(res, dict):
                path_nodes = res['chemin'].split(' -> ')
                resultat = {
                    'type': 'Dijkstra',
                    'depart': depart,
                    'arrivee': arrivee,
                    'chemin': res['chemin'],
                    'distance_totale': res['distance_totale'],
                    'nb_etapes': len(path_nodes)
                }
            else:
                return JsonResponse({'status': 'error', 'error': str(res)})

        # ==================== BELLMAN-FORD ====================
        elif algo == 'bellman':
            if not depart:
                return JsonResponse({'status': 'error', 'error': 'Veuillez spécifier une ville de départ'})
            
            res = bellmanford.bellman_ford(depart, matrix=matrix, labels=labels)
            
            if "error" in res:
                return JsonResponse({'status': 'error', 'error': res['error']})

            if res['type'] == 'cycle':
                path_nodes = res['cycle']
                resultat = {
                    'type': 'Bellman-Ford - Cycle Négatif',
                    'alerte': '⚠️ Cycle négatif détecté !',
                    'cycle': res['cycle'],
                    'poids_cycle': res.get('poids_cycle', 'N/A'),
                    'message': res.get('message', '')
                }
            else:
                # Affichage des distances depuis le départ
                resultat = {
                    'type': 'Bellman-Ford',
                    'depart': depart,
                    'distances': res['distances_dict']
                }
                
                # Si arrivée spécifiée, montrer le chemin
                if arrivee and arrivee in labels:
                    chemin_info = bellmanford.reconstruire_chemin(
                        depart, arrivee, res['predecesseurs'], labels
                    )
                    if chemin_info['existe']:
                        path_nodes = chemin_info['chemin']
                        idx_arr = labels.index(arrivee)
                        resultat['chemin'] = ' → '.join(path_nodes)
                        resultat['distance'] = res['distances'][idx_arr]
                        resultat['arrivee'] = arrivee

        # ==================== FLOYD-WARSHALL ====================
        elif algo == 'floyd':
            dist_matrix = Floyd_Warshall.floyd_warshall(matrix=matrix, labels=labels)
            
            # Calcul du nœud le plus central
            min_sum = float('inf')
            central_node = None
            central_sum = 0
            
            for i, row in enumerate(dist_matrix):
                s = sum(d for d in row if d != float('inf'))
                if s < min_sum and s > 0:
                    min_sum = s
                    central_node = labels[i]
                    central_sum = s
            
            if central_node:
                path_nodes = [central_node]
            
            # Matrice formatée
            readable = [[("∞" if x == float('inf') else x) for x in row] for row in dist_matrix]
            
            resultat = {
                'type': 'Floyd-Warshall',
                'matrice_distances': readable,
                'noeud_central': central_node,
                'somme_distances_centrale': round(central_sum, 2) if central_sum else None,
                'taille': len(labels)
            }

        # ==================== BFS ====================
        elif algo == 'bfs':
            if not depart:
                return JsonResponse({'status': 'error', 'error': 'Veuillez spécifier une ville de départ'})
            
            res = bfs_dfs.bfs(depart, matrix=matrix, labels=labels)
            if "error" in res: 
                return JsonResponse({'status': 'error', 'error': res['error']})
            
            path_nodes = res['parcours']
            
            resultat = {
                'type': 'BFS (Parcours en Largeur)',
                'depart': depart,
                'ordre_visite': res['parcours'],
                'noeuds_visites': len(res['parcours']),
                'aretes_arbre': [f"{e[0]} → {e[1]}" for e in res['edges']]
            }
            
            # Nouvelles données pour le graphe
            new_graph_data = {
                'matrix': matrix if matrix else Matrice.M.tolist(),
                'labels': labels if labels else Matrice.villes,
                'highlight_edges': res['edges']
            }

        # ==================== DFS ====================
        elif algo == 'dfs':
            if not depart:
                return JsonResponse({'status': 'error', 'error': 'Veuillez spécifier une ville de départ'})
            
            res = bfs_dfs.dfs(depart, matrix=matrix, labels=labels)
            if "error" in res: 
                return JsonResponse({'status': 'error', 'error': res['error']})
            
            path_nodes = res['parcours']
            
            resultat = {
                'type': 'DFS (Parcours en Profondeur)',
                'depart': depart,
                'ordre_visite': res['parcours'],
                'noeuds_visites': len(res['parcours']),
                'aretes_arbre': [f"{e[0]} → {e[1]}" for e in res['edges']]
            }
            
            new_graph_data = {
                'matrix': matrix if matrix else Matrice.M.tolist(),
                'labels': labels if labels else Matrice.villes,
                'highlight_edges': res['edges']
            }

        # ==================== PRIM ====================
        elif algo == 'prim':
            if not depart:
                return JsonResponse({'status': 'error', 'error': 'Veuillez spécifier une ville de départ'})
            
            res = prim_kruskal.prim(depart, matrix=matrix, labels=labels)
            if "error" in res: 
                return JsonResponse({'status': 'error', 'error': res['error']})
            
            # Tous les nœuds connectés par l'arbre
            noeuds_couverts = set([depart])
            for edge in res['edges']:
                noeuds_couverts.add(edge[0])
                noeuds_couverts.add(edge[1])
            
            path_nodes = list(noeuds_couverts)
            
            resultat = {
                'type': 'Prim (Arbre Couvrant Minimum)',
                'depart': depart,
                'poids_total': res['weight'],
                'nombre_aretes': len(res['edges']),
                'noeuds_couverts': len(noeuds_couverts),
                'aretes': [f"{e[0]} ↔ {e[1]}" for e in res['edges']]
            }
            
            new_graph_data = {
                'matrix': matrix if matrix else Matrice.M.tolist(),
                'labels': labels if labels else Matrice.villes,
                'highlight_edges': res['edges']
            }

        # ==================== KRUSKAL ====================
        elif algo == 'kruskal':
            res = prim_kruskal.kruskal(matrix=matrix, labels=labels)
            
            # Tous les nœuds connectés par l'arbre
            noeuds_couverts = set()
            for edge in res['edges']:
                noeuds_couverts.add(edge[0])
                noeuds_couverts.add(edge[1])
            
            path_nodes = list(noeuds_couverts)
            
            resultat = {
                'type': 'Kruskal (Arbre Couvrant Minimum)',
                'poids_total': res['weight'],
                'nombre_aretes': len(res['edges']),
                'noeuds_couverts': len(noeuds_couverts),
                'aretes': [f"{e[0]} ↔ {e[1]}" for e in res['edges']]
            }
            
            new_graph_data = {
                'matrix': matrix if matrix else Matrice.M.tolist(),
                'labels': labels if labels else Matrice.villes,
                'highlight_edges': res['edges']
            }

        # ==================== PERT ====================
        elif algo == 'pert':
            custom_tasks_str = data.get('pert_data')
            taches_projet = None
            
            if custom_tasks_str:
                try:
                    taches_projet = json.loads(custom_tasks_str)
                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'error': 'Format JSON des tâches invalide'})
            
            # Calcul PERT
            res_pert = MethodePert.calcul_pert(taches_projet, verbose=False)
            
            if 'erreur' in res_pert:
                return JsonResponse({'status': 'error', 'error': res_pert['erreur']})
            
            path_nodes = res_pert['chemin_critique']
            
            # Formatage des détails pour affichage
            details_formatted = {}
            for tache, info in res_pert['details'].items():
                details_formatted[tache] = {
                    'duree': info['duree'],
                    'ES': info['ES'],
                    'EF': info['EF'],
                    'LS': info['LS'],
                    'LF': info['LF'],
                    'marge': info['marge_totale'],
                    'critique': '✓' if info['critique'] else '✗',
                    'nom': info.get('nom', tache)
                }
            
            resultat = {
                'type': 'PERT (Ordonnancement)',
                'chemin_critique': ' → '.join(res_pert['chemin_critique']),
                'duree_projet': res_pert['duree_projet'],
                'nb_taches_critiques': res_pert['taches_critiques_count'],
                'nb_taches_totales': res_pert['taches_totales'],
                'details': details_formatted
            }
            
            # Construction du graphe PERT pour visualisation
            if taches_projet:
                taches = taches_projet
            else:
                taches = MethodePert.default_taches
            
            pert_labels = list(taches.keys())
            n_p = len(pert_labels)
            pert_matrix = [[0]*n_p for _ in range(n_p)]
            
            for t_idx, t_name in enumerate(pert_labels):
                if 'predecesseurs' in taches[t_name]:
                    for pred in taches[t_name]['predecesseurs']:
                        if pred in pert_labels:
                            p_idx = pert_labels.index(pred)
                            pert_matrix[p_idx][t_idx] = taches[pred]['duree']
            
            new_graph_data = {
                'matrix': pert_matrix,
                'labels': pert_labels
            }

        return JsonResponse({
            'status': 'success',
            'result': resultat,
            'path': path_nodes,
            'new_graph': new_graph_data
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'error': str(e), 
            'trace': traceback.format_exc()
        })