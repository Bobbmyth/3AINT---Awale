class awale:
    def __init__(self, nom_joueur1: str, nom_joueur2: str):
        self.nom_joueur1 = nom_joueur1
        self.nom_joueur2 = nom_joueur2
        self.score = [0, 0]
        self.n = 0
        self.plateau = [4] * 12
        self.joueur_actif = 1
        
    def peut_nourrir(self, case: int) -> bool:
        graines = self.plateau[case]
        if graines == 0:
            return False
        pos = case
        a_semer = graines
        while a_semer > 0:
            pos = (pos + 1) % 12
            if pos == case:
                pos = (pos + 1) % 12
            if self.joueur_actif == 1 and pos >= 6:
                return True
            if self.joueur_actif == 2 and pos < 6:
                return True
        return False

    def est_valide(self, case: int) -> bool:
        if self.joueur_actif == 1:
            if case < 0 or case > 5:
                return False
            adversaire_vide = sum(self.plateau[6:12]) == 0
            if adversaire_vide and not self.peut_nourrir(case):
                return False
        else:
            if case < 6 or case > 11:
                return False
            adversaire_vide = sum(self.plateau[0:6]) == 0
            if adversaire_vide and not self.peut_nourrir(case):
                return False
        if self.plateau[case] == 0:
            return False
        return True

    def semer(self, case: int) -> list:
        graines = self.plateau[case]
        self.plateau[case] = 0
        case_courante = case
        while graines > 0:
            case_courante = (case_courante + 1) % 12
            if case_courante == case:  
                case_courante = (case_courante + 1) % 12
            self.plateau[case_courante] += 1
            graines -= 1
        return self.plateau

    def recolter(self, case_courante: int) -> tuple:
        score = 0
        cases_a_recolter = []
        if self.joueur_actif == 1:
            pos = case_courante
            while pos >= 6 and (self.plateau[pos] == 2 or self.plateau[pos] == 3):
                cases_a_recolter.append(pos)
                pos -= 1
            adversaire_apres = [self.plateau[i] for i in range(6, 12)]
            for p in cases_a_recolter:
                adversaire_apres[p - 6] = 0
            if sum(adversaire_apres) == 0:
                return self.plateau, 0
        else:
            pos = case_courante
            while pos <= 5 and (self.plateau[pos] == 2 or self.plateau[pos] == 3):
                cases_a_recolter.append(pos)
                pos -= 1
            adversaire_apres = [self.plateau[i] for i in range(0, 6)]
            for p in cases_a_recolter:
                adversaire_apres[p] = 0
            if sum(adversaire_apres) == 0:
                return self.plateau, 0

        for p in cases_a_recolter:
            score += self.plateau[p]
            self.plateau[p] = 0

        return self.plateau, score

    def tour_jeu(self, case: int) -> bool:
        if not self.est_valide(case):
            print("Case invalide, rechoisissez !")
            return True
        graines = self.plateau[case]
        self.plateau = self.semer(case)
        case_courante = (case + graines) % 12
        if graines >= 12:
            sauts = graines // 12
            case_courante = (case + graines + sauts) % 12
        self.plateau, score = self.recolter(case_courante)
        self.score[self.joueur_actif - 1] += score
        self.n += 1
        self.joueur_actif = 2 if self.joueur_actif == 1 else 1

        if self.score[0] >= 25 or self.score[1] >= 25:
            return False
        total = sum(self.plateau)
        if total <= 3:
            self.score[0] += sum(self.plateau[0:6])
            self.score[1] += sum(self.plateau[6:12])
            self.plateau = [0] * 12
            return False

        if self.joueur_actif == 1:
            camp = range(0, 6)
        else:
            camp = range(6, 12)
        
        if sum(self.plateau[c] for c in camp) == 0:
            adversaire = range(6, 12) if self.joueur_actif == 1 else range(0, 6)
            peut_nourrir = any(self.peut_nourrir(c) for c in adversaire)
            if not peut_nourrir:
                gagnant_idx = 0 if self.joueur_actif == 2 else 1
                self.score[gagnant_idx] += sum(self.plateau)
                self.plateau = [0] * 12
                return False

        return True

    def gagnant(self) -> str:
        if self.score[0] > self.score[1]:
            return self.nom_joueur1 + " gagne !"
        elif self.score[1] > self.score[0]:
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

    def awale_pvp(self):
        jeu_continue = True
        while jeu_continue:
            self.affiche()
            print(f"Score - {self.nom_joueur1}: {self.score[0]} | {self.nom_joueur2}: {self.score[1]}")
            print(f"Tour de jeu : {self.joueur_actif}")
            try:
                case_choisie = int(input("Choisissez une case : "))
            except ValueError:
                print("Veuillez entrer un chiffre valable")
                continue
            jeu_continue = self.tour_jeu(case_choisie)
        return self.gagnant()