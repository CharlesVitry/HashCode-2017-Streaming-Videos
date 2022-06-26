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
            None


    return liste_solutions_generees

def recupération_resabilite_solution(cash_serveur_liste_solution, capacite_stockage):
    for cash_serveur in cash_serveur_liste_solution:

        #Si un cache serveur est complet alors on l'épure
        if sum([video.poid for video in cache_serveur.videos]) > capacite_stockage:
           #On calculs le ratio de chaque video dans le cache serveur
            ratio_video = {}
            for endpoint in cache_serveur.endpoints:
                for requete in endpoint.requetes_liste_a_traite:

                    video = videos_liste[requete.video_id]
                    gain_latence_pondere = (
                                                   endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(
                                               cache_serveur.id)) * video.rapport_divise(endpoint.id)

                    # Si la vidéo est déjà dans la liste des gains,
                    # on ajoute le gain sinon on affecte le gain actuel.
                    if requete.video_id in ratio_video:
                        ratio_video[requete.video_id] += gain_latence_pondere
                    else:
                        ratio_video[requete.video_id] = gain_latence_pondere

            # On ordonne les gains de vidéos de façon décroissante
            videos_ordonnees_decroissantes_par_gain = sorted(ratio_video.items(), key=lambda x: -x[1])

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


def scatter_search():
    None