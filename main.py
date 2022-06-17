from lecture_ecriture_fichiers import lecture_fichier
from heuristiques import *


def exec(Fichier_a_traite):
    #Lecture du fichier d'entrée
    result = lecture_fichier(Fichier_a_traite)

    #Application de l'heuristique
    HeuristiqueGloutonne = gloutonne(
        result.capacite_stockage,
        result.videos_liste,
        result.endpoints_liste,
        result.cache_serveur_liste,
        result.requetes_liste
                                )


    #print(HeuristiqueGloutonne)
    #Vérification de la validité de la solution produite
    #lorem ipsum

    #Calcul du Score Obtenu
    #write_file(cache_server, "Resultat_Heuristiques/me_at_the_zoo.out")


if __name__ == '__main__':
    print("Lancement ! ")
    exec("Instances_de_Test/me_at_the_zoo.in")

