from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
from donnees_modeles import *
from operator import itemgetter
from itertools import chain, combinations
from copy import copy

def generation_solution_diversifies(fichier_entree,nombre_solutions, UtilisationGRASP):

    liste_solutions_generees = []

    #On génére un nombre défini de solutions
    for x in range(int(nombre_solutions)):

        solution_simple_input = lecture_fichier_entree(fichier_entree)
        solution_complementaire_input = lecture_fichier_entree(fichier_entree)

        # #Si on choisit de générer les solutions de manière purement aléatoire
        # if not UtilisationGRASP :
        #
        #     #On génère une solution simple et son complémentaire
        #     for (cache_serveur, cache_serveur_complementaire) in zip(solution_simple_input.cache_serveur_liste,solution_complementaire_input.cache_serveur_liste):
        #
        #         cache_serveur_complementaire.dict_videos = cache_serveur.remplissage_aleatoire_dict(solution_simple_input.videos_liste)
        #
        #         cache_serveur.dictionnaire_a_liste_videos(solution_simple_input.videos_liste)
        #         cache_serveur_complementaire.dictionnaire_a_liste_videos(solution_complementaire_input.videos_liste)
        #
        #     liste_solutions_generees.append(solution_simple_input.cache_serveur_liste)
        #     liste_solutions_generees.append(solution_complementaire_input.cache_serveur_liste)


        #Si l'on choisit de générer les solutions avec GRASP
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


        #On en déduit le dictionnaire
        for cache_serveur in solution_simple:
            cache_serveur.construction_dict(solution_simple_input.videos_liste).videos_liste_a_dict()

        liste_solutions_generees.append(solution_simple)

    return liste_solutions_generees

def recuperation_resabilite_solution(cash_serveur_liste_solution, capacite_stockage):
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

def amelioration_solution(cash_serveur_liste_solution, Fichier_a_traite):
    donnees_entrees = lecture_fichier_entree(Fichier_a_traite)
    #Récupération de la résabilité de la solution
    cash_serveur_liste_solution = recuperation_resabilite_solution(cash_serveur_liste_solution, donnees_entrees.capacite_stockage)

    #Application de l'algo glouton dessus
    cash_serveur_liste_solution =    gloutonneDeprecated(
            donnees_entrees.capacite_stockage,
            donnees_entrees.videos_liste,
            donnees_entrees.endpoints_liste,
            cash_serveur_liste_solution,
            donnees_entrees.requetes_liste,
            classementCache=True,
            nettoyage_requetes_video=True,
            GRASP=False,
            alphaGRASP=1)

    #Application d'une amélioration par recherche local
    cash_serveur_liste_solution = try_local_search(donnees_entrees.capacite_stockage, donnees_entrees.videos_liste, donnees_entrees.endpoints_liste, cash_serveur_liste_solution, donnees_entrees.requetes_liste, True)

    return cash_serveur_liste_solution

def distance_entre_deux_solutions(cash_serveur_liste_solution1, cash_serveur_liste_solution2):
    distance_euclidienne = 0
    for (cache_serveur_solution1,cache_serveur_solution2) in zip(cash_serveur_liste_solution1,cash_serveur_liste_solution2):
        for key in cache_serveur_solution1.dict_videos:
            if (key in cache_serveur_solution2.dict_videos and cache_serveur_solution1.dict_videos[key] == cache_serveur_solution2.dict_videos[key]):
                distance_euclidienne += 1
    return distance_euclidienne

def selection_ensemble_reference(ListeSolutions,donnees_entrees, nbre_elementsB1, B2):
    liste_score = []
    for solution in ListeSolutions:
        score_solution = evaluation_heuristique(solution, donnees_entrees.requetes_liste,
                                                          donnees_entrees.endpoints_liste,
                                                          donnees_entrees.videos_liste)
        liste_score.append([solution, score_solution])

    # On supprimme les doublons
    # liste_score  = list(set(liste_score))

    #On trie la liste selon le score
    liste_score = sorted(liste_score, key=itemgetter(1))

    #On retient un nombre d'élement constituant les meilleurs solutions : notre ensemble de solutions élites
    ListeSolutions = [element[0] for element in liste_score[0:nbre_elementsB1]]

    if B2:
        liste_distance = []
        #On créé la liste des élements non retenu pour sélectionner les élements avec le plus de distance à l'ensemble de référence actuel
        ListeSolutionNonRetenu = [element[0] for element in liste_score[nbre_elementsB1:-1]]

        for solution in ListeSolutionNonRetenu:
            somme_distance = sum(map(lambda x: distance_entre_deux_solutions(solution,x ), ListeSolutions))
            liste_distance.append([solution,somme_distance])
        # On trie la liste des distances
        liste_distance = sorted(liste_distance, key=itemgetter(1))
        nbre_elementsB2 = int(nbre_elementsB1/3)
        ListeB2 = [element[0] for element in liste_distance[0:nbre_elementsB2]]
        ListeSolutions += ListeB2


    return ListeSolutions

def generation_combinaison(combinaison,Fichier_a_traite):

    nouvelle_solution = lecture_fichier_entree(Fichier_a_traite)

    nouvelle_solution.cache_serveur_liste = gloutonneDeprecated(
        nouvelle_solution.capacite_stockage,
        nouvelle_solution.videos_liste,
        nouvelle_solution.endpoints_liste,
        nouvelle_solution.cache_serveur_liste,
        nouvelle_solution.requetes_liste,
        classementCache=True,
        nettoyage_requetes_video=True,
        GRASP=False,
        alphaGRASP=1)


    #Scores des solutions
    scores_solution = []
    for solution in combinaison:
        scores_solution.append(evaluation_heuristique(solution, nouvelle_solution.requetes_liste,
                                                          nouvelle_solution.endpoints_liste,
                                                          nouvelle_solution.videos_liste))
    somme_score = sum(scores_solution)
    ratio_score_solution = [x / somme_score for x in scores_solution]


    #Création d'une nouvelle solution par combinaison
    for cache_serveur in nouvelle_solution.cache_serveur_liste:
        cache_serveur.construction_dict_scatter(nouvelle_solution.videos_liste).construction_dict(nouvelle_solution.videos_liste)
    #Affectation du score pour chaque présence d'une vidéo
    numero_solution = 0
    for solution in combinaison:
        for (cache_serveur, cache_serveur_nouvelle_solution) in zip(solution, nouvelle_solution.cache_serveur_liste):

            for id in cache_serveur.dict_videos:
                if cache_serveur.dict_videos[id]:
                    cache_serveur_nouvelle_solution.dict_videos_score_scatter[id] += ratio_score_solution[numero_solution]
        numero_solution += 1

    #On affecte les vidéos dans le cache serveur, si le score est supérieur à 0.5
    for cache_serveur in nouvelle_solution.cache_serveur_liste:
        for id in cache_serveur.dict_videos_score_scatter:
            if cache_serveur.dict_videos_score_scatter[id] > 0.5:
                cache_serveur.dict_videos[id] = True
        cache_serveur.dictionnaire_a_liste_videos(nouvelle_solution.videos_liste)

    return nouvelle_solution.cache_serveur_liste

def toutes_combinaisons(Liste_solutions):
    return chain(*map(lambda x: combinations(Liste_solutions, x), range(0, len(Liste_solutions) + 1)))

def combinaison_solutions(Liste_solutions,Fichier_a_traite):

    #On itère parmis toutes les combinaisons de cardinalité de 2 (pair) et supérieur
    for combinaison in toutes_combinaisons(Liste_solutions):
        if len(combinaison) > 1:

            #On génére la solution
            sous_solution = generation_combinaison(combinaison,Fichier_a_traite)

            Liste_solutions.append(sous_solution)
    return Liste_solutions


def scatter_search(Fichier_a_traite, cardinalite_P, cardinalite_RefSetB1, GRASP_generation, nombre_iteration,B2):
    print("Scatter Search")
    donnees_entrees = lecture_fichier_entree(Fichier_a_traite)

    #Génération aléatoire de solutions
    ListeSolutions = generation_solution_diversifies(Fichier_a_traite, cardinalite_P, GRASP_generation)
    print("Nous possédons désormais l'ensemble P de solutions de cardinalité : ",len(ListeSolutions))

    # Sélection de l'ensemble de référence
    Ensemble_Reference = selection_ensemble_reference(ListeSolutions, donnees_entrees, cardinalite_RefSetB1,B2)
    print("Cardinalité Ensemble de référence : ", len(Ensemble_Reference))
    i = 0
    while i < nombre_iteration :
        #Generation de solution combinaisons de solution de l'Ensemble de référence
        ListeSolutionsGenere = combinaison_solutions(Ensemble_Reference,Fichier_a_traite)
        #print("NBRE SOLUCE GENERE : ",len(ListeSolutionsGenere))

        #Amélioration des solutions générés
        ListeSolutions_Ameliorees = []
        for solution in ListeSolutionsGenere:
            #print(solution[0].videos)
            ListeSolutions_Ameliorees.append(amelioration_solution(solution,Fichier_a_traite))

        # On mets à jour l'ensemble de référence
        Ensemble_Reference = selection_ensemble_reference(ListeSolutions_Ameliorees, donnees_entrees, cardinalite_RefSetB1,B2)
        #print("Cardinalité Ensemble de référence : ", len(Ensemble_Reference))

        print("Score à l'itération ",i+1)
        for solution in Ensemble_Reference:
            print(evaluation_heuristique(solution, donnees_entrees.requetes_liste,
                                         donnees_entrees.endpoints_liste,
                                         donnees_entrees.videos_liste))

        i += 1



    return ListeSolutions