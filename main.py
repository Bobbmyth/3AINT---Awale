from copy import deepcopy
import pygame
from awale import awale
from gui import GUI
from human import Human
from stupidBot import StupidBot
from mcts import MCTS

jeu = awale("Alice", "Bot")
gui = GUI(jeu)

mode = gui.start_menu()

joueur1 = Human(jeu)
joueur2 = Human(jeu) if mode == "pvp" else StupidBot(jeu, 2)
mcts = MCTS(iterations_max=500) if mode == "mcts" else None

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

    if jeu.joueur_actif == 2 and running and mode in ("bot", "mcts"):
        pygame.time.wait(500)
        if mode == "bot":
            coup = joueur2.get_move()
        else:
            coup = mcts.determiner_coup(
                deepcopy(jeu.plateau),
                deepcopy(jeu.score),
                jeu.joueur_actif
            )
        if coup is not None:
            if not jeu.tour_jeu(coup):
                running = False
        else:
            running = False


    clock.tick(60)

gui.ecran_fin(jeu.gagnant())
pygame.quit()