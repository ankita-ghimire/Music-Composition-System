# AI Music Composition System

This is the final project for our B.Sc.CSIT program, demonstrating a collaborative AI system for music generation. The web application allows users to create unique musical pieces by specifying a key and mood, which are then used to generate a melody and a corresponding chord progression.

---

## 🎵 Features

*   **AI Melody Generation:** Utilizes a **Markov Chain** model trained on a dataset of musical pieces to generate stylistically coherent melodies.
*   **Rule-Based Chord Generation:** Employs an **Expert System** based on music theory rules (via the `music21` library) to create harmonically correct chord progressions.
*   **Interactive Web Interface:** A user-friendly web app built with **Flask** and **Bootstrap** allows for easy composition.
*   **User Authentication:** Users can register and log in to save and manage their personal compositions.
*   **Persistent Storage:** Compositions are saved to a **SQLite** database, linked to user accounts.
*   **In-Browser Playback:** Allows users to listen to their compositions directly on the "My Compositions" page using **MIDI.js**.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **AI & Musicology:** music21
*   **Database:** SQLite
*   **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
*   **Audio Playback:** MIDI.js

---

## 🚀 Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites
*   Python 3.9+
*   Git

### 2. Clone the Repository
```bash
git clone https://github.com/ankita-ghimire/Music-Composition-System.git
cd Music-Composition-System

3. Set Up the Virtual Environment

It is highly recommended to use a virtual environment.
# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.\.venv\Scripts\activate```

### 4. Install Dependencies
All required Python libraries are listed in `requirements.txt`.
```bash
pip install -r requirements.txt

5. Important: Training Data

This repository does not include the MIDI training data due to its large size.

    Action Required: Please download the training_data.zip file from the following link:
   https://drive.google.com/drive/folders/17x1gyoVA5pV0geZvP_gBOnlDoei8NJdb?usp=drive_link

    Unzip the file and place the training_data folder in the root directory of this project. The AI model will not be able to train without this data.

    6. Run the Application

Once the setup is complete, you can start the Flask web server.
code Bash
python server.py
The application will then be available at http://1227.0.0.1:5000 in your web browser.