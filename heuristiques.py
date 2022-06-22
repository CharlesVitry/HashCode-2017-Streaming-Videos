from donnees_modeles import *
from contraintes import *

# Structure en classes peu utile dans notre cas d'utilisation
#
# class Heuristique:
#     def __init__(self, nom , emplacement):
#         self.nom = nom
#         self.emplacement = emplacement
#
# class BorneInferieur(Heuristique):
#     def __init__(self):
#         super().__init__("Borne Inférieur","BorneInf")
#
# class BorneSuperieur(Heuristique):
#     def __init__(self):
#         super().__init__("Borne Inférieur","BorneInf")
#
# class Gloutonne(Heuristique):
#     def __init__(self):
#         super().__init__("Gloutonne","Gloutonne")

def borne_inferieur(cache_serveur_liste):
    #On affecte aucune vidéo à chaque cache serveur
    for cache_serveur in cache_serveur_liste:
        cache_serveur.videos = []

    return cache_serveur_liste


def borne_superieur_gloutonne(cache_serveur_liste, videos_liste):
    # On affecte toutes les vidéos à chaque cache serveur
    for cache_serveur in cache_serveur_liste:
        cache_serveur.videos = videos_liste

    return cache_serveur_liste


def born_supp(requetes_liste, endpoints_liste, cache_serveur_liste, videos_liste):
    UB = 0
    best_latence_pondere = 0
    somme_nombre_requete = 0
    
    # On parcours l'ensemble des requêtes 
    for requete in requetes_liste :
        endpoint_requete = objet_par_id(endpoints_liste, requete.endpoint_id)[0]
        
        # On récupère la latence au datacenter du endpoint de la requete
        latence_datacenter_LD = endpoint_requete.latence_datacenter_LD

        cache_id_all = []
        latences_possible_video = [latence_datacenter_LD]

        # On créé une liste des id de l'ensemble des cache serveur pour choisir le meilleur
        for cacheserveur in cache_serveur_liste:
            cache_id_all.append(cacheserveur.id)

        # On fait la liste des id de cache serveurs qui dessert le endpoint de la requête
        liste_id_cache_du_endpoint = [i['id_cache_serveur'] for i in (endpoint_requete.latence_aux_caches_serveurs)]

        # On parcours l'ensemble des cash serveur, on recup la latence entre le endpoint de la requete 
        for cache_serveur in liste_id_cache_du_endpoint:
            if (cache_serveur in cache_id_all):
                latences_possible_video.append(endpoint_requete.getter_latence_aux_caches_serveurs(cache_serveur))

        # on choisis le meilleur gain
        minimum = min(latences_possible_video)
        best_latence = latence_datacenter_LD - minimum
        somme_nombre_requete += requete.nombre_de_requetes
        best_latence_pondere += requete.nombre_de_requetes * best_latence

    UB = int(1000 * best_latence_pondere / somme_nombre_requete)
    return UB





def gloutonne(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste,classementCache, GRASP, alphaGRASP):


    #Dans le cas d'une solution déjà présente,
    #On vide la liste de vidéos déjà affectés au cache serveur
    for cache_serveur in cache_serveur_liste:
        cache_serveur.videos = []

    #On commence par copié la liste des requetes des endpoints, en effet, une fois traité
    # on supprimmera la requête pour recalculer le gain sur les endpoints
    for endpoint in endpoints_liste:
        endpoint.requetes_liste_a_traite = endpoint.requetes_liste


    # On calculs des ratios pour les poids de vidéos, les requetes et les endpoints
    somme_latence_datacenter = sum([endpoint.latence_datacenter_LD for endpoint in endpoints_liste])
    for endpoint in endpoints_liste:
        endpoint.latence_divise_fonction(somme_latence_datacenter)

    somme_poid_videos = sum([video.poid for video in videos_liste])
    for video in videos_liste:
        video.poid_divise_fonction(somme_poid_videos)

    somme_requetes = sum([requete.nombre_de_requetes for requete in requetes_liste])
    for requete in requetes_liste:
        requete.nombre_de_requetes_divise_fonction(somme_requetes)

    # On ordonne les caches serveurs par leur importance
    # càd leurs gains possibles par rapport vidéos associés aux requetes de leurs endpoints
    if classementCache:
        cache_serveurs_decroissant = sorted(cache_serveur_liste, key=lambda c: -c.importance_du_cache(videos_liste))
    else:
        cache_serveurs_decroissant = cache_serveur_liste


    # On parcours chacun des caches serveurs
    for cache_serveur in cache_serveurs_decroissant:

        # On calcul un gain ponderé sur chacune des vidéos pouvant entrer dans le cache serveur
        gain_videos = {}
        for endpoint in cache_serveur.endpoints:
            for requete in endpoint.requetes_liste_a_traite:

                video = videos_liste[requete.video_id]
                gain_latence_pondere = (endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(cache_serveur.id)) * video.rapport_divise(endpoint.id)

                # Si la vidéo est déjà dans la liste des gains,
                #on ajoute le gain sinon on affecte le gain actuel.
                if requete.video_id in gain_videos:
                    gain_videos[requete.video_id] += gain_latence_pondere
                else:
                    gain_videos[requete.video_id] = gain_latence_pondere
        # On ordonne les gains de vidéos de façon décroissante
        videos_ordonnees_decroissantes_par_gain = sorted(gain_videos.items(), key=lambda x: -x[1])

        # On ajouter les vidéos dans le cache serveur tant qu'il y a de la place
        poid_actuel_cache_serveur = 0
        for (i, gain) in videos_ordonnees_decroissantes_par_gain:

            # Inutile d'ajouter les gains à 0,
            # on arrete la boucle dès que la première vidéo à gain à 0 apparait
            
            if gain == 0:
                break
              
            video = videos_liste[i]

            # On vérifie qu'il y a la place nécessaire pour mettre la vidéo
            if (poid_actuel_cache_serveur + video.poid <= cache_serveur.capacite):

                # Actualisation du poid occupé du cache serveur
                poid_actuel_cache_serveur += video.poid

                # Ajout de la vidéo dans la liste du cache serveur
                cache_serveur.ajout_video(video)

                # On supprimme les requetes correspondantes à la vidéo sur
                # les endpoints connecté au cache serveur
                for endpoint in cache_serveur.endpoints:
                    endpoint.supp_requete_traite(video.id)

    return cache_serveur_liste

def trajectory(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste) :

    for endpoint in endpoints_liste:
        endpoint.requetes_liste_a_traite = endpoint.requetes_liste


    # 1ere étape : création d'une solution ne respectant pas la contrainte de capacités
    for cache_serveur in cache_serveur_liste :
        gain_videos = {}
        for endpoint in cache_serveur.endpoints :
    
            for requete in endpoint.requetes_liste_a_traite :
                video = videos_liste[requete.video_id]
                gain_latence = endpoint.latence_datacenter_LD - endpoint.getter_latence_aux_caches_serveurs(cache_serveur.id)

                # Si la vidéo est déjà dans la liste des gains,
                #on ajoute le gain sinon on affecte le gain actuel.
                if requete.video_id in gain_videos:
                    gain_videos[requete.video_id] += gain_latence
                else:
                    gain_videos[requete.video_id] = gain_latence
                    
        gain_sorted = sorted(gain_videos.items(), key=lambda x: -x[1])
        #print(gain_sorted)    
        for (i, gain) in gain_sorted:

            # Inutile d'ajouter les gains à 0,
            # on arrete la boucle dès que la première vidéo à gain à 0 apparait
            if gain == 0:
                break
              
            video = videos_liste[i]
            # Ajout de la vidéo dans la liste du cache serveur
            cache_serveur.ajout_video(video)

    # 2eme étape : amélioration de la solution trouvée 

    liste_remplissage = []
    for cache_serveur in cache_serveur_liste:
        liste_remplissage.append( sum([video.poid for video in cache_serveur.videos]) / capacite_stockage )
    if all( remplissage < 1 for remplissage in liste_remplissage  ):       
        return cache_serveur_liste        


    ##### MODIF SOLUCE
    # > changement / poid de la VIDEO pas QS
    
    return cache_serveur_liste
