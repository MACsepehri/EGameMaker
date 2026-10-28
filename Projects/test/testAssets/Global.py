
### MADE BY EGameMaker GAME ENGINE
### OPEN-SOURCE ENGINE
### https://github.com/MACsepehri/EGameMaker

import json
import os
import pygame

pygame.init()


class GlobalConfigure:
    def __init__(self, win, project_path):
        self.win = win
        self.project_path = project_path
        self.baseImagePath = os.path.join(
            project_path, "Assets", "Images"
        )
        self.configPath = os.path.join(
            project_path, "Assets", "Global.json"
        )

        with open(self.configPath, "r", encoding="utf-8") as file:
            self.content = json.load(file)

        self.state = self.content.get("state", "MainPage")
        self.images = {}
        self.imagePath = []

        self.__render_images()

    def __render_images(self):
        self.win.fill(tuple(self.content["background"]))

        extensions = (
            ".png", ".jpg", ".jpeg", ".webp",
            ".gif", ".bmp", ".ico"
        )

        for root, dirs, files in os.walk(self.baseImagePath):
            for filename in files:
                if filename.lower().endswith(extensions):
                    path = os.path.join(root, filename)
                    relative_path = os.path.relpath(
                        path, self.baseImagePath
                    ).replace("\", "/")

                    if relative_path not in self.images:
                        try:
                            self.images[relative_path] = (
                                pygame.image.load(path).convert_alpha()
                            )
                            self.imagePath.append(relative_path)
                        except pygame.error:
                            continue

        state_config = self.content.get("states", {}).get(
            self.state, {}
        )

        for image_data in state_config.get("images", []):
            image_path = image_data["path"]
            position = image_data.get("position", [0, 0])

            image = self.images.get(image_path)

            if image is not None:
                self.win.blit(image, position)

    def __render(self):
        self.__render_images()

    def update_state(self, new_state):
        if new_state not in self.content.get("states", {}):
            raise ValueError("State "+new_state+" does not exist")

        self.state = new_state
        self.content["state"] = new_state
        self.__render()

    def get_state(self):
        return self.content["state"]

