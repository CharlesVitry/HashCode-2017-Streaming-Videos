from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
from donnees_modeles import *
import random
import numpy as np

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


def get_decompo_lagrange(cache_serveur_liste_solution, requetes_liste, endpoints_liste, x, y, l):
    somme_nombre_requete = 0
    
    
    for requete in requetes_liste : 
        somme_nombre_requete += requete.nombre_de_requetes
    K = 1000 / somme_nombre_requete
    
    part1 = 0
    part2 = 0
    for requete in requetes_liste :
        endpoint_requete = objet_par_id(endpoints_liste, requete.endpoint_id)[0]
        latence_datacenter_LD = endpoint_requete.latence_datacenter_LD

        cache_id_all = []
        for cache_serveur in cache_serveur_liste_solution :
            cache_id_all.append(cache_serveur.id)
        liste_id_cache_du_endpoint = [i['id_cache_serveur'] for i in (endpoint_requete.latence_aux_caches_serveurs)]

        for cache_serveur in liste_id_cache_du_endpoint:
            if (cache_serveur in cache_id_all):
                part1 -= K * (requete.nombre_de_requetes * (latence_datacenter_LD - endpoint_requete.getter_latence_aux_caches_serveurs(cache_serveur)) + l) * y[cache_serveur][endpoint_requete.id]
                part2 += l * x[cache_serveur][requete.video_id]

    UB_lagrange = part1 - part2
    return UB_lagrange


def borne_sup_lagrangienne(nbre_cache_serveur, nbre_requetes, nbre_videos, cache_serveur_liste_solution, requete_liste, endpoints_liste):
    y = np.zeros((nbre_cache_serveur, nbre_requetes))
    for cache_serveur in cache_serveur_liste_solution :
        for endpoint in cache_serveur.endpoints :
            for requete in endpoint.requetes_liste :
                y[cache_serveur.id][requete.requete_id] = 1
    

    x = np.zeros((nbre_cache_serveur, nbre_videos))
    for cache_serveur in cache_serveur_liste_solution :
        for video in cache_serveur.videos :
            x[cache_serveur.id][video.id] = 1
    #print(x.shape)
    #print(x)
    #print(y.shape)
    #print(y)

    UB_lagrange = get_decompo_lagrange(cache_serveur_liste_solution, requete_liste, endpoints_liste, x, y, 1)
    return UB_lagrange
            
    

def gloutonneDeprecated(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste,classementCache,nettoyage_requetes_video, GRASP, alphaGRASP):


    #Dans le cas d'une solution déjà présente,
    #On vide la liste de vidéos déjà affectés au cache serveur
    # for cache_serveur in cache_serveur_liste:
    #     cache_serveur.videos = []

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


    ###########################
    # Méthode 1  on ajoute les vidéos par une probabilité proportionnelle à leur gain
    ###########################

    if GRASP:
        # somme_importance_caches = sum([cache_serveur.importance for cache_serveur in cache_serveurs_decroissant ])
        #
        # for cache_serveur in cache_serveurs_decroissant:
        #     cache_serveur.importance_divise_fonction(somme_importance_caches)

        # On parcours chacun des caches serveurs de manière totalement aléatoire
        for cache_serveur in sorted(cache_serveurs_decroissant, key=lambda _: random.random()):
            # On calcul un gain ponderé sur chacune des vidéos pouvant entrer dans le cache serveur
            # le dictionnaire a l'id de la vidéo et le gain associé à elle
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

            #Calcul des probabilités par vidéo
            somme_gain = sum(gain_videos.values() )**alphaGRASP
            probabilite_par_video = {i: (gain**alphaGRASP)/somme_gain for i, gain in gain_videos.items()}

            while len(probabilite_par_video) != 0:
                #On tire un nombre de 0 à 1 et on initialise la somme des probas à 1
                nombre_hasard = random.random()
                somme_proba = 0

                #On parcours le dictionnaire
                for i in list(probabilite_par_video):
                    somme_proba += probabilite_par_video[i]
                    #Si la somme des probas est supérieur au nombre au hasard, on ajoute la vidéo
                    if somme_proba > nombre_hasard :
                        video = videos_liste[i]
                        # On vérifie qu'il y a la place nécessaire pour mettre la vidéo
                        if (cache_serveur.capacite_occupe + video.poid <= capacite_stockage):

                            # Actualisation du poid occupé du cache serveur
                            cache_serveur.capacite_occupe += video.poid
                            #print(poid_actuel_cache_serveur)

                            # Ajout de la vidéo dans la liste du cache serveur
                            cache_serveur.ajout_video(video)

                            # On supprimme les requetes correspondantes à la vidéo sur
                            # les endpoints connecté au cache serveur
                            if nettoyage_requetes_video:
                                for endpoint in cache_serveur.endpoints:
                                    endpoint.supp_requete_traite(video.id)


                        #On arrete la boucle quand une vidéo a été choisi, la vidéo est supprimmé du dictionnaire
                        del probabilite_par_video[i]
                        break


    ###########################
    # Méthode 2  on ajoute les vidéos par des un classement décroissant de score
    ###########################

    else:
        # On parcours chacun des caches serveurs
        for cache_serveur in cache_serveurs_decroissant:

            # On calcul un gain ponderé sur chacune des vidéos pouvant entrer dans le cache serveur
            # le dictionnaire a l'id de la vidéo et le gain associé à elle
            gain_videos = {}
            for endpoint in cache_serveur.endpoints:
                for requete in endpoint.requetes_liste_a_traite:

                    video = videos_liste[requete.video_id]
                    gain_latence_pondere = (
                                                       endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(
                                                   cache_serveur.id)) * video.rapport_divise(endpoint.id)

                    # Si la vidéo est déjà dans la liste des gains,
                    # on ajoute le gain sinon on affecte le gain actuel.
                    if requete.video_id in gain_videos:
                        gain_videos[requete.video_id] += gain_latence_pondere
                    else:
                        gain_videos[requete.video_id] = gain_latence_pondere


            # On ordonne les gains de vidéos de façon décroissante
            videos_ordonnees_decroissantes_par_gain = sorted(gain_videos.items(), key=lambda x: -x[1])

            # On ajouter les vidéos dans le cache serveur tant qu'il y a de la place

            for (i, gain) in videos_ordonnees_decroissantes_par_gain:

                # Inutile d'ajouter les gains à 0,
                # on arrete la boucle dès que la première vidéo à gain à 0 apparait

                if gain == 0:
                    break

                video = videos_liste[i]

                # On vérifie qu'il y a la place nécessaire pour mettre la vidéo
                if (cache_serveur.capacite_occupe + video.poid <= capacite_stockage):

                    # Actualisation du poid occupé du cache serveur
                    cache_serveur.capacite_occupe += video.poid

                    # Ajout de la vidéo dans la liste du cache serveur
                    cache_serveur.ajout_video(video)

                    # On supprimme les requetes correspondantes à la vidéo sur
                    # les endpoints connecté au cache serveur
                    if nettoyage_requetes_video:
                        for endpoint in cache_serveur.endpoints:
                            endpoint.supp_requete_traite(video.id)

    #On créé le dictionnaire
    for cache_serveur in cache_serveur_liste:
        cache_serveur.construction_dict(videos_liste).videos_liste_a_dict()

    return cache_serveur_liste

"""
def gloutonne_nouvelle(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste,
                        classementCache, nettoyage_requetes_video, GRASP, alphaGRASP, nombre_de_video_a_ajoute_par_cache):

    nombre_videos_ajoutes = 0

    # On commence par copié la liste des requetes des endpoints, en effet, une fois traité
    # on supprimmera la requête pour recalculer le gain sur les endpoints

    if nombre_de_video_a_ajoute_par_cache == 1 :
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
        # le dictionnaire a l'id de la vidéo et le gain associé à elle
        gain_videos = {}
        for endpoint in cache_serveur.endpoints:
            for requete in endpoint.requetes_liste_a_traite:

                video = videos_liste[requete.video_id]
                gain_latence_pondere = (
                                                   endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(
                                               cache_serveur.id)) * video.rapport_divise(endpoint.id)

                # Si la vidéo est déjà dans la liste des gains,
                # on ajoute le gain sinon on affecte le gain actuel.
                if requete.video_id in gain_videos:
                    gain_videos[requete.video_id] += gain_latence_pondere
                else:
                    gain_videos[requete.video_id] = gain_latence_pondere

        ###
        # Méthode 1 d'ajout
        # Si l'on choisit d'ajouter les vidéos directement par leurs gains pondérés
        if not GRASP:
            # On ordonne les gains de vidéos de façon décroissante
            videos_ordonnees_decroissantes_par_gain = sorted(gain_videos.items(), key=lambda x: -x[1])

            # On ajouter les vidéos dans le cache serveur tant qu'il y a de la place
            for (i, gain) in videos_ordonnees_decroissantes_par_gain:

                # Inutile d'ajouter les gains à 0,
                # on arrete la boucle dès que la première vidéo à gain à 0 apparait

                if gain == 0:
                    break

                video = videos_liste[i]

                # On vérifie qu'il y a la place nécessaire pour mettre la vidéo
                if (cache_serveur.capacite_occupe + video.poid <= capacite_stockage):

                    # Actualisation du poid occupé du cache serveur
                    cache_serveur.capacite_occupe += video.poid

                    # Ajout de la vidéo dans la liste du cache serveur
                    cache_serveur.ajout_video(video)
                    nombre_videos_ajoutes += 1

                    # On supprimme les requetes correspondantes à la vidéo sur :

                    if nettoyage_requetes_video:
                        for endpoint in cache_serveur.endpoints:
                            # de la liste des endpoints connecté au cache server
                            endpoint.supp_requete_traite(video.id)
                            # La liste des requetes de la vidéo sur ces endpoints
                            #video.supp_requete( endpoint.id) #Inutile
                            # De la liste globale
                            #requetes_liste = [requete for requete in requetes_liste if requete.endpoint_id != endpoint.id and requete.video_id != video.id]
                    break





        ###
        # Méthode 2 d'ajout
        # Si l'on ajoute les vidéos par une probabilité proportionnelle à leur gain
        else:
            somme_gain = sum(gain_videos.values()) ** alphaGRASP
            probabilite_par_video = {i: (gain ** alphaGRASP) / somme_gain for i, gain in gain_videos.items()}

            # On parcours l'ensemble des vidéos apte à rentrer dans le cache serveur
            for x in probabilite_par_video:

                # On tire un nombre de 0 à 1 et on initialise la somme des probas à 1
                nombre_hasard = random.random()
                somme_proba = 0

                # On re-parcour le dictionnaire
                for i in probabilite_par_video:
                    somme_proba += probabilite_par_video[i]
                    # Si la somme des probas est supérieur au nombre au hasard, on ajoute la vidéo
                    if somme_proba > nombre_hasard:
                        video = videos_liste[i]
                        # On vérifie qu'il y a la place nécessaire pour mettre la vidéo
                        if (cache_serveur.capacite_occupe + video.poid <= capacite_stockage):

                            # Actualisation du poid occupé du cache serveur
                            cache_serveur.capacite_occupe += video.poid
                            # print(poid_actuel_cache_serveur)

                            # Ajout de la vidéo dans la liste du cache serveur
                            cache_serveur.ajout_video(video)


                            # On supprimme les requetes correspondantes à la vidéo sur
                            # les endpoints connecté au cache serveur
                            if nettoyage_requetes_video:
                                for endpoint in cache_serveur.endpoints:
                                    endpoint.supp_requete_traite(video.id)

                        break
    if nombre_videos_ajoutes == 0:
        return cache_serveur_liste
    else:
        return (gloutonne_nouvelle(
            capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste,
        classementCache = classementCache,
        nettoyage_requetes_video =  nettoyage_requetes_video,
        GRASP =    GRASP,
        alphaGRASP = alphaGRASP,
        nombre_de_video_a_ajoute_par_cache = nombre_de_video_a_ajoute_par_cache +1
    ))
"""

# def trajectory(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste) :
#
#     # Dans le cas d'une solution déjà présente,
#     # On vide la liste de vidéos déjà affectés au cache serveur
#     for cache_serveur in cache_serveur_liste:
#         cache_serveur.videos = []
#
#     #On copie la liste des requetes original
#     for endpoint in endpoints_liste:
#         endpoint.requetes_liste_a_traite = endpoint.requetes_liste
#
#
#     # 1ere étape : création d'une solution ne respectant pas la contrainte de capacités
#     cache_serveur_liste = gloutonne(
#         capacite_stockage * 1000,
#         videos_liste,
#         endpoints_liste,
#         cache_serveur_liste,
#         requetes_liste,
#         True,
#         False,
#         False,
#         1)
#     # 2eme étape : amélioration de la solution trouvée
#
#     liste_remplissage = []
#     for cache_serveur in cache_serveur_liste:
#         liste_remplissage.append( sum([video.poid for video in cache_serveur.videos]) / capacite_stockage )
#     if all( remplissage < 1 for remplissage in liste_remplissage  ):
#         return cache_serveur_liste
#
#
#     ##### MODIF SOLUCE
#     # > changement / poid de la VIDEO pas QS
#
#     return cache_serveur_liste


def try_local_search(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste) :
    # Dans le cas d'une solution déjà présente,
    # On vide la liste de vidéos déjà affectés au cache serveur
    for cache_serveur in cache_serveur_liste:
        cache_serveur.videos = []

    #On copie la liste des requetes original
    for endpoint in endpoints_liste:
        endpoint.requetes_liste_a_traite = endpoint.requetes_liste

    # 1ere étape : création d'une solution, ici gloutonne
    cache_serveur_liste = gloutonneDeprecated(
        capacite_stockage,
        videos_liste,
        endpoints_liste,
        cache_serveur_liste,
        requetes_liste,
        True,
        True,
        False,
        1)

    

    score_max = evaluation_heuristique(cache_serveur_liste, requetes_liste, endpoints_liste, videos_liste)

    for cache_serveur in cache_serveur_liste:

        poid_actuel_cache_serveur = sum([video.poid for video in cache_serveur.videos])
                                     
        liste_videos_in = [video for video in cache_serveur.videos]
        liste_videos_s = [video for video in videos_liste]
        
        
        for i in range(0, len(liste_videos_in)) :

            for j in range (0, 50):
                # NOUVELLE VIDEO
                temps_video = random.choice(liste_videos_s)
                temps_video_poid = temps_video.poid


                # ANCIENNE VIDEO
                old_video = liste_videos_in[i]
                old_video_poid = old_video.poid
                
                
                if(temps_video.id != old_video.id):

                    nouveau_poid = cache_serveur.capacite_occupe + temps_video_poid - old_video_poid
                        
        
                    if (nouveau_poid <= capacite_stockage):
                        # MISE A JOUR
                    
                        liste_videos_in[i] = temps_video
                        cache_serveur.videos = liste_videos_in
                        cache_serveur.capacite_occupe += temps_video_poid
                        cache_serveur.capacite_occupe -= old_video_poid 

                        poid_actuel_cache_serveur = cache_serveur.capacite_occupe
                        
                        nouveau_score = evaluation_heuristique(cache_serveur_liste, requetes_liste, endpoints_liste, videos_liste)
                        
                        if(nouveau_score > score_max):
                            score_max = nouveau_score

                        else :
                            liste_videos_in[i] = old_video
                            cache_serveur.videos = liste_videos_in
                            cache_serveur.capacite_occupe -= temps_video_poid
                            cache_serveur.capacite_occupe += old_video_poid 
                            poid_actuel_cache_serveur = cache_serveur.capacite_occupe - temps_video_poid + old_video_poid
                    else :
                        pass

    
    gloutonneDeprecated(
        capacite_stockage,
        videos_liste,
        endpoints_liste,
        cache_serveur_liste,
        requetes_liste,
        classementCache=True,
        nettoyage_requetes_video=True,
        GRASP=False,
        alphaGRASP=1)

                    
    return cache_serveur_liste

