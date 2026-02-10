import asyncio
import pygame
from src.game import Game
from src.settings import WINDOW_WIDTH, WINDOW_HEIGHT
from src.scenes.main_menu import MainMenuScene
from src.scenes.personality_test import PersonalityTestScene
from src.scenes.avatar_select import AvatarSelectScene
from src.scenes.dress_up import DressUpScene
from src.scenes.college_app import CollegeAppScene
from src.scenes.decision import DecisionScene
from src.scenes.export import ExportScene


async def main():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
    pygame.display.set_caption("HYBRIS: Create Your Applicant")

    scenes = {
        "MAIN_MENU": MainMenuScene(),
        "PERSONALITY_TEST": PersonalityTestScene(),
        "AVATAR_SELECT": AvatarSelectScene(),
        "DRESS_UP": DressUpScene(),
        "COLLEGE_APP": CollegeAppScene(),
        "DECISION": DecisionScene(),
        "EXPORT": ExportScene(),
    }

    game = Game(screen, scenes, "MAIN_MENU")
    await game.run()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
