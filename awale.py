class awale:
    def __init__(self, nom_joueur1:str, nom_joueur2:str):
        self.nom_joueur1 = nom_joueur1
        self.nom_joueur2 = nom_joueur2
        self.score = [0, 0]             #Réserve de chaque joueur
        self.n = 0                      #Nombre de tours de jeux
        self.plateau = [4]*12           #plateau de jeu de départ
        self.joueur_actif = 1

    # def initialisation (nom_joueur1, nom_joueur2) -> dict:
    #     jeu = {}
    #     jeu ['joueur_1'] = nom_joueur1
    #     jeu ['joueur_2'] = nom_joueur2
    #     jeu ['score'] = [0 , 0] #Réserve de chaque joueur
    #     jeu ['n'] = 0 #Nombre de tours de jeux
    #     jeu ['plateau'] = [4] * 12 #plateau de jeu de départ
    #     jeu ['joueur_actif'] = 1
    #     return jeu

    def est_valide(self, case:int) -> bool:
        if case < 0  or case > 5:
            return False
        if self.plateau[case] == 0:
            return False
        adversaire_vide = sum(self.plateau[6:12]) == 0         #règle de ne pas affamer son adversaire
        if adversaire_vide and self.plateau[case] <= 5 - case:
            return False
        return True

    def semer(self, case:int) -> list:
        graine = self.plateau[case]
        self.plateau[case] = 0
        case_courante = case
        while graine > 0:
            case_courante = (case_courante+1) % 12
            self.plateau[case_courante] += 1
            graine -= 1
        return self.plateau

    def recolter(self, case_courante:int) -> tuple:
        score = 0
        while case_courante >= 6 and (self.plateau[case_courante] == 2 or self.plateau[case_courante] == 3):
            score += self.plateau[case_courante]
            self.plateau[case_courante] = 0 
            case_courante -= 1
        return(self.plateau, score)

    def tour_jeu(self, case: int) -> bool:
        if not self.est_valide(case):
            print("Case invalide, rechoisissez !")
            return True 
        graines = self.plateau[case]
        self.plateau = self.semer(case)
        case_courante = (case + graines) % 12
        self.plateau, score = self.recolter(case_courante)
        self.score[0] += score
        self.n += 1
        self.plateau = self.plateau[6:12] + self.plateau[0:6]
        return True 

    def gagnant(self) -> str:
        if self.score[0] > self.score[1]:
            return self.nom_joueur1 + " gagne !"
        elif jeu['score'][1] > jeu['score'][0]:
            return self.nom_joueur2 + " gagne !"
        else:
            return "Égalité !"
        
    def affiche(self) -> None:
        p = self.plateau
        print("Joueur 2")
        print("+----+----+----+----+----+----+")
        print(f"| {p[11]:2} | {p[10]:2} | {p[9]:2} | {p[8]:2} | {p[7]:2} | {p[6]:2} |")
        print("+----+----+----+----+----+----+")
        print(f"| {p[0]:2} | {p[1]:2} | {p[2]:2} | {p[3]:2} | {p[4]:2} | {p[5]:2} |")
        print("+----+----+----+----+----+----+")
        print("Joueur 1")
        print("  0    1    2    3    4    5  ")

    def awale_pvp (self):
        jeu_continue = True
        while jeu_continue :
            self.affiche()
            print (f"Tour de jeu : {self.joueur_actif}")
            try:
                case_choisie = int (input ("Choisissez une case :"))
            except ValueError:
                print ('Veuillez entrer un chiffre valable :')
                continue
            jeu_continue = self.tour_jeu (case_choisie)
        return self.gagnant()


jeu = awale("Alice", "Bob")
resultat = jeu.awale_pvp()
print(resultat)