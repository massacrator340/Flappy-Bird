# <img src="assets/Game Objects/yellowbird-1.png" width = 40> Flappy-Bird

A Python implementation of the classic Flappy Bird game built with the Pygame library.

## 🕹️ Game Features

* **Player Movement**: Gravity-based physics and responsive jump mechanics.

* **Collision System**: Accurate collision detection between the player, obstacles, and ground.

* **Obstacle Generation**: Procedural spawning of pipes with randomized heights.

* **Score Tracking**: Real-time score display using custom vector-based fonts.

## 📋 Prerequisites

Before starting, ensure you have **Python 3.10 or higher** installed.

1.  **Download Python**: Visit the official [Python Downloads page](https://www.python.org/downloads/).
2.  **Windows Users (Crucial)**: During installation, you **must check the box** that says **"Add Python to PATH"**.
    
3.  **Verify**: Open your terminal and type `python --version`.

## 🛠️ Installation

To run this project locally on your machine, follow these steps:

1. **Clone the repository:**
Open your terminal and run the following command to download the project:

    ```sh
    git clone https://github.com/Fabulousqueen/Flappy-Bird.git
    ```

2.  **Create a Virtual Environment (Recommended)**:
    This keeps your system clean from project-specific libraries.
    
    ```sh
    python -m venv venv
    ```
    * **Activate (Windows)**: `venv\Scripts\activate`
    * **Activate (macOS/Linux)**: `source venv/bin/activate`

3.  **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Launch the game**:
    ```sh
    cd src
    python main.py
    ```

## 👾 How to play?

1. **Jump:** Press the `SPACE` bar or `Left Click` the mouse to flap your wings and defy gravity;

2. **Avoid Obstacles:** Navigate through the gaps between the pipes;

3. **Score:** Each successful pass through a pair of pipes increases your score;

4. **Game Over:** If you hit a pipe or the ground, the game is over;

5. **Restart Game:** You can restart the game by pressing `R` or `Right Click` the mouse.

## 🔧 Troubleshooting

### 🔊 Audio Issues
* **System Mixer**: If you don't hear sounds, check that the application is not muted in your OS volume mixer.
    
* **Volume Constant**: You can adjust `VOLUME_SFX` in `src/settings.py`.
* **Hardware**: Ensure your audio output device is connected *before* launching the game.

## 👥 Contributors

* [Fabulousqueen](https://github.com/Fabulousqueen/)
* [Shana95](https://github.com/Shana95/)
* [Massy340](https://github.com/massacrator340?tab=overview&from=2024-12-01&to=2024-12-31)

## 🎨 Credits

* **Game assets:** created by **kosresetr55** from itch.io ([Link here](https://kosresetr55.itch.io/flappy-bird-assets-by-kosresetr55))
* **Flappychar.ttf**: Based on the [FlappyBirdy](https://www.dafont.com/flappybirdy.font) font by **GeronimoFonts** via DaFont.

## ⚖️ License
This project is licensed under the **GNU GPLv3 License**
