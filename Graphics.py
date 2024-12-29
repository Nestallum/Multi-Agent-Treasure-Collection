import pygame
import sys

# Constants for display
CELL_SIZE = 60
MARGIN = 4

# Colors
CELL = (25, 25, 25)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
# Agents and Chests
BLUE = (74, 144, 226)
RED = (209, 84, 90)
GOLD = (214, 165, 58)


# class Graphics:
#     def __init__(self, environment):
#         pygame.init()
#         self.env = environment
#         self.width = environment.tailleX * (CELL_SIZE + MARGIN) + MARGIN
#         self.height = environment.tailleY * (CELL_SIZE + MARGIN) + MARGIN
#         self.screen = pygame.display.set_mode((self.width, self.height))
#         pygame.display.set_caption("Treasure Hunt - Multi-Agent System")
#         self.clock = pygame.time.Clock()

#     def draw_grid(self):
#         self.screen.fill(WHITE)  # Fond noir comme l'ancien affichage
#         for x in range(self.env.tailleX):
#             for y in range(self.env.tailleY):
#                 # Couleur par défaut pour une cellule vide
#                 color = CELL

#                 # Vérifie si la cellule est le dépôt
#                 if (x, y) == self.env.posUnload:
#                     color = GRAY

#                 # Vérifie s'il y a un trésor (coffres représentés par des carrés)
#                 elif self.env.grilleTres[x][y] is not None:
#                     if self.env.grilleTres[x][y].getType() == 1:
#                         color = GOLD
#                     else:
#                         color = RED

#                 # Dessine la cellule (grille avec fond gris par défaut)
#                 pygame.draw.rect(
#                     self.screen,
#                     color,
#                     [
#                         y * (CELL_SIZE + MARGIN) + MARGIN,
#                         x * (CELL_SIZE + MARGIN) + MARGIN,
#                         CELL_SIZE,
#                         CELL_SIZE,
#                     ],
#                 )

#                 # Vérifie s'il y a un agent (agents représentés par des cercles)
#                 if self.env.grilleAgent[x][y] is not None:
#                     agent = self.env.grilleAgent[x][y]
#                     if hasattr(agent, 'getType'):
#                         agent_type = agent.getType()
#                         if agent_type == 1:  # Agent Gold
#                             color = GOLD
#                         elif agent_type == 2:  # Agent Stones
#                             color = RED
#                         elif agent_type == 0:  # Agent Chest
#                             color = BLUE

#                         pygame.draw.circle(
#                             self.screen,
#                             color,
#                             (
#                                 y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
#                                 x * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
#                             ),
#                             CELL_SIZE // 2
#                         )

#     def update_display(self):
#         self.draw_grid()
#         pygame.display.flip()

#     def run(self):
#         running = True
#         while running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#             self.update_display()
#             self.clock.tick(30)

#         pygame.quit()
#         sys.exit()

class Graphics:
    def __init__(self, environment):
        pygame.init()
        self.env = environment
        self.width = environment.tailleX * (CELL_SIZE + MARGIN) + MARGIN  # Largeur totale
        self.height = environment.tailleY * (CELL_SIZE + MARGIN) + MARGIN  # Hauteur totale
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Treasure Hunt - Multi-Agent System")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 15)  # Police pour les coordonnées, plus petite

    def draw_grid(self):
        self.screen.fill(WHITE)  # Fond blanc
        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                # Couleur par défaut pour une cellule vide
                color = CELL

                # Vérifie si la cellule est le dépôt
                if (x, y) == self.env.posUnload:
                    color = GRAY

                # Vérifie s'il y a un trésor (coffres représentés par des carrés)
                elif self.env.grilleTres[x][y] is not None:
                    if self.env.grilleTres[x][y].getType() == 1:
                        color = GOLD
                    else:
                        color = RED

                # Dessine la cellule (grille avec fond gris par défaut)
                pygame.draw.rect(
                    self.screen,
                    color,
                    [
                        y * (CELL_SIZE + MARGIN) + MARGIN,  # Décalage horizontal
                        x * (CELL_SIZE + MARGIN) + MARGIN,  # Décalage vertical
                        CELL_SIZE,
                        CELL_SIZE,
                    ],
                )

                # Vérifie s'il y a un agent (agents représentés par des cercles)
                if self.env.grilleAgent[x][y] is not None:
                    agent = self.env.grilleAgent[x][y]
                    if hasattr(agent, 'getType'):
                        agent_type = agent.getType()
                        if agent_type == 1:  # Agent Gold
                            color = GOLD
                        elif agent_type == 2:  # Agent Stones
                            color = RED
                        elif agent_type == 0:  # Agent Chest
                            color = BLUE

                        pygame.draw.circle(
                            self.screen,
                            color,
                            (
                                y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                                x * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                            ),
                            CELL_SIZE // 2.5
                        )

        # Ajouter les coordonnées externes (comme un échiquier)
        for x in range(self.env.tailleX):
            text = self.font_small.render(str(x), True, WHITE)
            self.screen.blit(
                text,
                (
                    8,  # Coordonnée X sur la première colonne, légèrement à droite
                    x * (CELL_SIZE + MARGIN) + MARGIN + 5  # Placée en haut à gauche de chaque case
                )
            )

        for y in range(self.env.tailleY):
            text = self.font_small.render(str(y), True, WHITE)
            self.screen.blit(
                text,
                (
                    y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE - 14,  # Coordonnée Y ajustée en bas à droite
                    self.height - 18  # Légèrement plus bas dans la dernière ligne
                )
            )

    def update_display(self):
        self.draw_grid()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update_display()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()