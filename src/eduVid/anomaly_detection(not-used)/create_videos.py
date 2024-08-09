from PIL import Image, ImageDraw

import os
import numpy as np
import imageio
import pygame


class PygameDrawApp:
    def __init__(self, data_structure_name):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption('Draw and Record')
        self.clock = pygame.time.Clock()
        self.screen.fill((255, 255, 255))
        self.drawing = False
        self.last_pos = None
        self.draw_color = (0, 0, 0)
        self.radius = 5

        # Create directory if it does not exist
        self.data_structure_name = data_structure_name
        self.save_path = f"train/data_videos/{self.data_structure_name}"
        os.makedirs(self.save_path, exist_ok=True)

        # Get the current video number
        self.video_number = len(os.listdir(self.save_path)) + 1
        self.video_filename = f"{self.save_path}/video_{self.video_number}.mp4"

        # Initialize the video writer
        self.video_writer = imageio.get_writer(self.video_filename, fps=30)

    def draw(self, pos):
        if self.last_pos is not None:
            pygame.draw.line(self.screen, self.draw_color, self.last_pos, pos, self.radius)
        self.last_pos = pos

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.drawing = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drawing = False
                    self.last_pos = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.drawing:
                        self.draw(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.screen.fill((255, 255, 255))
                    elif event.key == pygame.K_s:
                        pygame.image.save(self.screen, "drawing.png")
                
            # Capture the current screen as a frame
            pil_string_image = pygame.image.tostring(self.screen, "RGB")
            pil_image = Image.frombytes("RGB", (1024, 768), pil_string_image)
            frame = np.array(pil_image)
            self.video_writer.append_data(frame)
                        
            pygame.display.flip()
            self.clock.tick(30)
        
        self.video_writer.close()
        pygame.quit()

def run_draw_app(data_structure_name):
    app = PygameDrawApp(data_structure_name)
    app.run()

def main():
    data_structure_name = "..." # Data Structure to Draw
    run_draw_app(data_structure_name)

if __name__ == "__main__":
    main()