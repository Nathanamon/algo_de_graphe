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
        
        # Récupération données (sauf pour PERT qui a ses propres données par défaut si vide)
        try:
            matrix = parse_matrix(data.get('matrix'))
            raw_labels = data.get('labels', '')
            labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        except:
            matrix, labels = None, []

        resultat = {}
        path_nodes = []
        # Nouveaux champs pour forcer la mise à jour du graphe (utile pour PERT)
        new_graph_data = None 

        # --- ALGORITHMES ---

        if algo == 'dijkstra':
            res = dijkstra.dijkstra(depart, arrivee, matrix=matrix, labels=labels)
            if isinstance(res, dict):
                resultat = res
                path_nodes = res['chemin'].split(' -> ')
            else:
                resultat = {'message': str(res)}

        elif algo == 'bellman':
            res = bellmanford.bellman_ford(depart, matrix=matrix, labels=labels)
            
            if "error" in res:
                return JsonResponse({'status': 'error', 'error': res['error']})

            if res['type'] == 'cycle':
                cycle_names = [labels[i] for i in res['cycle']]
                path_nodes = cycle_names
                resultat = {'message': "⚠️ Cycle négatif détecté !", 'cycle': " -> ".join(cycle_names)}
            else:
                # Reconstruction du chemin si une arrivée est donnée
                dists = res['distances']
                preds = res['predecesseurs']
                
                if arrivee and arrivee in labels:
                    idx_arr = labels.index(arrivee)
                    if dists[idx_arr] == float('inf'):
                        resultat = {'message': "Pas de chemin."}
                    else:
                        # On remonte les prédécesseurs
                        curr = idx_arr
                        path_indices = []
                        while curr != -1:
                            path_indices.insert(0, curr)
                            curr = preds[curr]
                        path_nodes = [labels[i] for i in path_indices]
                        resultat = {
                            'distance': dists[idx_arr],
                            'chemin': " -> ".join(path_nodes)
                        }
                
                # On renvoie aussi toutes les distances pour affichage
                formatted_dists = {labels[i]: (d if d != float('inf') else "∞") for i, d in enumerate(dists)}
                resultat['toutes_distances'] = formatted_dists

        elif algo == 'floyd':
            dist_matrix = Floyd_Warshall.floyd_warshall(matrix=matrix, labels=labels)
            
            # Calcul de centralité pour colorier un nœud
            min_sum = float('inf')
            central_node = None
            for i, row in enumerate(dist_matrix):
                s = sum(d for d in row if d != float('inf'))
                if s < min_sum and s > 0:
                    min_sum = s
                    central_node = labels[i]
            
            if central_node:
                path_nodes = [central_node] # On colorie juste ce nœud
                resultat['info'] = f"Nœud le plus central : {central_node}"

            # Matrice lisible
            readable = [[("∞" if x == float('inf') else x) for x in row] for row in dist_matrix]
            resultat['matrice'] = readable

        elif algo == 'bfs':
            res = bfs_dfs.bfs(depart, matrix=matrix, labels=labels)
            if isinstance(res, dict) and "error" in res:
                resultat = res
            else:
                path_nodes = res
                resultat = {'parcours': ' → '.join(res), 'type': 'BFS'}

        elif algo == 'dfs':
            res = bfs_dfs.dfs(depart, matrix=matrix, labels=labels)
            if isinstance(res, dict) and "error" in res:
                resultat = res
            else:
                path_nodes = res
                resultat = {'parcours': ' → '.join(res), 'type': 'DFS'}

        elif algo == 'prim':
            res = prim_kruskal.prim(depart, matrix=matrix, labels=labels)
            if "error" in res:
                resultat = res
            else:
                # Récupérer les arêtes pour le graphe
                edges = res['edges']
                path_nodes = []
                for edge in edges:
                    path_nodes.extend(edge)  # Ajouter les deux extrémités
                resultat = {
                    'aretes': [f"{u} -- {v}" for u, v in edges],
                    'poids_total': res['weight'],
                    'nombre_aretes': len(edges)
                }

        elif algo == 'kruskal':
            res = prim_kruskal.kruskal(matrix=matrix, labels=labels)
            if "error" in res:
                resultat = res
            else:
                # Récupérer les arêtes pour le graphe
                edges = res['edges']
                path_nodes = []
                for edge in edges:
                    path_nodes.extend(edge)  # Ajouter les deux extrémités
                resultat = {
                    'aretes': [f"{u} -- {v}" for u, v in edges],
                    'poids_total': res['weight'],
                    'nombre_aretes': len(edges)
                }

        elif algo == 'pert':
            # 1. Récupération des données
            custom_tasks_str = data.get('pert_data')
            taches_projet = None
            
            if custom_tasks_str:
                try:
                    taches_projet = json.loads(custom_tasks_str)
                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'error': 'Format JSON des tâches invalide'})
            
            # 2. Calcul via la méthode PERT
            # On récupère le résultat complet (dictionnaire)
            res_pert = MethodePert.calcul_pert(taches_projet)
            
            # Gestion d'erreur renvoyée par MethodePert (ex: cycle détecté)
            if 'erreur' in res_pert:
                return JsonResponse({'status': 'error', 'error': res_pert['erreur']})

            # CORRECTION ICI : On extrait la liste du chemin critique pour le surlignage
            path_nodes = res_pert['chemin_critique']
            
            # On passe tout le résultat au frontend pour l'onglet "Résultats détaillés"
            resultat = res_pert
            
            # 3. Construction du graphe PERT pour l'affichage (Matrice d'adjacence visuelle)
            if taches_projet:
                taches = taches_projet
            else:
                taches = MethodePert.default_taches
                
            pert_labels = list(taches.keys())
            n_p = len(pert_labels)
            # Initialisation matrice vide
            pert_matrix = [[0]*n_p for _ in range(n_p)]
            
            for t_idx, t_name in enumerate(pert_labels):
                if 'predecesseurs' in taches[t_name]:
                    for pred in taches[t_name]['predecesseurs']:
                        if pred in pert_labels:
                            p_idx = pert_labels.index(pred)
                            # On met la durée du prédécesseur comme poids de l'arc (pour info visuelle)
                            # Ou on met simplement 1 pour marquer le lien. 
                            # Ici on garde la durée du noeud source (convention visuelle)
                            pert_matrix[p_idx][t_idx] = taches[pred]['duree']
            
            new_graph_data = {
                'matrix': pert_matrix,
                'labels': pert_labels
            }

        return JsonResponse({
            'status': 'success',
            'result': resultat,
            'path': path_nodes,
            'new_graph': new_graph_data # Champ spécial pour PERT
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e), 'trace': traceback.format_exc()})