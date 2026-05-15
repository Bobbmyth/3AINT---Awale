def initialisation (nom_joueur1, nom_joueur2) -> dict:
    jeu = {}
    jeu ['joueur_1'] = nom_joueur1
    jeu ['joueur_2'] = nom_joueur2
    jeu ['score'] = [0 , 0] #Réserve de chaque joueur
    jeu ['n'] = 0 #Nombre de tours de jeux
    jeu ['plateau'] = [4] * 12 #plateau de jeu de départ
    jeu ['joueur_actif'] = 1
    return jeu

def est_valide(plateau: list, case:int) -> bool:
    if case < 0  or case > 5:
        return False
    if plateau[case] == 0:
        return False
    adversaire_vide = sum(plateau[6:12]) == 0         #règle de ne pas affamer son adversaire
    if adversaire_vide and plateau[case] <= 5 - case:
        return False
    return True

def semer(plateau: list, case:int) -> list:
    graine = plateau[case]
    plateau[case] = 0
    case_courante = case
    while graine > 0:
        case_courante = (case_courante+1) % 12
        plateau[case_courante] += 1
        graine -= 1
    return plateau

def recolter(plateau:list, case_courante:int) -> tuple:
    score = 0
    while case_courante >= 6 and (plateau[case_courante] == 2 or plateau[case_courante] == 3):
        score += plateau[case_courante]
        plateau[case_courante] = 0 
        case_courante -= 1
    return(plateau, score)

def tour_jeu(jeu: dict, case: int) -> bool:
    if not est_valide(jeu['plateau'], case):
        print("Case invalide, rechoisissez !")
        return True 
    graines = jeu['plateau'][case]
    jeu['plateau'] = semer(jeu['plateau'], case)
    case_courante = (case + graines) % 12
    jeu['plateau'], score = recolter(jeu['plateau'], case_courante)
    jeu['score'][0] += score
    jeu['n'] += 1
    jeu['plateau'] = jeu['plateau'][6:12] + jeu['plateau'][0:6]
    return True 

def gagnant(jeu: dict) -> str:
    if jeu['score'][0] > jeu['score'][1]:
        return jeu['joueur_1'] + " gagne !"
    elif jeu['score'][1] > jeu['score'][0]:
        return jeu['joueur_2'] + " gagne !"
    else:
        return "Égalité !"
    
def affiche(plateau: list) -> None:
    print("Joueur 2")
    print("+----+----+----+----+----+----+")
    print(f"| {plateau[11]:2} | {plateau[10]:2} | {plateau[9]:2} | {plateau[8]:2} | {plateau[7]:2} | {plateau[6]:2} |")
    print("+----+----+----+----+----+----+")
    print(f"| {plateau[0]:2} | {plateau[1]:2} | {plateau[2]:2} | {plateau[3]:2} | {plateau[4]:2} | {plateau[5]:2} |")
    print("+----+----+----+----+----+----+")
    print("Joueur 1")
    print("  0    1    2    3    4    5  ")

def awale_pvp (nom_joueur1: str, nom_joueur2: str) -> str:
    jeu = initialisation ( nom_joueur1, nom_joueur2)
    jeu_continue = True
    while jeu_continue :
        affiche (jeu ['plateau'])
        print (f"Tour de jeu : {jeu['joueur_actif']}")
        try:
            case_choisie = int (input ("Choisissez une case :"))
        except ValueError:
            print ('Veuillez entrer un chiffre valable :')
            continue
        jeu_continue = tour_jeu (jeu, case_choisie)
    return gagnant (jeu)


