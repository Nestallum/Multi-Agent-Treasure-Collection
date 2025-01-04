import pygame
import sys

# Constants for display
CELL_SIZE = 60  # Size of the grid cells
MARGIN = 5  # Space between cells

# Colors
CELL = (25, 25, 25)  # Default cell color
WHITE = (255, 255, 255)  # Background color
GRAY = (200, 200, 200)  # Unused
BLACK = (0, 0, 0)  # Unused
# Agents and Chests
BLUE = (74, 144, 226)  # Agent Gold color
RED = (209, 84, 90)  # Agent Stones color
GOLD = (214, 165, 58)  # Chest/treasure color

class Graphics:
    def __init__(self, environment):
        """
        Initialize the Graphics object with the given environment.

        Args:
        - environment: The simulation environment containing agents, treasures, and grid properties.
        """
        pygame.init()
        self.env = environment
        self.env_updated = True  # Indicates if the environment has been updated
        # Calculate screen dimensions based on grid size and cell spacing
        self.width = environment.tailleX * (CELL_SIZE + MARGIN) + MARGIN
        self.height = environment.tailleY * (CELL_SIZE + MARGIN) + MARGIN
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Treasure Hunt - Multi-Agent System")  # Window title
        self.clock = pygame.time.Clock()  # Pygame clock for managing updates
        self.font = pygame.font.SysFont(None, 20)  # Font for resource display
        self.font_small = pygame.font.SysFont(None, 15)  # Smaller font for coordinates
        
        # Load and scale image assets
        self.img_empty_cell = pygame.transform.scale(pygame.image.load("assets/empty_cell.png"), (CELL_SIZE, CELL_SIZE))
        self.img_drop_off = pygame.transform.scale(pygame.image.load("assets/drop_off.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_gold = pygame.transform.scale(pygame.image.load("assets/agent_gold.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_stones = pygame.transform.scale(pygame.image.load("assets/agent_stones.png"), (CELL_SIZE, CELL_SIZE))
        self.img_agent_chest = pygame.transform.scale(pygame.image.load("assets/agent_chest.png"), (CELL_SIZE, CELL_SIZE))
        self.img_treasure_gold = pygame.transform.scale(pygame.image.load("assets/treasure_gold.png"), (CELL_SIZE, CELL_SIZE))
        self.img_treasure_stones = pygame.transform.scale(pygame.image.load("assets/treasure_stones.png"), (CELL_SIZE, CELL_SIZE))

    def draw_grid(self):
        """
        Draw the grid and its elements (empty cells, agents, treasures, drop-off zones) on the screen.
        """
        self.screen.fill(WHITE)  # Fill the screen with a white background
        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                # Draw the default empty cell
                self.screen.blit(
                    self.img_empty_cell,
                    (
                        y * (CELL_SIZE + MARGIN) + MARGIN,  # Horizontal offset
                        x * (CELL_SIZE + MARGIN) + MARGIN,  # Vertical offset
                    ),
                )

                # Draw the drop-off point
                if (x, y) == self.env.posUnload:
                    resources = "Drop Off"
                    score = str(self.env.score)
                    self.screen.blit(  
                        self.img_drop_off,
                        (
                            y * (CELL_SIZE + MARGIN) + MARGIN,
                            x * (CELL_SIZE + MARGIN) + MARGIN,
                        ),
                    )
                    # Render text for resources and score
                    resources = self.font.render(resources, True, WHITE)
                    score = self.font.render(score, True, WHITE)
                    resources_rect = resources.get_rect(center=(
                        y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                        x * (CELL_SIZE + MARGIN) + CELL_SIZE - 6
                    ))
                    score_rect = score.get_rect(center=(
                        y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                        x * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                    ))
                    self.screen.blit(resources, resources_rect)
                    self.screen.blit(score, score_rect)  

                # Draw treasures (chests)
                elif self.env.grilleTres[x][y] is not None:
                    if self.env.grilleTres[x][y].getType() == 1:  # Gold treasure
                        treasure_img = self.img_treasure_gold
                        treasure = self.env.grilleTres[x][y]
                        resources = str(treasure.getValue())
                        status = "Closed"
                        if treasure.isOpen():
                            status = "Open!"
                    
                    else:  # Stone treasure
                        treasure_img = self.img_treasure_stones
                        treasure = self.env.grilleTres[x][y]
                        resources = str(treasure.getValue())
                        status = "Closed"
                        if treasure.isOpen():
                            status = "Open!"

                    self.screen.blit(  
                        treasure_img,
                        (
                            y * (CELL_SIZE + MARGIN) + MARGIN,
                            x * (CELL_SIZE + MARGIN) + MARGIN,
                        ),
                    )
                    # Render text for treasure value and status
                    resources = self.font.render(resources, True, WHITE)
                    status = self.font.render(status, True, WHITE)
                    resources_rect = resources.get_rect(center=(
                        y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                        x * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                    ))
                    status_rect = status.get_rect(center=(
                        y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                        x * (CELL_SIZE + MARGIN) + CELL_SIZE - 6
                    ))
                    self.screen.blit(resources, resources_rect)
                    self.screen.blit(status, status_rect)

                # Draw agents
                if self.env.grilleAgent[x][y] is not None:
                    agent = self.env.grilleAgent[x][y]
                    if hasattr(agent, 'getType'):
                        agent_type = agent.getType()
                        img = None

                        if agent_type == 1:  # Gold agent
                            img = self.img_agent_gold
                            resources = f"{agent.gold}/{agent.backPack}"
                        elif agent_type == 2:  # Stone agent
                            img = self.img_agent_stones
                            resources = f"{agent.stone}/{agent.backPack}"
                        elif agent_type == 0:  # Chest agent
                            img = self.img_agent_chest
                            resources = "Chest"

                        if img:
                            # Draw the agent's image
                            self.screen.blit(
                                img,
                                (
                                    y * (CELL_SIZE + MARGIN) + MARGIN,
                                    x * (CELL_SIZE + MARGIN) + MARGIN,
                                ),
                            )
                            # Render text for agent's resources
                            text = self.font.render(resources, True, WHITE)
                            text_rect = text.get_rect(center=(
                                y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                                x * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                            ))
                            self.screen.blit(text, text_rect)

        # Add grid coordinates (like a chessboard)
        for x in range(self.env.tailleX):
            text = self.font_small.render(str(x), True, WHITE)
            self.screen.blit(
                text,
                (
                    8,  # X coordinate on the first column
                    x * (CELL_SIZE + MARGIN) + MARGIN + 5  # Top-left position
                )
            )

        for y in range(self.env.tailleY):
            text = self.font_small.render(str(y), True, WHITE)
            self.screen.blit(
                text,
                (
                    y * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE - 14,  # Bottom-right position
                    self.height - 18  # Slightly lower in the last row
                )
            )

    def update_display(self, environment):
        """
        Update the display with the current state of the environment.

        Args:
        - environment: The updated simulation environment.
        """
        pygame.time.delay(30)  # Add a small delay for smoother animation
        self.env = environment  # Update the environment reference
        # Handle user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.draw_grid()  # Redraw the grid with updated information
        pygame.display.flip()  # Update the display
