from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
########################
# Configuration
Emplacement_Entrees = "Instances_de_Test/"
Emplacement_Sorties = "Resultat_Heuristiques/"

Noms_Entrees_Sorties = {"me_at_the_zoo.in" : "me_at_the_zoo.out" ,
                        "trending_today.in" : "trending_today.out",
                        "videos_worth_spreading.in" : "videos_worth_spreading.out"}

###########################

def exec(Fichier_a_traite):
    #Lecture du fichier d'entrée
    donnees_entrees = lecture_fichier_entree(Fichier_a_traite)

    #Application de l'heuristique
    HeuristiqueGloutonne = gloutonne(
        donnees_entrees.capacite_stockage,
        donnees_entrees.videos_liste,
        donnees_entrees.endpoints_liste,
        donnees_entrees.cache_serveur_liste,
        donnees_entrees.requetes_liste
                                )

    #Vérification de la validité de la solution produite
    pass

    #Ecriture fichier sortie
    #ecriture_fichier_sortie(HeuristiqueGloutonne, Emplacement_Sorties + "resultat.out")

    # Calcul du Score Obtenu
    return evaluation_heuristique(HeuristiqueGloutonne, donnees_entrees.requetes_liste, donnees_entrees.endpoints_liste, donnees_entrees.videos_liste)




if __name__ == '__main__':
    print("Lancement ! ")
    Latence_totale_sauve = []
    Latence_totale_sauve.append(exec("Instances_de_Test/me_at_the_zoo.in"))
    #Latence_totale_sauve.append(exec("Instances_de_Test/trending_today.in"))
    #Latence_totale_sauve.append(exec("Instances_de_Test/videos_worth_spreading.in"))

    print("Latence totale sauvé sur les 3 fichiers : ", sum(Latence_totale_sauve))

