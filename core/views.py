from django.shortcuts import render
from django.http import JsonResponse
import json
import ast
import traceback
import math

from . import dijkstra, bellmanford, Floyd_Warshall, Matrice, MethodePert, bfs_dfs, prim_kruskal

def clean_data(data):
    """Nettoie les données pour le JSON (Infinity -> None)."""
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(v) for v in data]
    elif isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None
        return data
    return data

def parse_matrix(raw_string):
    if not raw_string: return None
    clean_str = raw_string.replace("inf", "None").replace("Infinity", "None").replace("null", "None")
    try:
        matrix = ast.literal_eval(clean_str)
        return [[(float('inf') if val is None else float(val)) for val in row] for row in matrix]
    except:
        return None

def index(request):
    matrix_list = Matrice.M.tolist()
    context = {
        'default_matrix': json.dumps(clean_data(matrix_list)),
        'default_villes': json.dumps(Matrice.villes)
    }
    return render(request, 'index.html', context)

def calculer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        algo = data.get('algo')
        depart = data.get('depart', '').strip()
        arrivee = data.get('arrivee', '').strip()
        
        try:
            matrix = parse_matrix(data.get('matrix'))
            raw_labels = data.get('labels', '')
            labels = [l.strip() for l in raw_labels.split(',') if l.strip()]
        except:
            matrix, labels = None, []

        resultat = {}
        path_nodes = []
        new_graph_data = None 

        # --- DIJKSTRA ---
        if algo == 'dijkstra':
            if not depart or not arrivee:
                return JsonResponse({'status': 'error', 'error': 'Précisez départ et arrivée.'})
            res = dijkstra.dijkstra(depart, arrivee, matrix=matrix, labels=labels)
            if isinstance(res, dict):
                path_nodes = res['chemin'].split(' -> ')
                resultat = res
                resultat['type'] = 'Dijkstra'
            else:
                return JsonResponse({'status': 'error', 'error': str(res)})

        # --- BELLMAN-FORD ---
        elif algo == 'bellman':
            if not depart: return JsonResponse({'status': 'error', 'error': 'Précisez le départ.'})
            res = bellmanford.bellman_ford(depart, matrix=matrix, labels=labels)
            
            if "error" in res: return JsonResponse({'status': 'error', 'error': res['error']})

            if res['type'] == 'cycle':
                path_nodes = res['cycle']
                resultat = {'type': 'Bellman-Ford (Cycle)', 'cycle': res['cycle'], 'alerte': 'Cycle Négatif !'}
            else:
                resultat = {'type': 'Bellman-Ford', 'distances': res['distances_dict'], 'depart': depart}
                if arrivee and arrivee in labels:
                    info = bellmanford.reconstruire_chemin(depart, arrivee, res['predecesseurs'], labels)
                    if info['existe']:
                        path_nodes = info['chemin']
                        resultat['chemin_texte'] = ' → '.join(path_nodes)
                        # CORRECTION ICI : On prend la distance directement dans le résultat global
                        # au lieu de chercher 'distance' dans info qui ne l'a pas.
                        resultat['dist_arrivee'] = res['distances_dict'].get(arrivee, "N/A")

        # --- FLOYD-WARSHALL ---
        elif algo == 'floyd':
            dist_matrix = Floyd_Warshall.floyd_warshall(matrix=matrix, labels=labels)
            min_sum, central_node = float('inf'), None
            for i, row in enumerate(dist_matrix):
                s = sum(d for d in row if d != float('inf'))
                if 0 < s < min_sum:
                    min_sum, central_node = s, labels[i]
            
            if central_node: path_nodes = [central_node]
            readable = [[("∞" if x == float('inf') else x) for x in row] for row in dist_matrix]
            resultat = {'type': 'Floyd-Warshall', 'matrice_distances': readable, 'noeud_central': central_node}

        # --- BFS ---
        elif algo == 'bfs':
            if not depart: return JsonResponse({'status': 'error', 'error': 'Précisez le départ.'})
            res = bfs_dfs.bfs(depart, matrix=matrix, labels=labels)
            if "error" in res: return JsonResponse({'status': 'error', 'error': res['error']})
            path_nodes = res['parcours']
            resultat = {'type': 'BFS', 'ordre_visite': res['parcours'], 'aretes_arbre': [f"{u}→{v}" for u,v in res['edges']]}
            new_graph_data = {'matrix': matrix or Matrice.M.tolist(), 'labels': labels or Matrice.villes, 'highlight_edges': res['edges']}

        # --- DFS ---
        elif algo == 'dfs':
            if not depart: return JsonResponse({'status': 'error', 'error': 'Précisez le départ.'})
            res = bfs_dfs.dfs(depart, matrix=matrix, labels=labels)
            if "error" in res: return JsonResponse({'status': 'error', 'error': res['error']})
            path_nodes = res['parcours']
            resultat = {'type': 'DFS', 'ordre_visite': res['parcours'], 'aretes_arbre': [f"{u}→{v}" for u,v in res['edges']]}
            new_graph_data = {'matrix': matrix or Matrice.M.tolist(), 'labels': labels or Matrice.villes, 'highlight_edges': res['edges']}

        # --- PRIM ---
        elif algo == 'prim':
            if not depart: return JsonResponse({'status': 'error', 'error': 'Précisez le départ.'})
            res = prim_kruskal.prim(depart, matrix=matrix, labels=labels)
            if "error" in res: return JsonResponse({'status': 'error', 'error': res['error']})
            noeuds = set([depart])
            for u, v in res['edges']: noeuds.add(u); noeuds.add(v)
            path_nodes = list(noeuds)
            resultat = {'type': 'Prim', 'poids_total': res['weight'], 'aretes': [f"{u}-{v}" for u,v in res['edges']]}
            new_graph_data = {'matrix': matrix or Matrice.M.tolist(), 'labels': labels or Matrice.villes, 'highlight_edges': res['edges']}

        # --- KRUSKAL ---
        elif algo == 'kruskal':
            res = prim_kruskal.kruskal(matrix=matrix, labels=labels)
            noeuds = set()
            for u, v in res['edges']: noeuds.add(u); noeuds.add(v)
            path_nodes = list(noeuds)
            resultat = {'type': 'Kruskal', 'poids_total': res['weight'], 'aretes': [f"{u}-{v}" for u,v in res['edges']]}
            new_graph_data = {'matrix': matrix or Matrice.M.tolist(), 'labels': labels or Matrice.villes, 'highlight_edges': res['edges']}

        # --- PERT ---
        elif algo == 'pert':
            custom_tasks = data.get('pert_data')
            taches_input = json.loads(custom_tasks) if custom_tasks else None
            
            res_pert = MethodePert.calcul_pert(taches_input)
            if 'erreur' in res_pert: return JsonResponse({'status': 'error', 'error': res_pert['erreur']})
            
            path_nodes = res_pert['chemin_critique']
            resultat = res_pert
            resultat['type'] = 'PERT'
            # CORRECTION ICI : On envoie le chemin critique tel quel (Liste) au lieu de stringifier
            # Le frontend gérera l'affichage.

            # Construction graphe PERT
            taches = taches_input if taches_input else MethodePert.default_taches
            pert_lbls = list(taches.keys())
            sz = len(pert_lbls)
            p_mat = [[0]*sz for _ in range(sz)]
            for idx, t in enumerate(pert_lbls):
                for p in taches[t].get('predecesseurs', []):
                    if p in pert_lbls:
                        p_idx = pert_lbls.index(p)
                        p_mat[p_idx][idx] = taches[p]['duree']
            new_graph_data = {'matrix': p_mat, 'labels': pert_lbls}

        return JsonResponse(clean_data({
            'status': 'success',
            'result': resultat,
            'path': path_nodes,
            'new_graph': new_graph_data
        }))

    except Exception as e:
        return JsonResponse({'status': 'error', 'error': f"Erreur serveur : {str(e)}", 'trace': traceback.format_exc()})