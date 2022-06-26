from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
from donnees_modeles import *
import random
from copy import copy

def generation_solution_diversifies(fichier_entree,nombre_solutions, UtilisationGRASP):

    liste_solutions_generees = []

    #On génére un nombre défini de solutions
    for x in range(int(nombre_solutions/2)):


        solution_simple_input = lecture_fichier_entree(fichier_entree)
        solution_complementaire_input = lecture_fichier_entree(fichier_entree)

        #Si on choisit de générer les solutions de manière purement aléatoire
        if not UtilisationGRASP :

            #On génère une solution simple et son complémentaire
            for (cache_serveur, cache_serveur_complementaire) in zip(solution_simple_input.cache_serveur_liste,solution_complementaire_input.cache_serveur_liste):

                cache_serveur_complementaire.dict_videos = cache_serveur.remplissage_aleatoire_dict(solution_simple_input.videos_liste)

                cache_serveur.dictionnaire_a_liste_videos(solution_simple_input.videos_liste)
                cache_serveur_complementaire.dictionnaire_a_liste_videos(solution_complementaire_input.videos_liste)

            liste_solutions_generees.append(solution_simple_input.cache_serveur_liste)
            liste_solutions_generees.append(solution_complementaire_input.cache_serveur_liste)

        #Si l'on choisit de générer les solutions avec GRASP
        else:
            solution_simple = gloutonneDeprecated(
         solution_simple_input.capacite_stockage,
         solution_simple_input.videos_liste,
         solution_simple_input.endpoints_liste,
         solution_simple_input.cache_serveur_liste,
         solution_simple_input.requetes_liste,
        classementCache = True,
        nettoyage_requetes_video =  True,
        GRASP =    True,
        alphaGRASP = 1)
            solution_complementaire = gloutonneDeprecated(
         solution_complementaire_input.capacite_stockage,
         solution_complementaire_input.videos_liste,
         solution_complementaire_input.endpoints_liste,
         solution_complementaire_input.cache_serveur_liste,
         solution_complementaire_input.requetes_liste,
        classementCache = True,
        nettoyage_requetes_video =  True,
        GRASP =    True,
        alphaGRASP = 1)

            #On en déduit le dictionnaire
            for cache_serveur in solution_simple:
                cache_serveur.construction_dict(solution_simple_input.videos_liste).videos_liste_a_dict()

            for cache_serveur in solution_complementaire:
                cache_serveur.construction_dict(solution_complementaire_input.videos_liste).videos_liste_a_dict()


            liste_solutions_generees.append(solution_simple)
            liste_solutions_generees.append(solution_complementaire)

    return liste_solutions_generees

def recupération_resabilite_solution(cash_serveur_liste_solution, capacite_stockage):
    for cache_serveur in cash_serveur_liste_solution:

        #Si un cache serveur est complet alors on retire des vidéos tant qu'il est plein
        if sum([video.poid for video in cache_serveur.videos]) > capacite_stockage:
            #On calculs le ratio de chaque video dans le cache serveur
            ratio_video = {}

            for endpoint in cache_serveur.endpoints:
                for requete in endpoint.requetes_liste:
                    #Si la requete correspond à une video présente dans le cache, on l'ajoute à la liste des ratios
                    if cache_serveur.dict_videos[requete.video_id]:

                        video = objet_par_id(cache_serveur.videos, requete.video_id)[0]

                        #video = cache_serveur.videos[requete.video_id]
                        gain_latence_pondere = (endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(
                                                   cache_serveur.id)) * video.rapport_divise(endpoint.id)

                        # Si la vidéo est déjà dans la liste des gains,
                        # on ajoute le gain sinon on affecte le gain actuel.
                        if requete.video_id in ratio_video:
                            ratio_video[requete.video_id] += gain_latence_pondere
                        else:
                            ratio_video[requete.video_id] = gain_latence_pondere


            # On ordonne les gains de vidéos de façon décroissante
            videos_ordonnees_croissantes_par_ratio = sorted(ratio_video.items(), key=lambda x: x[1])

            #On retire les vidéos, on break(arrete) quand le cache serveur a retrouvé sa résabilité
            for (i, gain) in videos_ordonnees_croissantes_par_ratio:
                video = objet_par_id(cache_serveur.videos, i)[0]

                # Actualisation du poid occupé du cache serveur
                cache_serveur.capacite_occupe -= video.poid

                # Suppression de la vidéo dans la liste du cache serveur
                cache_serveur.suppression_video(video)

                #Suppression dans le dictionnaire
                cache_serveur.dict_videos[video.id] = False

                #Si la capacité est respecté, on arrete
                if (cache_serveur.capacite_occupe <= capacite_stockage):
                    break

    return cash_serveur_liste_solution



def scatter_search():
    None