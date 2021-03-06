#!/usr/bin/env python

from lecture_ecriture_fichiers import *
from heuristiques import *
from contraintes import *
from fonction_objective import *
from donnees_modeles import *
import numpy as np
import time
from art import tprint
import matplotlib.pyplot as plt

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
    donnees_heuristique = lecture_fichier_entree(Fichier_a_traite)

    #BorneInferieur = borne_inferieur(donnees_entrees.cache_serveur_liste)

    # BorneSuperieurGloutonne = borne_superieur_gloutonne(donnees_entrees.cache_serveur_liste,
    #                                 donnees_entrees.videos_liste)

    UB = born_supp(donnees_entrees.requetes_liste,
                   donnees_entrees.endpoints_liste,
                   donnees_entrees.cache_serveur_liste,
                   donnees_entrees.videos_liste)

    print("UB : ", UB)
    print("")

    #Application de l'heuristique
    HeuristiqueGloutonne = gloutonneDeprecated(
         donnees_heuristique.capacite_stockage,
         donnees_heuristique.videos_liste,
         donnees_heuristique.endpoints_liste,
         donnees_heuristique.cache_serveur_liste,
         donnees_heuristique.requetes_liste,
        classementCache = True,
        nettoyage_requetes_video =  True,
        GRASP =    False,
        alphaGRASP = 1)

    
    #Vérification de la validité de la solution produite
    Validite_De_La_Solution(HeuristiqueGloutonne, donnees_entrees.cache_serveur_liste, donnees_entrees.capacite_stockage,
                            Fichier_a_traite, donnees_entrees.requetes_liste,
                            donnees_entrees.endpoints_liste, donnees_entrees.videos_liste )
    # Calcul du Score Obtenu
    EvalHeuristiqueGloutonne = evaluation_heuristique(HeuristiqueGloutonne, donnees_entrees.requetes_liste, donnees_entrees.endpoints_liste,
                               donnees_entrees.videos_liste)


    donnees_entrees = lecture_fichier_entree(Fichier_a_traite)
    donnees_heuristique = lecture_fichier_entree(Fichier_a_traite)
    
    LocalSearch = try_local_search(donnees_heuristique.capacite_stockage,
                                   donnees_heuristique.videos_liste,
                                   donnees_heuristique.endpoints_liste,
                                   donnees_heuristique.cache_serveur_liste,
                                   donnees_heuristique.requetes_liste) 
    
    
    #Vérification de la validité de la solution produite
    Validite_De_La_Solution(LocalSearch, donnees_entrees.cache_serveur_liste, donnees_entrees.capacite_stockage,
                            Fichier_a_traite, donnees_entrees.requetes_liste,
                            donnees_entrees.endpoints_liste, donnees_entrees.videos_liste )

    #Calcul du Score Obtenu
    EvalLocalSearch = evaluation_heuristique(LocalSearch, donnees_entrees.requetes_liste, donnees_entrees.endpoints_liste,
                               donnees_entrees.videos_liste)



    UBLagrange = borne_sup_lagrangienne(donnees_heuristique.nbre_cache_serveur,
                                       donnees_heuristique.nbre_requetes,
                                        donnees_heuristique.nbre_videos,
                                    HeuristiqueGloutonne,
                                        donnees_heuristique.requetes_liste,
                                        donnees_heuristique.endpoints_liste)
    print("Borne lagrangienne : ", round(UBLagrange, 2))
    
    #Ecriture fichier sortie
    #ecriture_fichier_sortie(HeuristiqueGloutonne, Emplacement_Sorties + "Gloutonne.out")
    tab = [EvalHeuristiqueGloutonne, ""]

    
    
    return tab

if __name__ == '__main__':
    tprint("Projet M1 \nOptimisation")
    print("Lancement ! \n================================================== \nStatistiques d'Exécution \n")
    
    Latence_totale_sauve = []
    date_debut_heuristique = time.time()
    Latence_totale_sauve.append(exec("Instances_de_Test/me_at_the_zoo.in"))
    date_fin_heuristique = time.time()
    print("Temps d'éxécution de  l'heuristique : ",
        time.strftime("%H:%M:%S", time.gmtime(date_fin_heuristique - date_debut_heuristique)))

    print("\n================================================== \n")
    

    date_debut_heuristique = time.time()
    Latence_totale_sauve.append(exec("Instances_de_Test/trending_today.in"))
    print("Temps d'éxécution de  l'heuristique : ",
        time.strftime("%H:%M:%S", time.gmtime(date_fin_heuristique - date_debut_heuristique)))

    print("\n================================================== \n")
    
    date_debut_heuristique = time.time()
    Latence_totale_sauve.append(exec("Instances_de_Test/videos_worth_spreading.in"))
    print("Temps d'éxécution de  l'heuristique : ",
        time.strftime("%H:%M:%S", time.gmtime(date_fin_heuristique - date_debut_heuristique)))


    print("\nLatence totale sauvé sur les 3 fichiers : ", (Latence_totale_sauve)," \n==================================================  ")


    #########
    # Score
    # borne inférieur : 0
    # borne supérieur : 1 878 872
    # gloutonne : 1 567 505
    #########




