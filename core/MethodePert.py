# Jeu de données par défaut (Choix de la construction d'une maison)
default_taches = {
    'A': {'duree': 3, 'predecesseurs': []},      # Préparer terrain
    'B': {'duree': 4, 'predecesseurs': ['A']},   # Fondations
    'C': {'duree': 2, 'predecesseurs': ['B']},   # Murs
    'D': {'duree': 5, 'predecesseurs': ['B']},   # Toiture
    'E': {'duree': 2, 'predecesseurs': ['C']},   # Electricité
    'F': {'duree': 1, 'predecesseurs': ['D', 'E']} # Finitions
}

def calcul_pert(projet=None):
    """
    Calcule les dates au plus tôt, au plus tard et le chemin critique.
    Si 'projet' n'est pas fourni, utilise 'default_taches'.
    """
    # 1. Gestion des valeurs par défaut
    if projet is None:
        projet = default_taches

    # 2. Calcul dates au plus tôt (ES, EF)
    earliest = {t: {'ES': 0, 'EF': 0} for t in projet}
    
    # Simple propagation (tri topologique implicite via itération)
    change = True
    while change:
        change = False
        for t, data in projet.items():
            es_max = 0
            for p in data['predecesseurs']:
                # On vérifie que le prédécesseur existe pour éviter les plantages sur des données perso incomplètes
                if p in earliest:
                    es_max = max(es_max, earliest[p]['EF'])
            
            if earliest[t]['ES'] != es_max:
                earliest[t]['ES'] = es_max
                earliest[t]['EF'] = es_max + data['duree']
                change = True

    fin_projet = max(val['EF'] for val in earliest.values())

    # 3. Calcul dates au plus tard (LS, LF)
    latest = {t: {'LS': 0, 'LF': fin_projet} for t in projet}
    
    change = True
    while change:
        change = False
        for t in projet:
            # Trouver les successeurs de t
            successeurs = [k for k, v in projet.items() if t in v['predecesseurs']]
            
            lf_min = fin_projet
            if successeurs:
                # On filtre pour s'assurer que les successeurs existent dans 'latest'
                valid_succ = [s for s in successeurs if s in latest]
                if valid_succ:
                    lf_min = min(latest[s]['LS'] for s in valid_succ)
            
            if latest[t]['LF'] != lf_min:
                latest[t]['LF'] = lf_min
                latest[t]['LS'] = lf_min - projet[t]['duree']
                change = True

    # 4. Chemin critique (Marge nulle)
    chemin_critique = []
    print(f"\n{'Tâche':<5} {'Durée':<5} {'Début +Tôt':<12} {'Fin +Tard':<10} {'Marge'}")
    print("-" * 50)
    for t in projet:
        marge = latest[t]['LS'] - earliest[t]['ES']
        print(f"{t:<5} {projet[t]['duree']:<5} {earliest[t]['ES']:<12} {latest[t]['LF']:<10} {marge}")
        if marge == 0:
            chemin_critique.append(t)
            
    return chemin_critique