import warnings


def Validite_De_La_Solution(solution):

    if not contrainte1():
        warnings.warn("Contrainte 1 Non Satisfaite")
        return False

    if not contrainte2():
        warnings.warn("Contrainte 2 Non Satisfaite")
        return False

    if not contrainte3():
        warnings.warn("Contrainte 3 Non Satisfaite")
        return False

    if not contrainte4():
        warnings.warn("Contrainte 4 Non Satisfaite")
        return False

#Test de raise ValueError
    if not contrainte5():
        warnings.warn("Contrainte 5 Non Satisfaite")
        return False

    return True

def contrainte1():
    return True

def contrainte2():
    return True

def contrainte3():
    return True

def contrainte4():
    return True

def contrainte5():
    return True