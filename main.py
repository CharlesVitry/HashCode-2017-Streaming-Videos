#!/usr/bin/env python

from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
from donnees_modeles import *
import time

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
    input_heuristique = lecture_fichier_entree(Fichier_a_traite)

    #BorneInferieur = borne_inferieur(donnees_entrees.cache_serveur_liste)

    # BorneSuperieurGloutonne = borne_superieur_gloutonne(donnees_entrees.cache_serveur_liste,
    #                                 donnees_entrees.videos_liste)

    UB = born_supp(input_heuristique.requetes_liste, input_heuristique.endpoints_liste, input_heuristique.cache_serveur_liste, input_heuristique.videos_liste)
    print("UB : ", UB)
    
    date_debut_heuristique = time.time()
    #Application de l'heuristique
    HeuristiqueGloutonne = gloutonne(
         input_heuristique.capacite_stockage,
         input_heuristique.videos_liste,
         input_heuristique.endpoints_liste,
         input_heuristique.cache_serveur_liste,
         input_heuristique.requetes_liste,
         False,
         True,
        1)
    #Vérification de la validité de la solution produite
    Validite_De_La_Solution(HeuristiqueGloutonne, donnees_entrees.cache_serveur_liste,     donnees_entrees.capacite_stockage )
    

    print("")
    
    donnees_entrees = lecture_fichier_entree(Fichier_a_traite)
    input_heuristique = lecture_fichier_entree(Fichier_a_traite)
    Trajectory = trajectory(
         input_heuristique.capacite_stockage,
         input_heuristique.videos_liste,
         input_heuristique.endpoints_liste,
         input_heuristique.cache_serveur_liste,
         input_heuristique.requetes_liste
         )

    
    #Vérification de la validité de la solution produite
    Validite_De_La_Solution(Trajectory, donnees_entrees.cache_serveur_liste,     donnees_entrees.capacite_stockage )

    
    

    date_fin_heuristique = time.time()
    print("Temps d'éxécution de  l'heuristique : ",
          time.strftime("%H:%M:%S", time.gmtime(date_fin_heuristique - date_debut_heuristique)))

    


    #Ecriture fichier sortie
    #ecriture_fichier_sortie(HeuristiqueGloutonne, Emplacement_Sorties + "resultat.out")

    # Calcul du Score Obtenu
    x = evaluation_heuristique(HeuristiqueGloutonne, donnees_entrees.requetes_liste, donnees_entrees.endpoints_liste, donnees_entrees.videos_liste)
    y = evaluation_heuristique(Trajectory, donnees_entrees.requetes_liste, donnees_entrees.endpoints_liste, donnees_entrees.videos_liste)

    result = [x, y]
    return result



if __name__ == '__main__':
    print("Lancement ! \n================== \nStatistiques d'Exécution \n")
    Latence_totale_sauve = []
    Latence_totale_sauve.append(exec("Instances_de_Test/me_at_the_zoo.in"))
    #Latence_totale_sauve.append(exec("Instances_de_Test/trending_today.in"))
    #Latence_totale_sauve.append(exec("Instances_de_Test/videos_worth_spreading.in"))

    print("\nLatence totale sauvé sur les 3 fichiers : ", (Latence_totale_sauve)," \n================== ")


    #########
    # Score
    # borne inférieur : 0
    # borne supérieur : 1 878 872
    # gloutonne : 1 567 505
    #########




