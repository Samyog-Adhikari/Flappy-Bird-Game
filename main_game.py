import os
import sys
import random
import pygame

ASSET_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets"
)

SPRITE_FILES = [
    "background-day.png",
    "base.png",
    "pipe-green.png",
    "redbird-downflap.png",
    "redbird-midflap.png",
    "redbird-upflap.png",
    "message.png",
    "gameover.png",
    "0.png",
    "1.png",
    "2.png",
    "3.png",
    "4.png",
    "5.png",
    "6.png",
    "7.png",
    "8.png",
    "9.png",
]


FPS = 60

GRAVITY = 0.48
FLAP_STRENGTH = -8.5

PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY_MS = 1400

GROUND_SCROLL_SPEED = 3
WINDOW_SCALE = 1.25


def ensure_assets():
    os.makedirs(ASSET_DIR, exist_ok=True)

    missing = []

    for filename in SPRITE_FILES:
        path = os.path.join(ASSET_DIR, filename)

        if not os.path.exists(path):
            missing.append(filename)

    if missing:
        print("\nMissing assets:")

        for filename in missing:
            print(" -", filename)

        print("\nPut your assets inside:")
        print(ASSET_DIR)

        sys.exit(1)


def load_image(name):
    path = os.path.join(ASSET_DIR, name)

    if not os.path.exists(path):
        print(f"Missing asset: {path}")
        sys.exit(1)

    return pygame.image.load(path).convert_alpha()


class Bird:

    def __init__(self, images, x, y):

        self.images = images

        self.frame = 0
        self.frame_timer = 0

        self.x = float(x)
        self.y = float(y)

        self.velocity = 0

        self.rect = self.images[0].get_rect(
            center=(int(x), int(y))
        )

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

        self.frame_timer += 1

        if self.frame_timer >= 5:

            self.frame_timer = 0

            self.frame = (
                self.frame + 1
            ) % len(self.images)

    def animate(self):

        self.frame_timer += 1

        if self.frame_timer >= 5:

            self.frame_timer = 0

            self.frame = (
                self.frame + 1
            ) % len(self.images)

    def get_image(self):

        image = self.images[self.frame]

        angle = -self.velocity * 3

        angle = max(-25, min(90, angle))

        return pygame.transform.rotate(
            image,
            angle
        )

    def draw(self, screen):

        image = self.get_image()

        draw_rect = image.get_rect(
            center=self.rect.center
        )

        screen.blit(image, draw_rect)


class PipePair:

    def __init__(self, x, gap_y, pipe_image):

        self.x = float(x)

        self.gap_y = gap_y

        self.pipe_image = pipe_image

        self.flipped_image = pygame.transform.flip(
            pipe_image,
            False,
            True
        )

        self.width = pipe_image.get_width()
        self.height = pipe_image.get_height()

        self.passed = False

    @property
    def top_rect(self):

        return pygame.Rect(
            int(self.x),
            int(
                self.gap_y
                - PIPE_GAP // 2
                - self.height
            ),
            self.width,
            self.height
        )

    @property
    def bottom_rect(self):

        return pygame.Rect(
            int(self.x),
            int(
                self.gap_y
                + PIPE_GAP // 2
            ),
            self.width,
            self.height
        )

    def update(self):

        self.x -= PIPE_SPEED

    def draw(self, screen):

        screen.blit(
            self.flipped_image,
            self.top_rect
        )

        screen.blit(
            self.pipe_image,
            self.bottom_rect
        )

    def off_screen(self):

        return (
            self.x + self.width < 0
        )


def draw_score(
    screen,
    digit_images,
    score,
    screen_width
):

    score_string = str(score)

    total_width = sum(
        digit_images[int(digit)].get_width()
        for digit in score_string
    )

    x = (
        screen_width - total_width
    ) // 2

    for digit in score_string:

        image = digit_images[int(digit)]

        screen.blit(
            image,
            (x, 30)
        )

        x += image.get_width()


def main():
    pygame.init()

    pygame.display.set_caption(
        "Flappy Bird"
    )

    ensure_assets()

    # Get the dimensions before creating the window, then convert the image.
    background_path = os.path.join(
        ASSET_DIR,
        "background-day.png"
    )

    background = pygame.image.load(
        background_path
    )

    screen_width = background.get_width()
    screen_height = background.get_height()

    screen = pygame.display.set_mode(
        (
            int(screen_width * WINDOW_SCALE),
            int(screen_height * WINDOW_SCALE)
        )
    )
    game_surface = pygame.Surface((screen_width, screen_height))

    background = background.convert_alpha()

    clock = pygame.time.Clock()

    base_image = load_image(
        "base.png"
    )

    pipe_image = load_image(
        "pipe-green.png"
    )

    message_image = load_image(
        "message.png"
    )

    gameover_image = load_image(
        "gameover.png"
    )

    digit_images = [
        load_image(f"{i}.png")
        for i in range(10)
    ]

    bird_images = [
        load_image(
            "redbird-upflap.png"
        ),
        load_image(
            "redbird-midflap.png"
        ),
        load_image(
            "redbird-downflap.png"
        )
    ]

    ground_y = (
        screen_height
        - base_image.get_height()
    )

    def new_game():

        bird = Bird(
            bird_images,
            screen_width // 3,
            screen_height // 2
        )

        return {
            "bird": bird,
            "pipes": [],
            "score": 0,
            "ground_x": 0,
            "pipe_timer": PIPE_FREQUENCY_MS,
            "state": "ready"
        }

    game = new_game()

    def spawn_pipe():

        margin = 70

        minimum = (
            margin
            + PIPE_GAP // 2
        )

        maximum = (
            ground_y
            - margin
            - PIPE_GAP // 2
        )

        gap_y = random.randint(
            minimum,
            maximum
        )

        game["pipes"].append(
            PipePair(
                screen_width + 20,
                gap_y,
                pipe_image
            )
        )

    running = True

    while running:

        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key in (
                    pygame.K_SPACE,
                    pygame.K_UP
                ):

                    if game["state"] in (
                        "ready",
                        "playing"
                    ):

                        game["state"] = "playing"

                        game["bird"].flap()

                    elif game["state"] == "dead":

                        game = new_game()

                        game["state"] = "playing"

                        game["bird"].flap()

                elif (
                    event.key == pygame.K_r
                    and game["state"] == "dead"
                ):

                    game = new_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if game["state"] in (
                    "ready",
                    "playing"
                ):

                    game["state"] = "playing"

                    game["bird"].flap()

                elif game["state"] == "dead":

                    game = new_game()

                    game["state"] = "playing"

                    game["bird"].flap()

        bird = game["bird"]

        if game["state"] == "playing":
            bird.update()
            game["pipe_timer"] += dt

            if (
                game["pipe_timer"]
                >= PIPE_FREQUENCY_MS
            ):

                game["pipe_timer"] = 0

                spawn_pipe()

            for pipe in game["pipes"]:

                pipe.update()

                if (
                    not pipe.passed
                    and pipe.x + pipe.width
                    < bird.x
                ):

                    pipe.passed = True

                    game["score"] += 1

            game["pipes"] = [
                pipe
                for pipe in game["pipes"]
                if not pipe.off_screen()
            ]

            game["ground_x"] -= (
                GROUND_SCROLL_SPEED
            )

            if (
                game["ground_x"]
                <= -base_image.get_width()
            ):

                game["ground_x"] = 0

            if bird.rect.top <= 0:

                game["state"] = "dead"

            if bird.rect.bottom >= ground_y:

                game["state"] = "dead"

            for pipe in game["pipes"]:

                if (
                    bird.rect.colliderect(
                        pipe.top_rect
                    )
                    or
                    bird.rect.colliderect(
                        pipe.bottom_rect
                    )
                ):

                    game["state"] = "dead"

                    break

        elif game["state"] == "ready":

            bird.animate()

        game_surface.blit(
            background,
            (0, 0)
        )

        for pipe in game["pipes"]:

            pipe.draw(game_surface)

        game_surface.blit(
            base_image,
            (
                int(game["ground_x"]),
                ground_y
            )
        )

        game_surface.blit(
            base_image,
            (
                int(game["ground_x"])
                + base_image.get_width(),
                ground_y
            )
        )

        bird.draw(game_surface)

        if game["state"] == "ready":

            message_rect = (
                message_image.get_rect(
                    center=(
                        screen_width // 2,
                        screen_height // 2 - 40
                    )
                )
            )

            game_surface.blit(
                message_image,
                message_rect
            )

        elif game["state"] == "playing":

            draw_score(
                game_surface,
                digit_images,
                game["score"],
                screen_width
            )

        elif game["state"] == "dead":

            draw_score(
                game_surface,
                digit_images,
                game["score"],
                screen_width
            )

            gameover_rect = (
                gameover_image.get_rect(
                    center=(
                        screen_width // 2,
                        screen_height // 2 - 40
                    )
                )
            )

            game_surface.blit(
                gameover_image,
                gameover_rect
            )

        pygame.transform.scale(game_surface, screen.get_size(), screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()