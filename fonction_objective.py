from donnees_modeles import *

def evaluation_heuristique(cache_serveur_liste_solution,requetes_liste,endpoints_liste,videos_liste ):

    #La fonction objective est composé de deux termes sommes sur les requetes
    latence_sauve_pondere = 0
    somme_nombre_requete = 0

    #parcours des requetes
    for requete in requetes_liste:
        endpoint_requete = objet_par_id(endpoints_liste, requete.endpoint_id)[0]

        #On récupère la latence au datacenter du endpoint de la requete
        latence_datacenter_LD = endpoint_requete.latence_datacenter_LD

        #On ajoute la latence datacenter aux latences possibles pour cette requete
        latences_possible_video = [latence_datacenter_LD]

        #Liste des caches contenant la vidéo de la requete
        cache_id_avec_video = []

        for cacheserveur in cache_serveur_liste_solution:
            if  requete.video_id in [video.id for video in cacheserveur.videos] :
                #print("ajout")
                cache_id_avec_video.append(cacheserveur.id)

        liste_id_cache_du_endpoint = [i['id_cache_serveur'] for i in (endpoint_requete.latence_aux_caches_serveurs)]

        #print(liste_id_cache_du_endpoint, " ; ",cache_id_avec_video)
        for cache_serveur in liste_id_cache_du_endpoint:
            if (cache_serveur in cache_id_avec_video):
                latences_possible_video.append(endpoint_requete.getter_latence_aux_caches_serveurs(cache_serveur))
        #print(latences_possible_video)

        minimum = min(latences_possible_video)
        latence_sauve = latence_datacenter_LD - minimum
        somme_nombre_requete = somme_nombre_requete + requete.nombre_de_requetes
        latence_sauve_pondere = latence_sauve_pondere + requete.nombre_de_requetes * latence_sauve

    return int(1000 * latence_sauve_pondere / somme_nombre_requete)




