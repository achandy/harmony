[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/achandy/harmony)](https://github.com/achandy/harmony)
[![Last Commit](https://img.shields.io/github/last-commit/achandy/harmony)](https://github.com/achandy/harmony/commits/main)


![Harmony Logo](harmony-logo.png)

**Harmony** is a CLI application that allows users to interact with Spotify and Apple Music APIs for various tasks, including authentication, exploring, and managing music data.

---

## Features

- **Spotify Integration**:
    - Authenticate with Spotify using OAuth.
    - Access Spotify tools directly via the CLI.

- **Apple Music Integration**:
    - Authenticate with Apple Music using a local HTTP server and MusicKit.js.
    - Access Apple Music tools directly via the CLI.
    - 
---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/harmony.git
   cd harmony
   ```

2. Install dependencies, including `pytoml`:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have properly configured the `pyproject.toml` file, as it sets up the project environment and dependencies. To install your Harmony CLI tool as a command-line application, run:

   ```bash
   pip install .
   ```

   This will set up the application for direct execution and add the `harmony` command to your PATH.

4. Create a `.env` file in the root directory and provide the required environment variables:

   - For Spotify:
     - `SPOTIFY_CLIENT_ID`
     - `SPOTIFY_CLIENT_SECRET`

   - For Apple Music:
     - `APPLE_KEY_ID`
     - `APPLE_TEAM_ID`
     - `APPLE_PRIVATE_KEY`

---

## Usage

Run the Harmony CLI directly using:

   ```bash
   harmony
   ```

The main menu will appear:
   - Authenticate with Spotify or Apple Music for session-specific tools.
   - Utilize the Spotify and Apple Music submenus to perform actions like searching for songs, albums, or artists.

---

## Prerequisites

- **Python**: Requires Python 3.7 or higher.
- **Dependencies**:
    - Ensure all required libraries are installed via `requirements.txt`.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Developed by **Allan Chandy**  
Email: *chandyallan@gmail.com*

---