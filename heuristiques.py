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


def borne_superieur(cache_serveur_liste, videos_liste):
    # On affecte toutes les vidéos à chaque cache serveur
    for cache_serveur in cache_serveur_liste:
        cache_serveur.videos = videos_liste

    return cache_serveur_liste

def gloutonne(capacite_stockage, videos_liste, endpoints_liste, cache_serveur_liste, requetes_liste):
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
    cache_serveurs_decroissant = sorted(cache_serveur_liste, key=lambda c: -c.importance_du_cache(videos_liste))

    # On parcours chacun des caches serveurs
    for cache_serveur in cache_serveurs_decroissant:

        # On calcul un gain ponderé sur chacune des vidéos pouvant entrer dans le cache serveur
        gain_videos = {}
        for endpoint in cache_serveur.endpoints:
            for requete in endpoint.requetes_liste:

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
                    endpoint.supp_requete(video.id)

    return cache_serveur_liste

