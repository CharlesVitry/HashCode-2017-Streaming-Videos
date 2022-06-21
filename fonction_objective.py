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

        #On créé une liste des id des caches serveur possèdant la vidéo
        for cacheserveur in cache_serveur_liste_solution:
            if  requete.video_id in [video.id for video in cacheserveur.videos] :
                #print("ajout")
                cache_id_avec_video.append(cacheserveur.id)

        #On fait la liste des id de cache serveurs qui dessert le endpoint de la requête
        liste_id_cache_du_endpoint = [i['id_cache_serveur'] for i in (endpoint_requete.latence_aux_caches_serveurs)]

        #print(liste_id_cache_du_endpoint, " ; ",cache_id_avec_video)

        #On ajoute la latence des caches serveurs qui dessert le endpoint ET qui ont la vidéo de la requête
        for cache_serveur in liste_id_cache_du_endpoint:
            if (cache_serveur in cache_id_avec_video):
                latences_possible_video.append(endpoint_requete.getter_latence_aux_caches_serveurs(cache_serveur))
        #print(latences_possible_video)

        #On calcul la latence sauvé par différence à la latence au cache serveur
        
        minimum = min(latences_possible_video)
        latence_sauve = latence_datacenter_LD - minimum
        somme_nombre_requete += requete.nombre_de_requetes
        latence_sauve_pondere += requete.nombre_de_requetes * latence_sauve

    return int(1000 * latence_sauve_pondere / somme_nombre_requete)




