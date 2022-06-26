from dataclasses import dataclass, field
import random


@dataclass
class Videos:
    id: int
    poid: int
    requetes_liste: list = field(default_factory=list)
    efficacite_par_endpoint: dict = field(default_factory=dict)
    efficacite_divise: dict = field(default_factory=dict)
    poid_divise: None = None

    def supp_requete(self, endpoint_id):
        self.requetes_liste = [requete for requete in self.requetes_liste if requete.endpoint_id != endpoint_id]

    def rentabilite_video(self, cash_serveur):
        liste_id_endpoint_cash_serveur = [endpoint.id for endpoint in cash_serveur.endpoints]
        requetes_video_au_cache = [requete for requete in self.requetes_liste if
                                   requete.endpoint_id in liste_id_endpoint_cash_serveur]

        rentabilite = 0
        for requete in requetes_video_au_cache:
            rentabilite += self.rapport_divise(requete.endpoint_id) * \
                           (objet_par_id(cash_serveur.endpoints, requete.endpoint_id)[0].latence_datacenter_divise_LD -
                            objet_par_id(cash_serveur.endpoints, requete.endpoint_id)[
                                0].getter_latence_aux_caches_serveurs_divise(cash_serveur.id))
        return rentabilite

    def ajout_requete(self, requete):
        self.requetes_liste.append(requete)

    def rapport_par_endpoint(self, endpoint_id):
        return self.efficacite_par_endpoint_fonction(endpoint_id) / self.poid

    def rapport_divise(self, endpoint_id):
        return self.efficacite_divise_fonction(endpoint_id) / self.poid

    def poid_divise_fonction(self, poid_videos_total):
        self.poid_divise = (self.poid / poid_videos_total)

    def efficacite(self):
        return sum([requete.nombre_de_requetes for requete in self.requetes_liste])

    def efficacite_par_endpoint_fonction(self, endpoint_id):
        if endpoint_id in self.efficacite_par_endpoint:
            return self.efficacite_par_endpoint[endpoint_id]
        efficacite = sum(
            [requete.nombre_de_requetes for requete in self.requetes_liste if requete.endpoint_id == endpoint_id])
        self.efficacite_par_endpoint[endpoint_id] = efficacite
        return efficacite

    def efficacite_divise_fonction(self, endpoint_id):
        if endpoint_id in self.efficacite_divise:
            return self.efficacite_divise[endpoint_id]
        efficacite = sum([requete.nombre_de_requetes_divise for requete in self.requetes_liste if
                          requete.endpoint_id == endpoint_id])
        self.efficacite_divise[endpoint_id] = efficacite
        return efficacite


@dataclass
class Endpoints:
    id: int
    latence_datacenter_LD: int
    latence_aux_caches_serveurs: list
    latence_datacenter_divise_LD: None = None
    requetes_liste: list = field(default_factory=list)
    requetes_liste_a_traite: list = field(default_factory=list)
    latence_aux_caches_serveurs_divise: list = field(default_factory=list)
    dict_latence_aux_caches_serveurs_divise: dict = field(default_factory=dict)

    def latence_divise_fonction(self, latence_somme_totale):
        self.latence_datacenter_divise_LD = self.latence_datacenter_LD / latence_somme_totale
        for cache_serveur in self.latence_aux_caches_serveurs:
            self.latence_aux_caches_serveurs_divise.append({
                'id_cache_serveur': cache_serveur['id_cache_serveur'],
                'latenceLc_divise': cache_serveur['latenceLc'] / latence_somme_totale
            })

    def getter_latence_aux_caches_serveurs(self, cache_serveur_id):
        return [cache_serveur['latenceLc'] for cache_serveur in self.latence_aux_caches_serveurs if
                cache_serveur_id == cache_serveur['id_cache_serveur']][0]

    def getter_latence_aux_caches_serveurs_divise(self, cache_serveur_id):
        if cache_serveur_id in self.dict_latence_aux_caches_serveurs_divise:
            return self.dict_latence_aux_caches_serveurs_divise[cache_serveur_id]
        efficacite = [cache_serveur['latenceLc_divise'] for cache_serveur in self.latence_aux_caches_serveurs_divise if
                      cache_serveur_id == cache_serveur['id_cache_serveur']][0]
        self.dict_latence_aux_caches_serveurs_divise[cache_serveur_id] = efficacite
        return efficacite

    def supp_requete_traite(self, video_id):
        self.requetes_liste_a_traite = [requete for requete in self.requetes_liste_a_traite if
                                        requete.video_id != video_id]

    def ajout_requete(self, requete):
        self.requetes_liste.append(requete)


@dataclass
class Cache_Serveur:
    id: int
    capacite: int
    capacite_occupe: int = 0
    importance: float = 0
    importance_divise: float = 0
    endpoints: list = field(default_factory=list)
    videos: list = field(default_factory=list)
    dict_videos: dict = field(default_factory=dict)

    def remplissage_aleatoire_dict(self, videos_liste):
        dict_complementaire = {}
        for video in videos_liste:
            self.dict_videos[video.id] = bool(random.getrandbits(1))
            dict_complementaire[video.id] = not self.dict_videos[video.id]
        return dict_complementaire

    def construction_dict(self, videos_liste):
        for video in videos_liste:
            self.dict_videos[video.id] = False

    def videos_liste_a_dict(self):
        for video in self.videos:
            self.dict_videos[video.id] = True

    def dictionnaire_a_liste_videos(self, videos_liste):
        # On vide la liste de vidéos
        self.videos = []

        # On ajoute les vidéos qui sont en "Vraie" dans le dictionnaire
        for video in videos_liste:
            if self.dict_videos[video.id]:
                self.videos.append(video)

    def importance_divise_fonction(self, importance_somme):
        self.importance_divise = self.importance / importance_somme

    def suppression_requete(self, video_id, endpoint_id):
        self.requetes_liste = [requete for requete in self.requetes_liste if
                               requete.endpoint_id != endpoint_id and requete.video_id != video_id]

    def ajout_endpoint(self, endpoint):
        self.endpoints.append(endpoint)

    def ajout_video(self, video):
        self.videos.append(video)

    def importance_du_cache(self, videos):
        importance = 0
        # on parcours les endpoints du cache serveurs
        for endpoint in self.endpoints:
            video_rapport = 0
            # on parcours les vidéos des requetes de ces endpoints
            for requete in endpoint.requetes_liste:
                video = videos[requete.video_id]
                # on somme le gain de ces vidéos
                video_rapport += video.rapport_divise(endpoint.id)

            # On fait la différence de la latence au datacenter et au cache serveur pondéré par le gain totale des vidéos
            importance += (endpoint.latence_datacenter_divise_LD - endpoint.getter_latence_aux_caches_serveurs_divise(
                self.id)) * video_rapport
        self.importance = importance
        return importance


@dataclass
class Requetes:
    video_id: int
    endpoint_id: int
    nombre_de_requetes: int
    nombre_de_requetes_divise: None = None

    def nombre_de_requetes_divise_fonction(self, somme_requetes):
        self.nombre_de_requetes_divise = self.nombre_de_requetes / somme_requetes


@dataclass
class DonneesEntrees:
    nbre_videos: int
    nbre_endpoints: int
    nbre_requetes: int
    nbre_cache_serveur: int
    capacite_stockage: int
    videos_liste: list[Videos]
    endpoints_liste: list[Endpoints]
    cache_serveur_liste: list[Cache_Serveur]
    requetes_liste: list[Requetes]

    def Nettoyage_donnes(self):
        None

    def EfficaciteVideos(self):
        None

    def EfficaciteRequetes(self):
        None

    def EfficaciteEndpoints(self):
        None


# Fonction de recherche par ID dans les listes,
# une structure utilisant des dictionnaires aurait été meilleur
def objet_par_id(liste, id):
    objet = [o for o in liste if o.id == id]
    return objet
