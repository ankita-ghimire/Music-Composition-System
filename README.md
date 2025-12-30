# MuseAI: AI Music Composition System

[![GitHub stars](https://img.shields.io/github/stars/ankita-ghimire/Music-Composition-System?style=social)](https://github.com/ankita-ghimire/Music-Composition-System/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

MuseAI is a full-stack web application that leverages a custom-trained AI model to generate unique musical compositions in real-time. This system serves as a creative partner for musicians and enthusiasts, translating high-level musical ideas like key, mood, and instrumentation into playable and downloadable music files.

---

### 🎥 **Project Demo**

A live deployment was attempted, but the memory requirements for the AI model's training process exceeded the limits of free-tier hosting services. To solve this, a production-ready, pre-trained model strategy was implemented.

This video demonstrates the fully functional application running locally.

**[Watch the Full Demo on YouTube](https://youtu.be/LXfl-zWmNtM)**

![Project Demo GIF]([https://LINK_TO_A_GIF.gif](https://github.com/ankita-ghimire/Music-Composition-System/blob/main/LINK_TO_A_GIF.gif?raw=true))

---

## 🌟 Core Features

*   **AI Melody Generation:** Generates unique and stylistically coherent melodies using a **Markov Chain model** trained on a curated dataset of MIDI files.
*   **Three Creative Modes:**
    *   **Solo Composer:** Creates a complete single-instrument piece with both an AI-generated melody and a harmonically-correct chord progression.
    *   **Ensemble Arranger:** Produces a multi-part composition with a lead instrument and an algorithmically generated arpeggiated accompaniment.
    *   **Chord Mix:** Allows users to input their own custom chord progressions, and the AI generates a melody specifically tailored to that harmony.
*   **Secure User Accounts:** Full user authentication system (register, login, logout) with password hashing, allowing users to save and manage their personal library of compositions.
*   **Interactive In-Browser Playback:** Utilizes **Tone.js** to provide immediate, high-quality audio previews of the generated music directly in the browser, with multi-instrument support.
*   **Standard File Export:** Allows users to download their creations as both MIDI (`.mid`) and MusicXML (`.xml`) files for use in professional DAWs and notation software.

---

## 🧠 Technical Architecture & Problem Solving

The application's core is a hybrid system of AI and rule-based algorithms. A key challenge encountered during deployment was the high memory consumption of the AI training process, which caused crashes on free-tier hosting platforms.

**The solution was to implement a professional, production-ready pre-trained model workflow:**

1.  **Offline Training:** A separate `train_ai.py` script leverages a powerful local machine to perform the memory-intensive task of training the Markov Chain model on the full `training_data` dataset.
2.  **Model Serialization:** The trained model (the Markov chain dictionary) is serialized into a lightweight, portable `trained_model.pkl` file using Python's `pickle` library.
3.  **Fast Production Loading:** The main Flask application (`app.py`) is now configured to simply load this small, pre-trained `.pkl` file on startup. This process is extremely fast and uses minimal memory.

This approach completely solves the deployment memory issue, allowing the application to start instantly and run efficiently while still benefiting from the full intelligence of the model trained on the complete dataset.

---

## 🛠️ Tech Stack

| Category         | Technology                                                                                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**      | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) |
| **Music & AI**   | ![Music21](https://img.shields.io/badge/Music21-8A2BE2?style=for-the-badge) ![Mido](https://img.shields.io/badge/Mido-4CAF50?style=for-the-badge) ![Pickle](https://img.shields.io/badge/Pickle-977A44?style=for-the-badge) |
| **Frontend**     | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white) |
| **Audio**        | ![Tone.js](https://img.shields.io/badge/Tone.js-F9A825?style=for-the-badge)                                                                                              |
| **Database**     | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white) |

---

## ⚙️ How to Run Locally

To run this project on your own machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ankita-ghimire/Music-Composition-System.git
    cd Music-Composition-System
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Train the AI Model (One-Time Step):**
    Run the training script. This will read the MIDI files from the `training_data` folder and create the `trained_model.pkl` file that the main application needs.
    ```bash
    python train_ai.py
    ```

5.  **Run the Flask Application:**
    Now you can start the web server.
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.
