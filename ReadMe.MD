# Typing Speed Test ⌨️

A cross-platform, desktop-based typing speed application built entirely in standard Python. This project features a custom-built UI that brings modern design principles (rounded corners, pill-shaped buttons, dynamic scaling) to native `tkinter`.

## 🚀 Key Features

*   **Dual Modes:** 
    *   **Standard:** Full punctuation and capitalisation for a realistic typing challenge.
    *   **Raw:** Automatically strips punctuation and standardises to lowercase for pure speed runs.
*   **Precision Tracking:** Calculates Words Per Minute (WPM) and Characters Per Minute (CPM). The 60-second timer strictly defers activation until the user's first keystroke.
*   **Analytics:** Post-test analytics provide a breakdown of both misspelt and skipped words.
*   **Persistent State:** High scores are tracked independently for both modes and automatically saved to a local `highscores.json` file.
*   **Dynamic UI Scaling:** Font sizes and container dimensions automatically calculate and adjust based on the application's window size.

## 🧠 Technical Architecture

This application strictly adheres to Object-Oriented Programming (OOP) principles, utilising a Model-View-Controller (MVC) pattern to separate state management, business logic, and UI rendering.

*   **The Model (`TypingEngine`):** Operates entirely independently of the GUI. It tokenises reference texts, handles single-word lookahead logic (to detect if a user skipped a word rather than misspelling it), supports state rollback on backspace, and calculates character-accurate WPM/CPM metrics.
* **The Views (`BaseScreen` & Subclasses):** The visual layer is divided into five modular screen states (`WelcomeScreen`, `ModeScreen`, `TipsScreen`, `TestScreen`, and `ResultScreen`) inheriting from a foundational `BaseScreen` class. 
    *   **Lifecycle Management:** Each screen implements an `on_show()` hook, allowing views to dynamically refresh high-score labels, randomise texts, and reset state whenever raised to the front.
    *   **Real-Time Text Mapping (`TestScreen`):** Dynamically maps word coordinates within the `tk.Text` widget (`_map_words`) to apply active word highlighting and recalculates font scaling on window resize events.
*   **The Controller (`TypingApp`):** The application root that manages global state (active mode and dual high-score dictionaries), handles JSON data persistence (`highscores.json`), stacks all View frames on initialisation, and routes navigation via `show_frame()`.
*   **Custom UI Primitives (Reusable Components):** 
    *   `DynamicRoundedCanvas`: A foundational class that intercepts `<Configure>` resize events to mathematically recalculate and redraw arcs and rectangles, creating responsive rounded UI panels.
    *   `PillButton` & `PillLabel`: Child classes inheriting from `DynamicRoundedCanvas`, leveraging default keyword arguments and `**kwargs` forwarding to create interactive, pill-shaped elements without redundant styling code.
    *   `ScrollableList`: A composite widget encapsulating `tk.Frame`, `tk.Scrollbar`, and `tk.Text` logic for clean rendering on the analytics screen.
## 🛠️ Getting Started

Because this project relies entirely on the Python Standard Library, there are no external dependencies or `pip install` requirements. 

### Prerequisites
* Python 3.6 or higher

### Installation & Execution
1. Clone the repository:
   ```bash
   git clone https://github.com/Joshuaongith/Typing_speed_test.git
2. Navigate to the project directory:
    ```bash
    cd typing-speed-test

3. Run the application:
    ```bash
    python main.py
    ```



## 📄 Licence

This project is licensed under the GNU General Public License v3.0. See `LICENCE` for more information.