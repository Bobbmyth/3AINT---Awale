import pygame
import sys

BEIGE = (240, 220, 180)
BROWN = (120, 70, 20)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT = (170,170,170)
DARK = (100,100,100)

class GUI:

    def __init__(self, awale):
        pygame.init()
        self.awale = awale
        self.screen = pygame.display.set_mode((1000, 500))
        pygame.display.set_caption("Awale")
        self.font = pygame.font.SysFont("Arial", 30)
        self.trous = {}

    def dessiner(self):

        self.screen.fill(BEIGE)

        pygame.draw.rect(
            self.screen,
            BROWN,
            (50, 100, 900, 300),
            border_radius=20
        )

        rayon = 50

        for i in range(6):
            x = 150 + i * 120
            y = 180

            pygame.draw.circle(self.screen, BLACK, (x, y), rayon)
            rect = pygame.Rect(
                x - rayon,
                y - rayon,
                rayon * 2,
                rayon * 2
            )

            self.trous[11 - i] = rect
            graines = self.awale.plateau[11 - i]
            texte = self.font.render(
                str(graines),
                True,
                WHITE
            )

            self.screen.blit(texte, (x - 10, y - 10))

        for i in range(6):
            x = 150 + i * 120
            y = 320

            pygame.draw.circle(self.screen, BLACK, (x, y), rayon)
            rect = pygame.Rect(
                x - rayon,
                y - rayon,
                rayon * 2,
                rayon * 2
            )

            self.trous[i] = rect
            graines = self.awale.plateau[i]
            texte = self.font.render(
                str(graines),
                True,
                WHITE
            )

            self.screen.blit(texte, (x - 10, y - 10))
        score = self.font.render(
            f"{self.awale.score[0]} - {self.awale.score[1]}",
            True,
            BLACK
        )

        self.screen.blit(score, (430, 30))
        tour = self.font.render(
            f"Tour joueur {self.awale.joueur_actif}",
            True,
            BLACK
        )

        self.screen.blit(tour, (380, 450))
        pygame.display.flip()
    
    def start_menu(self):
        title_font = pygame.font.SysFont("Arial", 64, bold=True)
        btn_font = pygame.font.SysFont("Arial", 36)
        btn_w, btn_h = 320, 45  # Hauteur légèrement réduite (45 au lieu de 55) pour le confort visuel
        cx = (1000 - btn_w) // 2

        # Définition des zones de clics de chaque bouton (ajustement vertical global)
        pvp_button     = pygame.Rect(cx, 140, btn_w, btn_h)
        bot_button     = pygame.Rect(cx, 195, btn_w, btn_h)
        glouton_button = pygame.Rect(cx, 250, btn_w, btn_h)
        mcts_button    = pygame.Rect(cx, 305, btn_w, btn_h)
        minmax_button  = pygame.Rect(cx, 360, btn_w, btn_h)
        quit_button    = pygame.Rect(cx, 415, btn_w, btn_h)

        buttons = [
            (pvp_button,     "Joueur vs Joueur",   "pvp"),
            (bot_button,     "Joueur vs Bot",     "bot"),
            (glouton_button, "Joueur vs Glouton", "glouton"),
            (mcts_button,    "Joueur vs MCTS",    "mcts"),
            (minmax_button,  "Joueur vs MinMax",  "minmax"),
            (quit_button,    "Quitter",           "quit"),
        ]

        while True:
            self.screen.fill(BEIGE)
            mouse = pygame.mouse.get_pos()
            
            title = title_font.render("Jeu d'Awalé", True, BROWN)
            self.screen.blit(title, (1000 // 2 - title.get_width() // 2, 40))
            pygame.draw.line(self.screen, BROWN, (300, 125), (700, 125), 3)
            
            for rect, label, _ in buttons:
                hovered = rect.collidepoint(mouse)
                pygame.draw.rect(self.screen, LIGHT if hovered else DARK, rect, border_radius=10)
                text = btn_font.render(label, True, WHITE)
                self.screen.blit(text, (
                    rect.centerx - text.get_width() // 2,
                    rect.centery - text.get_height() // 2
                ))
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, _, action in buttons:
                        if rect.collidepoint(mouse):
                            if action == "quit":
                                pygame.quit()
                                sys.exit()
                            return action

            pygame.display.update()
        
    def ecran_fin(self, message: str):
        title_font = pygame.font.SysFont("Corbel", 64, bold=True)
        btn_font = pygame.font.SysFont("Corbel", 36)
        btn = pygame.Rect((1000 - 300) // 2, 320, 300, 55)

        while True:
            self.screen.fill(BEIGE)
            mouse = pygame.mouse.get_pos()

            texte = title_font.render(message, True, BROWN)
            self.screen.blit(texte, (1000 // 2 - texte.get_width() // 2, 150))

            score_font = pygame.font.SysFont("Corbel", 40)
            score = score_font.render(
                f"{self.awale.score[0]} - {self.awale.score[1]}",
                True, BLACK
            )
            self.screen.blit(score, (1000 // 2 - score.get_width() // 2, 250))

            pygame.draw.rect(self.screen, LIGHT if btn.collidepoint(mouse) else DARK, btn, border_radius=10)
            quit_text = btn_font.render("Quitter", True, WHITE)
            self.screen.blit(quit_text, (
                btn.centerx - quit_text.get_width() // 2,
                btn.centery - quit_text.get_height() // 2
            ))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn.collidepoint(mouse):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()