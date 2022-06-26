import warnings
from statistics import mean, median
import pandas as pd
from art import tprint
import matplotlib.pyplot as plt
from tabulate import tabulate
from fonction_objective import *

plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})

# Contrôle de réalisabilité
def Validite_De_La_Solution(cache_serveur_liste_solution,cache_serveur_liste, capacite_stockage, Fichier_a_traite, requetes_liste, endpoints_liste, videos_liste ):
    Validite = True

    if not contrainte1(cache_serveur_liste_solution,capacite_stockage):
        warnings.warn("\nContrainte 1 Non Satisfaite :"
                      " La capacité des cash centers n'est pas respectée")
        Validite =  False

    if not contrainte2():
        warnings.warn("\nContrainte 2 Non Satisfaite :"
                      " Au moins une requete n'est pas desservie")
        Validite =  False

    if not contrainte3():
        warnings.warn("\nContrainte 3 Non Satisfaite : "
                      "Une requête est desservie par le cache center sans que la vidéo de la requete ne soit dans celui ci ")
        Validite =  False

    if not contrainte4():
        warnings.warn("\nContrainte 4 Non Satisfaite : "
                      "Le saving de latence est mal définit")
        Validite =  False

    if not contrainte5(cache_serveur_liste_solution,cache_serveur_liste):
        warnings.warn("\nContrainte 5 Non Satisfaite : "
                      "Le cache serveur ne dessert aucun endpoint où la vidéo est demandé"
                      "La vidéo n'a pas de requetes sur les endpoints de ce cache serveur ")
        Validite =  False

    affichage(cache_serveur_liste_solution, Fichier_a_traite, capacite_stockage, requetes_liste, endpoints_liste, videos_liste)
    return Validite

def contrainte1(cache_serveur_liste_solution,capacite_stockage):
    liste_remplissage = []

    for cache_serveur in cache_serveur_liste_solution:
        #Si la somme du poid des vidéos est supérieur à la capacité du cache serveur alors la contrainte n'est pas respectée
        liste_remplissage.append( sum([video.poid for video in cache_serveur.videos]) / capacite_stockage )
  
    #On déclare la contrainte 1 comme non satisfaite si l'un des cache serveur est rempli à plus de 100%
    if any( remplissage > 1 for remplissage in liste_remplissage  ):
        return False

    return True


def contrainte2():
    #les requetes sont au moins desservie par le datacenter dans notre modèle
    return True

def contrainte3():
    # Le fichier de sortie ne précise pas le moyen de validation de la requête
    return True

def contrainte4():
    #Le saving de latence est définit dans la fonction d'évaluation des heuristiques
    return True

def contrainte5(cache_serveur_liste_solution, cache_serveur_liste ):

    #On parcours les caches serveurs de solution et ceux lus.
    #En effet lors de l'élaboration de la solution, on supprimme les requetes traité au fur et à mesure

    for cache_serveur_soluce, cache_serveur in zip(cache_serveur_liste_solution, cache_serveur_liste):

        #Liste des id de vidéos présent sur le cache serveur
        videos_id_du_cache_serveur = [video.id for video in cache_serveur_soluce.videos]

        #Requetes du cache serveur
        requetes = [endpoint.requetes_liste for endpoint in cache_serveur.endpoints]

        # Id des vidéos des requetes
        videos_id_des_requetes_du_cache_serveur =   [ requete.video_id for requete in
        [requetes_liste for requetes_liste in
         [requete for liste_requetes in requetes for requete in liste_requetes]
                                                     ]
                                                        ]
        #Si une des vidéos est présentes MAIS n'est pas demandé par une requete d'un
        # des endpoints connecté au cache serveur ALors la contrainte 5 n'est pas respectée
        if not all(video_id in videos_id_des_requetes_du_cache_serveur  for video_id in videos_id_du_cache_serveur):
            return False

    return True


def affichage(cache_serveur_liste_solution, Fichier_a_traite, capacite_stockage, requetes_liste, endpoints_liste, videos_liste):

    print("Instance en cours : ", Fichier_a_traite[18:])
    print("Modèle : ", "...")
    print("")

    liste_remplissage = []
    for cache_serveur in cache_serveur_liste_solution:
        liste_remplissage.append( sum([video.poid for video in cache_serveur.videos]) / capacite_stockage )
    print("Moyenne de remplissage cache serveur : ", mean(liste_remplissage)*100," %",
          "\nMédianne de remplissage cache serveur : ",median(liste_remplissage)*100," %",
          "\nMinimum de remplissage cache serveur : ",min(liste_remplissage)*100," %",
          "\nMaximum de remplissage cache serveur : ",max(liste_remplissage)*100," %",
          "\n")
    
    tab_id = []
    tab_stockage = []
    
    for cache_serveur in cache_serveur_liste_solution :
        tab_id.append(cache_serveur.id)
        tab_stockage.append(cache_serveur.capacite_occupe)
        
    df = pd.DataFrame([tab_stockage], columns = tab_id)
    df.rename(index={0 : 'MO pris'}, inplace=True)

    if (len(df.columns) < 20 ):
        print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
    else :
        print("To many data")



    score = evaluation_heuristique(cache_serveur_liste_solution, requetes_liste, endpoints_liste,
                               videos_liste)
    print("Gain total / Score : ", score)
  
    filter_good = (df >= 90).any()
    df_good = df.loc[:, filter_good]
    filter_moyen = ((df < 90) & (df>70)).any()
    df_moyen = df.loc[:, filter_moyen]
    filter_bad = (df <= 70).any()
    df_bad = df.loc[:, filter_bad]

    
    
    print("")
