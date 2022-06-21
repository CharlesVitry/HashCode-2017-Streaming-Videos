import warnings

# Contrôle de réalisabilité
def Validite_De_La_Solution(cache_serveur_liste_solution,cache_serveur_liste, capacite_stockage ):
    Validite = True

    if not contrainte1(cache_serveur_liste_solution,capacite_stockage):
        warnings.warn("Contrainte 1 Non Satisfaite :"
                      " La capacité des cash centers n'est pas respectée")
        Validite =  False

    if not contrainte2():
        warnings.warn("Contrainte 2 Non Satisfaite :"
                      " Au moins une requete n'est pas desservie")
        Validite =  False

    if not contrainte3():
        warnings.warn("Contrainte 3 Non Satisfaite : "
                      "Une requête est desservie par le cache center sans que la vidéo de la requete ne soit dans celui ci ")
        Validite =  False

    if not contrainte4():
        warnings.warn("Contrainte 4 Non Satisfaite : "
                      "Le saving de latence est mal définit")
        Validite =  False

    if not contrainte5(cache_serveur_liste_solution,cache_serveur_liste):
        warnings.warn("Contrainte 5 Non Satisfaite : "
                      "Le cache serveur ne dessert aucun endpoint où la vidéo est demandé"
                      "La vidéo n'a pas de requetes sur les endpoints de ce cache serveur ")
        Validite =  False

    return Validite

def contrainte1(cache_serveur_liste_solution,capacite_stockage):
    for cache_serveur in cache_serveur_liste_solution:
        #Si la somme du poid des vidéos est supérieur à la capacité du cache serveur alors la contrainte n'est pas respectée
        if sum([video.poid for video in cache_serveur.videos]) > capacite_stockage:
            return False
    return True

def contrainte2():
    #les requetes sont au moins desservie par le datacenter dans notre modèle
    return True

def contrainte3():
    # Le fichier de sortie ne précise pas le moyen de validation de la requête
    return True

def contrainte4():
    #Le saving de latence est définit dans la fonction d'évaluation des heuristiques
    return True

def contrainte5(cache_serveur_liste_solution, cache_serveur_liste ):
    for cache_serveur_soluce, cache_serveur in zip(cache_serveur_liste_solution, cache_serveur_liste):

        #print(cache_serveur_soluce.id, " ", cache_serveur.id)
        videos_id_du_cache_serveur = [video.id for video in cache_serveur_soluce.videos]

        print(videos_id_du_cache_serveur)

        requetes = [endpoint.requetes_liste for endpoint in cache_serveur.endpoints]

        videos_id_des_requetes_du_cache_serveur =   [ requete.video_id for requete in
        [requetes_liste for requetes_liste in
         [requete for liste_requetes in requetes for requete in liste_requetes]
                                                     ]
                                                        ]

        print(videos_id_des_requetes_du_cache_serveur)

        if not all(video_id in videos_id_du_cache_serveur  for video_id in videos_id_des_requetes_du_cache_serveur):
            return False

    return True