import pygame
import sys

# Constants for display
CELL_SIZE = 60  # Taille des cases
MARGIN = 5

# Colors
CELL = (25, 25, 25)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
# Agents and Chests
BLUE = (74, 144, 226)
RED = (209, 84, 90)
GOLD = (214, 165, 58)

class Graphics:
    def __init__(self, environment):
        pygame.init()
        self.env = environment
        self.env_updated = True
        self.width = environment.tailleX * (CELL_SIZE + MARGIN) + MARGIN  # Largeur totale
        self.height = environment.tailleY * (CELL_SIZE + MARGIN) + MARGIN  # Hauteur totale
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Treasure Hunt - Multi-Agent System")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 15)  # Police pour les coordonnées, plus petite

        # Charger les assets PNG
        self.img_empty_cell = pygame.transform.scale(pygame.image.load("assets/empty_cell.png"), (CELL_SIZE, CELL_SIZE))
        self.img_drop_off = pygame.transform.scale(pygame.image.load("assets/drop_off.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_gold = pygame.transform.scale(pygame.image.load("assets/agent_gold.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_stones = pygame.transform.scale(pygame.image.load("assets/agent_stones.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_chest = pygame.transform.scale(pygame.image.load("assets/agent_chest.png"), (CELL_SIZE, CELL_SIZE))
        self.img_treasure_gold = pygame.transform.scale(pygame.image.load("assets/treasure_gold.png"), (CELL_SIZE, CELL_SIZE))
        self.img_treasure_stones = pygame.transform.scale(pygame.image.load("assets/treasure_stones.png"), (CELL_SIZE, CELL_SIZE))

    def draw_grid(self):
        self.screen.fill(WHITE)  # Fond blanc
        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                # Dessiner la cellule vide par défaut
                self.screen.blit(
                    self.img_empty_cell,
                    (
                        y * (CELL_SIZE + MARGIN) + MARGIN,  # Décalage horizontal
                        x * (CELL_SIZE + MARGIN) + MARGIN,  # Décalage vertical
                    ),
                )

                # Dessiner le dépôt
                if (x, y) == self.env.posUnload:
                    self.screen.blit(
                        self.img_drop_off,
                        (
                            y * (CELL_SIZE + MARGIN) + MARGIN,
                            x * (CELL_SIZE + MARGIN) + MARGIN,
                        ),
                    )

                # Dessiner les trésors (coffres)
                elif self.env.grilleTres[x][y] is not None:
                    if self.env.grilleTres[x][y].getType() == 1:  # Trésor or
                        self.screen.blit(
                            self.img_treasure_gold,
                            (
                                y * (CELL_SIZE + MARGIN) + MARGIN,
                                x * (CELL_SIZE + MARGIN) + MARGIN,
                            ),
                        )
                    else:  # Trésor pierres précieuses
                        self.screen.blit(
                            self.img_treasure_stones,
                            (
                                y * (CELL_SIZE + MARGIN) + MARGIN,
                                x * (CELL_SIZE + MARGIN) + MARGIN,
                            ),
                        )

                # Dessiner les agents
                if self.env.grilleAgent[x][y] is not None:
                    agent = self.env.grilleAgent[x][y]
                    if hasattr(agent, 'getType'):
                        agent_type = agent.getType()
                        if agent_type == 1:  # Agent Gold
                            self.screen.blit(
                                self.img_agent_gold,
                                (
                                    y * (CELL_SIZE + MARGIN) + MARGIN,
                                    x * (CELL_SIZE + MARGIN) + MARGIN,
                                ),
                            )
                        elif agent_type == 2:  # Agent Stones
                            self.screen.blit(
                                self.img_agent_stones,
                                (
                                    y * (CELL_SIZE + MARGIN) + MARGIN,
                                    x * (CELL_SIZE + MARGIN) + MARGIN,
                                ),
                            )
                        elif agent_type == 0:  # Agent Chest
                            self.screen.blit(
                                self.img_agent_chest,
                                (
                                    y * (CELL_SIZE + MARGIN) + MARGIN,
                                    x * (CELL_SIZE + MARGIN) + MARGIN,
                                ),
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

    def update_display(self, environment):
        pygame.time.delay(500) # Ajoute un délai en ms
        self.env = environment
        # Gérer les événements utilisateur
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.draw_grid()
        pygame.display.flip()
