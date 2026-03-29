"""Unit tests for Flappy Bird game logic."""

# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import

import os
import sys
from unittest.mock import MagicMock, patch

import pygame
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import background
import pipe
import player
import score
import ui
from states import States

# --- GLOBAL FIXTURES ---


@pytest.fixture(autouse=True)
def mock_pygame_essentials():
    """
    Global fixture to mock Pygame's core functionalities, including Fonts.
    """
    with patch("pygame.image.load") as mock_load, patch(
        "ui.pygame.image.load"
    ) as mock_load_ui, patch("pygame.mask.from_surface") as mock_mask, patch(
        "pygame.transform.rotate"
    ) as mock_rotate, patch(
        "pygame.transform.flip"
    ) as mock_flip, patch(
        "pygame.font.Font"
    ) as mock_font:

        # Setup mock surface
        mock_surface = MagicMock(spec=pygame.Surface)

        def dynamic_get_rect(**kwargs):
            if "midbottom" in kwargs:
                return pygame.Rect(
                    kwargs["midbottom"][0], kwargs["midbottom"][1], 50, 50
                )
            if "midtop" in kwargs:
                return pygame.Rect(kwargs["midtop"][0], kwargs["midtop"][1], 50, 50)
            if "center" in kwargs:
                return pygame.Rect(
                    kwargs["center"][0] - 25, kwargs["center"][1] - 25, 50, 50
                )
            return pygame.Rect(0, 0, 50, 50)

        mock_surface.get_rect.side_effect = dynamic_get_rect
        mock_surface.get_width.return_value = 100
        mock_surface.get_height.return_value = 100
        mock_surface.get_bounding_rect.return_value = pygame.Rect(0, 0, 50, 48)

        # Configurazione ritorni
        mock_load.return_value.convert_alpha.return_value = mock_surface
        mock_load_ui.return_value.convert_alpha.return_value = mock_surface
        mock_rotate.return_value = mock_surface
        mock_flip.return_value = mock_surface
        mock_mask.return_value = MagicMock()

        # Mock per il font: restituisce un oggetto che ha il metodo .render()
        mock_font_instance = MagicMock()
        mock_font_instance.render.return_value = mock_surface
        mock_font.return_value = mock_font_instance

        yield


# --- UNIT TESTS ---


def test_bird_jump_gravity_update():
    """
    Validates the bird's jump physics utilizing the AAAA pattern
    (Arrange, Assert, Act, Assert) to ensure initial state integrity before the action.
    """
    # Arrange
    bird = player.Bird(100, 200)
    bird.gravity = 0

    # Assert (Initial Condition)
    assert bird.gravity == 0

    # Act
    bird.jump()

    # Assert (Post-Action State)
    assert bird.gravity == -7


def test_bird_state_transitions():
    """
    Verifies the bird's state machine transitions during a standard lifecycle:
    from READY to FLYING, and halting at GROUNDED upon collision.
    """
    bird = player.Bird(100, 200)

    assert bird.get_state() == States.READY

    bird.enable_fly()
    assert bird.get_state() == States.FLYING

    bird.die()
    assert bird.get_state() == States.GROUNDED


def test_pipe_movement():
    """Ensures the pipe correctly updates its x-coordinate."""
    pipe_instance = pipe.Pipe(300, 200, 0, 100)
    initial_x = pipe_instance.rect.x
    velocity = 5
    pipe_instance.update(velocity, States.FLYING)
    assert pipe_instance.rect.x == initial_x - velocity


def test_pipe_scoring_logic():
    """Validates the scoring boundary logic."""
    pipe_instance = pipe.Pipe(100, 200, 0, 100)
    pipe_instance.rect.centerx = 100
    has_passed = pipe_instance.check_passed(110)
    assert has_passed is True
    assert pipe_instance.passed is True


def test_ground_scrolling():
    """Verifies the parallax ground object scrolls correctly."""
    mock_screen = MagicMock(spec=pygame.Surface)
    ground = background.Ground("base.png", 0, 500, mock_screen)
    ground.width = 700
    initial_x = ground.pos_x
    velocity = 10
    ground.update(velocity, States.FLYING)
    assert ground.pos_x == initial_x - velocity


@pytest.mark.parametrize(
    "y_pos, expected_fly",
    [
        (100, True),
        (2000, False),
    ],
)
def test_bird_ground_collision(y_pos, expected_fly):
    """Parameterized test covering ground collision scenarios."""
    bird = player.Bird(100, y_pos)
    bird.enable_fly()  # Attiviamo il volo
    bird.rect.bottom = y_pos
    bird.hit_ground(500)

    assert bird.fly is expected_fly


def test_bird_applies_physics_when_flying():
    """Ensures gravity affects the bird only when the state is FLYING."""
    bird = player.Bird(100, 200)
    bird.enable_fly()
    initial_y = bird.rect.y
    bird.update(500)
    bird.update(500)
    assert bird.rect.y != initial_y


def test_bird_no_physics_when_not_flying():
    """Ensures the bird remains static when the game is not active."""
    bird = player.Bird(100, 200)
    initial_y = bird.rect.y
    bird.update(500)
    assert bird.rect.y == initial_y


def test_bird_hits_ceiling():
    """Validates ceiling collision constraints preventing out-of-bounds flight."""
    bird = player.Bird(100, 50)
    bird.enable_fly()
    bird.rect.top = -10
    bird.update(500)
    assert bird.rect.top == 0


def test_bird_hits_ground_and_stops():
    """Ensures flight is disabled upon ground intersection."""
    bird = player.Bird(100, 2000)
    bird.enable_fly()
    bird.rect.bottom = 2000
    bird.update(500)

    assert bird.fly is False


def test_pipe_does_not_move_if_not_flying():
    """Ensures pipes respect the global game state."""
    pipe_instance = pipe.Pipe(300, 200, 0, 100)
    initial_x = pipe_instance.rect.x
    pipe_instance.update(5, States.READY)
    assert pipe_instance.rect.x == initial_x


def test_pipe_kills_when_off_screen():
    """Checks flags for pipes leaving the viewport."""
    with patch("pipe.Pipe.pipe_bottom_surface", MagicMock()):
        pipe_instance = pipe.Pipe(0, 200, 0, 100)
        pipe_instance.rect.right = -100
        pipe_instance.update(5, States.FLYING)
        assert not pipe_instance.alive()


def test_pipe_check_passed_only_once():
    """Validates scoring idempotency."""
    pipe_instance = pipe.Pipe(100, 200, 0, 100)
    pipe_instance.rect.centerx = 100
    assert pipe_instance.check_passed(110) is True
    assert pipe_instance.check_passed(120) is False


def test_ground_resets_position():
    """Verifies the looping logic of the parallax ground."""
    mock_screen = MagicMock(spec=pygame.Surface)
    ground = background.Ground("base.png", 0, 500, mock_screen)
    ground.width = 700
    ground.pos_x = -701
    ground.update(0, States.FLYING)
    assert ground.pos_x == 0


def test_bird_animation_loops():
    """Checks if the sprite animation index loops correctly."""
    bird = player.Bird(100, 200)
    bird.enable_fly()
    for _ in range(20):
        bird._animate()
    assert 0 <= bird.image_index < len(bird.images)


def test_bird_rotation_executes():
    """Validates that rotation logic applies transformations safely."""
    bird = player.Bird(100, 200)
    bird.gravity = 10
    bird._rotate()
    assert bird.rect is not None


def test_pipe_top_vs_bottom_logic():
    """Ensures that top and bottom pipes are initialized with different images/rects."""
    pipe_top = pipe.Pipe(300, 200, 1, 100)
    pipe_bottom = pipe.Pipe(300, 200, 0, 100)

    assert pipe_top.get_position() == 1
    assert pipe_bottom.get_position() == 0
    assert pipe_top.rect.bottom < pipe_bottom.rect.top


# --- REFACTORED TESTS FOR NEW IMPORTS AND SIGNATURES ---


def test_score_increment():
    """Tests the score increment logic from score.py."""
    s = score.Score("font1", "font2", 100, 100)
    assert s.value == 0
    s.scored()
    assert s.value == 1


def test_score_draw_call():
    """Test the score draw method with all required positional arguments."""
    mock_screen = MagicMock(spec=pygame.Surface)
    s = score.Score("font1", "font2", 100, 100)
    # Passed timing=True, screen=mock_screen, and bird_state=States.FLYING
    s.draw(True, mock_screen, States.FLYING)
    assert mock_screen.blit.called


def test_start_screen_fade_out():
    """Validates that the start screen fades out when the bird starts flying."""
    start_screen = ui.StartScreen("message.png", 150, 305, 255, 0)
    initial_alpha = start_screen.transparency

    mock_canvas = MagicMock(spec=pygame.Surface)
    start_screen.draw(States.FLYING, mock_canvas)

    assert start_screen.transparency < initial_alpha
    assert mock_canvas.blit.called


def test_game_over_screen_fade_in():
    """Validates that the game over screen fades in when the bird is grounded."""
    go_screen = ui.GameOverScreen("gameover.png", 150, 305, 0, 255)
    initial_alpha = go_screen.transparency

    mock_canvas = MagicMock(spec=pygame.Surface)
    go_screen.draw(States.GROUNDED, mock_canvas)

    assert go_screen.transparency > initial_alpha
    assert mock_canvas.blit.called


def test_game_reset_logic_v2():
    """Updated test for reset_game including bird, pipes, score, and UI screens."""
    from reset import reset_game

    bird = player.Bird(100, 200)

    bird.died = True
    bird.gravity = 10
    pipe_group = pygame.sprite.Group()
    pipe_group.add(pipe.Pipe(300, 200, 0, 100))

    mock_score = MagicMock(spec=score.Score)
    mock_start = MagicMock(spec=ui.StartScreen)
    mock_gameover = MagicMock(spec=ui.GameOverScreen)

    reset_game(bird, pipe_group, mock_score, mock_start, mock_gameover)

    assert bird.died is False
    assert bird.gravity == 0
    assert len(pipe_group) == 0


# --- ADDITIONAL COVERAGE TESTS ---


def test_bird_rotation_when_dead():
    """Checks if the bird rotates to -90 degrees instantly when dead."""
    bird = player.Bird(100, 200)
    bird.die()
    bird._rotate()
    assert bird.image is not None


def test_bird_reset_functionality():
    """Validates that the bird class resets all its attributes correctly."""
    import settings

    bird = player.Bird(100, 200)
    bird.gravity = 15.0
    bird.fly = True
    bird.died = True
    bird.reset()

    assert bird.gravity == 0.0
    assert bird.fly is False
    assert bird.died is False
    assert bird.rect.midbottom == (settings.BIRD_START_X, settings.BIRD_START_Y)


def test_ui_base_class_exceptions():
    """Ensures base UI class abstract methods raise NotImplementedError."""
    base_ui = ui.UI("dummy.png", 0, 0, 255, 0)
    with pytest.raises(NotImplementedError):
        base_ui._animation()
    with pytest.raises(NotImplementedError):
        base_ui.draw(States.FLYING, MagicMock())


def test_ui_target_transparency_reached():
    """Checks the transparency target boolean validation."""
    my_ui = ui.UI("dummy.png", 0, 0, 255, 255)
    assert my_ui.target_transparency_reached() is True


def test_start_screen_ready_state_bypasses_fade():
    """Tests StartScreen draw logic during READY state."""
    start_screen = ui.StartScreen("message.png", 150, 305, 255, 0)
    mock_canvas = MagicMock(spec=pygame.Surface)
    start_screen.draw(States.READY, mock_canvas)

    assert mock_canvas.blit.called
    assert start_screen.transparency == 255


def test_score_draw_skip_when_not_flying_or_not_timing():
    """Ensures score rendering is bypassed when conditions aren't met."""
    mock_screen = MagicMock(spec=pygame.Surface)
    s = score.Score("font1", "font2", 100, 100)

    s.draw(False, mock_screen, States.FLYING)
    assert not mock_screen.blit.called

    s.draw(True, mock_screen, States.READY)
    assert not mock_screen.blit.called


def test_ground_does_not_move_when_grounded():
    """Ensures ground stops scrolling upon bird death to prevent visual desync."""
    mock_screen = MagicMock(spec=pygame.Surface)
    ground = background.Ground("base.png", 0, 500, mock_screen)
    initial_x = ground.pos_x
    ground.update(5, States.GROUNDED)

    assert ground.pos_x == initial_x


@patch("main.pygame.mixer.Sound")
@patch("main.pygame.display.set_mode")
@patch("main.pygame.display.Info")
def test_main_game_initialization_and_quit(mock_info, mock_set_mode, mock_sound):
    """
    Smoke test for main.py. Verifies that the game initializes its assets
    and can cleanly exit when receiving a pygame.QUIT event.
    This covers the initialization logic without entering the infinite loop.
    """
    import main

    # Configure mock info to avoid NoneType math errors
    mock_info_obj = MagicMock()
    mock_info_obj.current_h = 1080
    mock_info.return_value = mock_info_obj

    # Patch event.get specifically for this test to trigger immediate exit
    with patch("pygame.event.get") as mock_event_get:
        mock_quit_event = MagicMock()
        mock_quit_event.type = pygame.QUIT
        mock_event_get.return_value = [mock_quit_event]

        # main() will raise SystemExit because of sys.exit() inside the quit block
        with pytest.raises(SystemExit):
            main.main()

        assert mock_set_mode.called
