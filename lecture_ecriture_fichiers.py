from donnees_modeles import *

def lecture_fichier_entree(emplacement_fichier):
    with open(emplacement_fichier, 'r') as entree:

        #Selon le manuel, il s'agit d'un format UNIX, on utilise donc '\n'
        lignes = [line.rstrip('\n') for line in entree]

        #La première ligne du fichiers contient les nombres de vidéos, endpoint, requetes, cache serveurs et la capacité des caches serveurs
        [nbre_videos, nbre_endpoints, nbre_requetes, nbre_cache_serveur, capacite_stockage] = [int(x) for x in lignes[0].split(' ')]

        #La deuxième ligne est le poid de chacune des vidéos, on utilise l'espace pour séparer chaque poid
        videos_liste = [Videos(i, int(x)) for (i, x) in enumerate(lignes[1].split(' '))]

        ########################################
        # Données sur les endpoints et les caches serveurs
        ########################################

        #création liste endpoints et cache serveurs
        endpoints_liste = []
        cache_serveur_liste = [Cache_Serveur(i, capacite_stockage) for i in range(nbre_cache_serveur)]

        #Bien que la ligne actuel soit renseigné à 2, il s'agit de la troisième ligne dans le fichier
        ligne_actuel = 2

        #On lit la latence au datacenter (LD) et le nombre de cache auquel est connecté l'endpoint
        for i in range(nbre_endpoints):
            endpoint_actuel = lignes[ligne_actuel]
            [latence_LD, K_nbre_cache_serveur] = [int(x) for x in endpoint_actuel.split(' ')]

            #on incrémente
            ligne_actuel += 1

            #On ajoute les caches serveur auquel l'endpoint est connecté
            caches_serveurs_du_endpoint = []
            for cache_serveur_actuel in lignes[ligne_actuel:(ligne_actuel + K_nbre_cache_serveur)]:
                [cache_serveur_ID, latence_Lc] = [int(x) for x in cache_serveur_actuel.split(' ')]
                caches_serveurs_du_endpoint.append({
                    'id_cache_serveur': cache_serveur_ID,
                    'latenceLc': latence_Lc
                })

                #On incrémente
                ligne_actuel += 1

            #On créé l'objet Endpoint
            endpoint = Endpoints(i, latence_LD, caches_serveurs_du_endpoint)

            for caches_serveur in caches_serveurs_du_endpoint:
                cache_serveur_liste[caches_serveur['id_cache_serveur']].ajout_endpoint(endpoint)

            endpoints_liste.append(endpoint)

        ########################################
        # Données sur les requetes des vidéos
        ########################################

        #Création de la liste de requêtes
        requetes_liste = []

        for requete_actuel in lignes[ligne_actuel:]:
            [video_id, endpoint_id, nbre_de_demandes] = [int(x) for x in requete_actuel.split(' ')]

            #Création objet Requete
            requete = Requetes(video_id, endpoint_id, nbre_de_demandes)
            video = videos_liste[video_id]

            #Sélectionner uniquement les vidéos qui peuvent rentrer dans un cache serveur à cette étape
            #permet de ne pas avoir à copie colle cette condition dans toute les heuristiques
            if video.poid <= capacite_stockage:
                video.ajout_requete(requete)
            endpoints_liste[endpoint_id].ajout_requete(requete)
            requetes_liste.append(requete)


        return DonneesEntrees(nbre_videos,
                                nbre_endpoints,
                                nbre_requetes,
                                nbre_cache_serveur,
                                capacite_stockage,
                                videos_liste,
                                endpoints_liste,
                                cache_serveur_liste,
                                requetes_liste)

def lecture_fichier_sortie(emplacement_fichier):
    with open(emplacement_fichier) as f:
        content = f.readlines()
    N = int(content[0])
    cacheServers = []
    line = 1
    for x in range(0, N):
        cacheSsummary = content[line].split(" ")
        Cs = CacheServer(int(cacheSsummary[0]))
        cacheSsummary = cacheSsummary[1:]
        for y in cacheSsummary:
            Cs.addVideo(int(y))
        cacheServers.append(Cs)
        line = line + 1


def ecriture_fichier_sortie(cache_serveur_liste, emplacement_sortie):
    print("\n")
    cache_serveurs_rempli = [cache_serveur for cache_serveur in cache_serveur_liste if len(cache_serveur.videos) > 0]

    with open(emplacement_sortie, 'w') as fichier_sortie:
        fichier_sortie.write('{}\n'.format(len(cache_serveurs_rempli)))
        for cache_serveur in cache_serveurs_rempli:
            videos_dans_le_cache = ' '.join([str(video.id) for video in cache_serveur.videos])
            #print( cache_serveur.id," : videos [ ",videos_dans_le_cache,  end=" ] \n")
            fichier_sortie.write('{} {}\n'.format(cache_serveur.id, videos_dans_le_cache))