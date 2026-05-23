import pygame
from awale import awale
from gui import GUI
from human import Human
from stupidBot import StupidBot

jeu = awale("Alice", "Bot")
gui = GUI(jeu)

mode = gui.start_menu()

joueur1 = Human(jeu)
joueur2 = Human(jeu) if mode == "pvp" else StupidBot(jeu, 2)

running = True
clock = pygame.time.Clock()

while running:
    gui.dessiner()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if jeu.joueur_actif == 1:
                coup = joueur1.get_move(event.pos, gui.trous)
            elif jeu.joueur_actif == 2 and mode == "pvp":
                coup = joueur2.get_move(event.pos, gui.trous)
            else:
                coup = None
            if coup is not None:
                if not jeu.tour_jeu(coup): 
                    running = False

    if mode == "bot" and jeu.joueur_actif == 2 and running:
        pygame.time.wait(500)
        coup = joueur2.get_move()
        if coup is not None:
            if not jeu.tour_jeu(coup):
                running = False
        else:
            running = False


    clock.tick(60)

gui.ecran_fin(jeu.gagnant())
pygame.quit()