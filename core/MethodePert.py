from collections import deque, defaultdict


# Jeu de données par défaut (Construction d'une maison)
default_taches = {
    'A': {'duree': 3, 'predecesseurs': [], 'nom': 'Préparation terrain'},
    'B': {'duree': 4, 'predecesseurs': ['A'], 'nom': 'Fondations'},
    'C': {'duree': 2, 'predecesseurs': ['B'], 'nom': 'Murs'},
    'D': {'duree': 5, 'predecesseurs': ['B'], 'nom': 'Toiture'},
    'E': {'duree': 2, 'predecesseurs': ['C'], 'nom': 'Électricité'},
    'F': {'duree': 1, 'predecesseurs': ['D', 'E'], 'nom': 'Finitions'}
}


def detecter_cycle_taches(projet):
    """
    Détecte la présence d'un cycle dans le graphe de dépendances des tâches.
    Utilise l'algorithme de Kahn (tri topologique).
    
    Args:
        projet (dict): Dictionnaire des tâches
    
    Returns:
        tuple: (bool, list) - (cycle_existe, ordre_topologique ou cycle)
    """
    # Calcul du degré entrant de chaque tâche
    degre_entrant = {t: 0 for t in projet}
    
    for tache, data in projet.items():
        for pred in data.get('predecesseurs', []):
            if pred in degre_entrant:
                degre_entrant[tache] += 1
    
    # File des tâches sans prédécesseurs
    file = deque([t for t, degre in degre_entrant.items() if degre == 0])
    ordre_topologique = []
    
    while file:
        tache = file.popleft()
        ordre_topologique.append(tache)
        
        # Trouver les successeurs de cette tâche
        for t, data in projet.items():
            if tache in data.get('predecesseurs', []):
                degre_entrant[t] -= 1
                if degre_entrant[t] == 0:
                    file.append(t)
    
    # Si toutes les tâches ont été traitées, pas de cycle
    if len(ordre_topologique) == len(projet):
        return False, ordre_topologique
    else:
        # Il y a un cycle : trouver les tâches impliquées
        taches_dans_cycle = [t for t in projet if t not in ordre_topologique]
        return True, taches_dans_cycle


def valider_projet(projet):
    """
    Valide la structure du projet PERT.
    
    Args:
        projet (dict): Dictionnaire des tâches
    
    Returns:
        tuple: (bool, str) - (valide, message_erreur)
    """
    if not projet:
        return False, "Le projet est vide"
    
    # Vérifier que chaque tâche a une durée
    for tache, data in projet.items():
        if 'duree' not in data:
            return False, f"La tâche '{tache}' n'a pas de durée définie"
        
        if not isinstance(data['duree'], (int, float)) or data['duree'] < 0:
            return False, f"La durée de la tâche '{tache}' doit être un nombre positif"
        
        # Vérifier que les prédécesseurs existent
        preds = data.get('predecesseurs', [])
        for pred in preds:
            if pred not in projet:
                return False, f"La tâche '{tache}' dépend de '{pred}' qui n'existe pas"
    
    # Vérifier l'absence de cycle
    cycle_detecte, info = detecter_cycle_taches(projet)
    if cycle_detecte:
        return False, f"Cycle détecté impliquant les tâches : {', '.join(info)}"
    
    return True, ""


def calcul_pert(projet=None, verbose=True):
    """
    Calcule les dates au plus tôt, au plus tard et identifie le chemin critique
    d'un projet selon la méthode PERT (Program Evaluation and Review Technique).
    
    Args:
        projet (dict, optional): Dictionnaire des tâches au format :
            {
                'nom_tache': {
                    'duree': float,
                    'predecesseurs': list[str],
                    'nom': str (optionnel, pour description)
                }
            }
            Si None, utilise default_taches.
        verbose (bool): Si True, affiche le tableau des résultats
    
    Returns:
        dict: Résultats détaillés contenant :
            - 'chemin_critique': list[str] - Tâches du chemin critique
            - 'duree_projet': float - Durée totale minimale du projet
            - 'details': dict - Détails de chaque tâche
            - 'erreur': str (si erreur de validation)
    
    Raises:
        ValueError: Si le projet contient un cycle ou des données invalides
    
    Example:
        >>> projet = {
        ...     'A': {'duree': 3, 'predecesseurs': []},
        ...     'B': {'duree': 2, 'predecesseurs': ['A']}
        ... }
        >>> result = calcul_pert(projet)
        >>> print(result['chemin_critique'])
        ['A', 'B']
    """
    # 1. Gestion des valeurs par défaut
    if projet is None:
        projet = default_taches
    
    # 2. Validation du projet
    valide, message = valider_projet(projet)
    if not valide:
        return {
            'erreur': message,
            'chemin_critique': [],
            'duree_projet': 0
        }
    
    # 3. Obtenir l'ordre topologique
    _, ordre_topologique = detecter_cycle_taches(projet)
    
    # 4. Calcul des dates au plus tôt (ES = Earliest Start, EF = Earliest Finish)
    earliest = {}
    
    for tache in ordre_topologique:
        data = projet[tache]
        
        # La date de début au plus tôt est le max des dates de fin des prédécesseurs
        es = 0
        for pred in data.get('predecesseurs', []):
            if pred in earliest:
                es = max(es, earliest[pred]['EF'])
        
        ef = es + data['duree']
        earliest[tache] = {'ES': es, 'EF': ef}
    
    # 5. Durée totale du projet
    duree_projet = max(val['EF'] for val in earliest.values()) if earliest else 0
    
    # 6. Calcul des dates au plus tard (LS = Latest Start, LF = Latest Finish)
    # On parcourt dans l'ordre inverse
    latest = {}
    
    # Initialisation : les tâches finales ont LF = durée du projet
    taches_finales = [
        t for t in projet 
        if not any(t in projet[autre].get('predecesseurs', []) for autre in projet)
    ]
    
    for tache in taches_finales:
        latest[tache] = {
            'LF': duree_projet,
            'LS': duree_projet - projet[tache]['duree']
        }
    
    # Propagation en ordre inverse
    for tache in reversed(ordre_topologique):
        if tache in latest:
            continue
        
        # Trouver les successeurs de cette tâche
        successeurs = [
            t for t in projet 
            if tache in projet[t].get('predecesseurs', [])
        ]
        
        # La date de fin au plus tard est le min des dates de début des successeurs
        lf = duree_projet  # Valeur par défaut si pas de successeur
        if successeurs:
            lf = min(latest[succ]['LS'] for succ in successeurs if succ in latest)
        
        ls = lf - projet[tache]['duree']
        latest[tache] = {'LS': ls, 'LF': lf}
    
    # 7. Calcul des marges et identification du chemin critique
    details = {}
    chemin_critique = []
    
    for tache in projet:
        es = earliest[tache]['ES']
        ef = earliest[tache]['EF']
        ls = latest[tache]['LS']
        lf = latest[tache]['LF']
        
        marge_totale = ls - es  # = lf - ef (toujours égales)
        
        # Une tâche est critique si sa marge est nulle
        est_critique = (marge_totale == 0)
        if est_critique:
            chemin_critique.append(tache)
        
        details[tache] = {
            'duree': projet[tache]['duree'],
            'ES': es,
            'EF': ef,
            'LS': ls,
            'LF': lf,
            'marge_totale': marge_totale,
            'critique': est_critique,
            'nom': projet[tache].get('nom', tache)
        }
    
    # 8. Affichage du tableau (si verbose)
    if verbose:
        print("\n" + "="*90)
        print(f"{'ANALYSE PERT - ORDONNANCEMENT DU PROJET':^90}")
        print("="*90)
        print(f"\n{'Tâche':<8} {'Durée':<7} {'ES':<6} {'EF':<6} {'LS':<6} {'LF':<6} {'Marge':<7} {'Critique':<10} {'Description'}")
        print("-"*90)
        
        for tache in ordre_topologique:
            d = details[tache]
            critique_symbole = "⚠️ OUI" if d['critique'] else "Non"
            print(
                f"{tache:<8} {d['duree']:<7} {d['ES']:<6} {d['EF']:<6} "
                f"{d['LS']:<6} {d['LF']:<6} {d['marge_totale']:<7} "
                f"{critique_symbole:<10} {d['nom']}"
            )
        
        print("-"*90)
        print(f"Durée totale du projet : {duree_projet} unités de temps")
        print(f"Chemin critique : {' → '.join(chemin_critique)}")
        print("="*90 + "\n")
    
    # 9. Retour des résultats
    return {
        'chemin_critique': chemin_critique,
        'duree_projet': duree_projet,
        'details': details,
        'ordre_topologique': ordre_topologique,
        'taches_critiques_count': len(chemin_critique),
        'taches_totales': len(projet)
    }


def generer_gantt_data(projet=None):
    """
    Génère les données pour un diagramme de Gantt à partir d'un projet PERT.
    
    Args:
        projet (dict, optional): Dictionnaire des tâches. Si None, utilise default_taches.
    
    Returns:
        dict: Données formatées pour affichage Gantt :
            {
                'taches': list[dict] avec pour chaque tâche :
                    - 'nom': str
                    - 'debut': float (date au plus tôt)
                    - 'fin': float (date au plus tard)
                    - 'duree': float
                    - 'critique': bool
                'duree_totale': float
            }
    """
    if projet is None:
        projet = default_taches
    
    # Calcul PERT
    resultats = calcul_pert(projet, verbose=False)
    
    if 'erreur' in resultats:
        return {'erreur': resultats['erreur']}
    
    # Formatage pour Gantt
    taches_gantt = []
    
    for tache, infos in resultats['details'].items():
        taches_gantt.append({
            'id': tache,
            'nom': infos['nom'],
            'debut': infos['ES'],
            'fin': infos['EF'],
            'duree': infos['duree'],
            'marge': infos['marge_totale'],
            'critique': infos['critique'],
            'predecesseurs': projet[tache].get('predecesseurs', [])
        })
    
    # Tri par date de début
    taches_gantt.sort(key=lambda x: x['debut'])
    
    return {
        'taches': taches_gantt,
        'duree_totale': resultats['duree_projet'],
        'chemin_critique': resultats['chemin_critique']
    }


def afficher_gantt_ascii(projet=None):
    """
    Affiche un diagramme de Gantt simple en ASCII dans la console.
    
    Args:
        projet (dict, optional): Dictionnaire des tâches
    """
    data = generer_gantt_data(projet)
    
    if 'erreur' in data:
        print(f"Erreur : {data['erreur']}")
        return
    
    duree_max = int(data['duree_totale'])
    
    print("\n" + "="*80)
    print(f"{'DIAGRAMME DE GANTT':^80}")
    print("="*80)
    
    # En-tête temporel
    print(f"\n{'Tâche':<10} ", end="")
    for t in range(0, duree_max + 1):
        print(f"{t:<3}", end="")
    print()
    print("-" * (10 + (duree_max + 1) * 3))
    
    # Barres des tâches
    for tache in data['taches']:
        symbole = "█" if tache['critique'] else "▓"
        
        # Construire la barre
        barre = [' '] * (duree_max + 1)
        debut = int(tache['debut'])
        fin = int(tache['fin'])
        
        for i in range(debut, fin):
            if i < len(barre):
                barre[i] = symbole
        
        # Affichage
        print(f"{tache['id']:<10} ", end="")
        for i in range(duree_max + 1):
            print(f"{barre[i]:<3}", end="")
        
        info = f" [{tache['duree']}j]"
        if tache['critique']:
            info += " ⚠️ CRITIQUE"
        print(info)
    
    print("-" * (10 + (duree_max + 1) * 3))
    print(f"\nLégende : █ = Tâche critique  |  ▓ = Tâche non-critique")
    print(f"Durée totale : {duree_max} unités de temps")
    print("="*80 + "\n")


# Test automatique si exécuté directement
if __name__ == "__main__":
    print("=== TEST DE LA MÉTHODE PERT ===\n")
    
    # Test 1 : Projet par défaut
    print("1. Projet par défaut (Construction maison)")
    resultat = calcul_pert()
    
    # Test 2 : Diagramme de Gantt
    print("\n2. Diagramme de Gantt")
    afficher_gantt_ascii()
    
    # Test 3 : Projet custom
    print("\n3. Projet custom (Développement logiciel)")
    projet_dev = {
        'A': {'duree': 2, 'predecesseurs': [], 'nom': 'Analyse besoins'},
        'B': {'duree': 3, 'predecesseurs': ['A'], 'nom': 'Conception'},
        'C': {'duree': 5, 'predecesseurs': ['B'], 'nom': 'Développement'},
        'D': {'duree': 2, 'predecesseurs': ['B'], 'nom': 'Design UI'},
        'E': {'duree': 3, 'predecesseurs': ['C', 'D'], 'nom': 'Tests'},
        'F': {'duree': 1, 'predecesseurs': ['E'], 'nom': 'Déploiement'}
    }
    calcul_pert(projet_dev)
    
    # Test 4 : Détection de cycle
    print("\n4. Test de détection de cycle")
    projet_cyclique = {
        'A': {'duree': 2, 'predecesseurs': ['C']},  # A dépend de C
        'B': {'duree': 3, 'predecesseurs': ['A']},  # B dépend de A
        'C': {'duree': 1, 'predecesseurs': ['B']}   # C dépend de B → CYCLE!
    }
    resultat_cycle = calcul_pert(projet_cyclique)
    print(f"Résultat : {resultat_cycle}")