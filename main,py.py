"""
Typing Speed Test Application

Copyright (C) 2026  Joshua Uzochukwu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import random
import string
import time
import tkinter as tk
from pathlib import Path


# Anchor data files to the script's folder, not the current working directory
BASE_DIR = Path(__file__).resolve().parent
TEXTS_PATH = BASE_DIR / "practice_texts.txt"
HIGHSCORE_PATH = BASE_DIR / "highscores.json"

# Used only if the practice text file is missing or empty. It is longer than
# every passage in practice_texts.txt so it fills the text panel just as well.
FALLBACK_TEXTS = [
    "Learning to type quickly is a skill that rewards steady practice more "
    "than raw effort. Begin by keeping your wrists relaxed and your eyes on "
    "the screen rather than the keyboard, and let your fingers find their "
    "familiar positions on the home row. Accuracy matters more than speed in "
    "the early stages, because every mistake you correct costs more time "
    "than a slower, careful keystroke ever would. Over the weeks, your "
    "rhythm will smooth out, and the words will begin to flow almost "
    "without thought."
]


def load_practice_texts(path=TEXTS_PATH):
    """Load practice passages from a text file.

    Passages are separated by one or more blank lines.

    Args:
        path: Location of the practice text file.

    Returns:
        A list of passages, or a single built-in passage if the file is
        missing, unreadable, or empty.
    """
    try:
        blocks = Path(path).read_text(encoding="utf-8").split("\n\n")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error loading practice texts: {e}")
        return list(FALLBACK_TEXTS)

    texts = [" ".join(block.split()) for block in blocks if block.strip()]
    return texts or list(FALLBACK_TEXTS)


# Logic model
class TypingEngine:
    """Core logic engine for tracking typing state and metrics."""

    def __init__(self, reference_text):
        self.reference_text = reference_text.split()
        self.user_words = []
        self.current_word_index = 0
        self.start_time = None
        self.is_running = False

    def start(self):
        """Start the test timer."""
        self.start_time = time.perf_counter()
        self.is_running = True

    def submit_word(self, typed_string):
        """Submit a typed word with lookahead and positional integrity.

        Args:
            typed_string: The word submitted by the user.
        """
        if not typed_string.strip():
            # Empty submission indicates the current word was skipped
            self.user_words.append("")
            self.current_word_index += 1
            return

        if self.current_word_index < len(self.reference_text):
            if typed_string == self.reference_text[self.current_word_index]:
                self.user_words.append(typed_string)
                self.current_word_index += 1
                return

            # Lookahead to check if the user skipped the current word
            # and typed the subsequent word instead
            if self.current_word_index + 1 < len(self.reference_text):
                if typed_string == self.reference_text[self.current_word_index + 1]:
                    self.user_words.append("")
                    self.user_words.append(typed_string)
                    self.current_word_index += 2
                    return

        self.user_words.append(typed_string)
        self.current_word_index += 1

    def revert_word(self):
        """Remove last submission and move index back.

        Returns:
            The previously submitted word string, or an empty string.
        """
        if self.current_word_index > 0:
            self.current_word_index -= 1
            return self.user_words.pop() if self.user_words else ""
        return ""

    def calculate_results(self):
        """Calculate WPM, CPM, and error lists from attempted words.

        Returns:
            A dictionary containing wpm, cpm, misspelled, skipped,
            and elapsed_time.
        """
        if not self.start_time:
            return {
                "wpm": 0,
                "cpm": 0,
                "misspelled": [],
                "skipped": [],
                "elapsed_time": 0,
            }

        elapsed_time = time.perf_counter() - self.start_time

        correct_chars = 0
        total_chars = 0
        misspelled = []
        skipped = []

        # Exclude unreached words at timeout from being marked as skipped
        for i in range(len(self.user_words)):
            if i >= len(self.reference_text):
                break

            typed = self.user_words[i]
            target = self.reference_text[i]

            if not typed.strip():
                skipped.append(target)
            elif typed == target:
                correct_chars += len(typed)
                total_chars += len(typed)
            else:
                misspelled.append(target)
                total_chars += len(typed)

        # Prevent division by zero on immediate termination
        if elapsed_time <= 0:
            elapsed_time = 0.001

        elapsed_minutes = elapsed_time / 60.0

        # Standard WPM normalises word length to 5 characters
        wpm = round((correct_chars / 5) / elapsed_minutes)
        cpm = round(total_chars / elapsed_minutes)

        return {
            "wpm": wpm,
            "cpm": cpm,
            "misspelled": misspelled,
            "skipped": skipped,
            "elapsed_time": elapsed_time,
        }


# Custom UI components
class DynamicRoundedCanvas(tk.Canvas):
    """Canvas that dynamically redraws rounded corners on resize."""

    def __init__(self, parent, color="#CFD6DD", radius=20, bg="#ffffff", **kwargs):
        super().__init__(parent, bg=bg, highlightthickness=0, **kwargs)
        self.color = color
        self.fixed_radius = radius
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Recalculate geometry and redraw rounded rectangle."""
        self.delete("shape")
        w = event.width
        h = event.height
        r = self.fixed_radius if self.fixed_radius else min(w, h) // 2

        if w < 2 * r or h < 2 * r:
            return

        self.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=self.color, outline="", tags="shape")
        self.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90, fill=self.color, outline="", tags="shape")
        self.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90, fill=self.color, outline="", tags="shape")
        self.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=self.color, outline="", tags="shape")
        self.create_rectangle(r, 0, w - r, h, fill=self.color, outline="", tags="shape")
        self.create_rectangle(0, r, w, h - r, fill=self.color, outline="", tags="shape")
        self.tag_lower("shape")


class PillLabel(DynamicRoundedCanvas):
    """Relative pill-shaped label with centred text."""

    def __init__(self, parent, text, radius=10, **kwargs):
        super().__init__(parent, radius=radius, **kwargs)
        self.text_id = self.create_text(0, 0, text=text, font=("Helvetica", 12, "bold"), fill="black")
        self.bind("<Configure>", self._center_text, add="+")

    def _center_text(self, event):
        self.coords(self.text_id, event.width / 2, event.height / 2)


class PillButton(DynamicRoundedCanvas):
    """Relative, interactive pill-shaped button."""

    def __init__(self, parent, text, command, radius=10, **kwargs):
        super().__init__(parent, radius=radius, **kwargs)
        self.command = command
        self.text_id = self.create_text(0, 0, text=text, font=("Helvetica", 14), fill="black")
        self.bind("<Configure>", self._center_text, add="+")
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))

    def _center_text(self, event):
        self.coords(self.text_id, event.width / 2, event.height / 2)


class ScrollableList(tk.Frame):
    """Reusable container for a title, text widget, and scrollbar."""

    def __init__(self, parent, title_text, bg="#CFD6DD", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        tk.Label(self, text=title_text, font=("Helvetica", 18), bg=bg).pack(side=tk.TOP, pady=(0, 5))

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(self, bg=bg, bd=0, font=("Helvetica", 14),
                                   highlightthickness=0, yscrollcommand=self.scroll.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.config(command=self.text_widget.yview)
        self.text_widget.tag_configure("center", justify="center")

    def update_content(self, items):
        """Replace text widget contents with a bulleted list."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        for item in items:
            self.text_widget.insert(tk.END, f"• {item}\n", "center")
        self.text_widget.config(state=tk.DISABLED)


# View screens
class BaseScreen(tk.Frame):
    """Foundational view class providing default background and hooks."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.pack_propagate(False)

    def on_show(self):
        """Execute lifecycle updates when screen is raised to front."""
        pass


class WelcomeScreen(BaseScreen):
    """Landing screen displaying high scores and main navigation."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.high_score_pill = PillLabel(self, text="")
        self.high_score_pill.place(relx=0.05, rely=0.05, relwidth=0.35, relheight=0.06)

        self.panel = DynamicRoundedCanvas(self)
        self.panel.place(relx=0.5, rely=0.45, relwidth=0.8, relheight=0.6, anchor="c")

        tk.Label(self.panel, text="WELCOME TO THE TYPING TEST", font=("Helvetica", 36), bg="#CFD6DD").place(relx=0.5,
                                                                                                            rely=0.5,
                                                                                                            anchor="c")

        self.tips_btn = PillButton(self, text="TIPS", command=lambda: controller.show_frame(TipsScreen))
        self.tips_btn.place(relx=0.1, rely=0.85, relwidth=0.2, relheight=0.08)

        self.start_btn = PillButton(self, text="START", command=lambda: controller.show_frame(ModeScreen))
        self.start_btn.place(relx=0.9, rely=0.85, relwidth=0.2, relheight=0.08, anchor="ne")

    def on_show(self):
        easy_hs = self.controller.high_score['easy']
        hard_hs = self.controller.high_score['hard']

        score_str = f"EASY: {easy_hs['cpm']}CPM {easy_hs['wpm']}WPM | HARD: {hard_hs['cpm']}CPM {hard_hs['wpm']}WPM"
        self.high_score_pill.itemconfig(self.high_score_pill.text_id, text=score_str)


class ModeScreen(BaseScreen):
    """Selection screen for toggling punctuation rules."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.back_btn = PillButton(self, text="BACK", command=lambda: controller.show_frame(WelcomeScreen))
        self.back_btn.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.06)

        self.panel = DynamicRoundedCanvas(self)
        self.panel.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.6, anchor="c")

        tk.Label(self.panel, text="Select Mode", font=("Helvetica", 24), bg="#CFD6DD").place(relx=0.5, rely=0.15,
                                                                                             anchor="c")

        self.raw_btn = PillButton(self.panel, text="No Punctuation", color="#ffffff", bg="#CFD6DD",
                                  command=lambda: self.start_test(False))
        self.raw_btn.place(relx=0.3, rely=0.55, relwidth=0.35, relheight=0.45, anchor="c")

        self.standard_btn = PillButton(self.panel, text="Punctuation", color="#ffffff", bg="#CFD6DD",
                                       command=lambda: self.start_test(True))
        self.standard_btn.place(relx=0.7, rely=0.55, relwidth=0.35, relheight=0.45, anchor="c")

    def start_test(self, has_punctuation):
        self.controller.punctuation_mode = has_punctuation
        self.controller.show_frame(TestScreen)


class TipsScreen(BaseScreen):
    """Informational screen displaying typing best practices."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.back_btn = PillButton(self, text="Typing test", color="#CFD6DD",
                                   command=lambda: controller.show_frame(WelcomeScreen))
        self.back_btn.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.06)

        self.panel = DynamicRoundedCanvas(self)
        self.panel.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.6, anchor="c")

        tk.Label(self.panel, text="Typing tips", font=("Helvetica", 24), bg="#CFD6DD").place(relx=0.5, rely=0.15,
                                                                                             anchor="c")

        tips = [
            "• Maintain a comfortable posture",
            "• Focus on accuracy first, speed will follow",
            "• Relax your fingers and wrists",
            "• Practice consistently"
        ]

        for i, tip in enumerate(tips):
            tk.Label(self.panel, text=tip, font=("Helvetica", 16), bg="#CFD6DD").place(relx=0.5, rely=0.35 + (i * 0.12),
                                                                                       anchor="c")


class ResultScreen(BaseScreen):
    """Post-test analytics screen displaying score and word errors."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.high_score_pill = PillLabel(self, text="")
        self.high_score_pill.place(relx=0.05, rely=0.05, relwidth=0.35, relheight=0.06)

        self.panel = DynamicRoundedCanvas(self)
        self.panel.place(relx=0.5, rely=0.45, relwidth=0.8, relheight=0.6, anchor="c")

        # Invert default colours to render a white pill on the grey panel
        self.score_pill = PillLabel(self.panel, text="", color="#ffffff", bg="#CFD6DD")
        self.score_pill.place(relx=0.5, rely=0.1, relwidth=0.4, relheight=0.12, anchor="c")

        self.misspelt_list = ScrollableList(self.panel, title_text="Misspelt words")
        self.misspelt_list.place(relx=0.5, rely=0.38, relwidth=0.5, relheight=0.25, anchor="c")

        self.skipped_list = ScrollableList(self.panel, title_text="Skipped words")
        self.skipped_list.place(relx=0.5, rely=0.74, relwidth=0.5, relheight=0.25, anchor="c")

        self.tips_btn = PillButton(self, text="TIPS", command=lambda: controller.show_frame(TipsScreen))
        self.tips_btn.place(relx=0.1, rely=0.85, relwidth=0.2, relheight=0.08)

        self.try_again_btn = PillButton(self, text="TRY AGAIN", command=lambda: controller.show_frame(TestScreen))
        self.try_again_btn.place(relx=0.9, rely=0.85, relwidth=0.2, relheight=0.08, anchor="ne")

    def load_results(self, results):
        """Populate score label and scrollable error lists."""
        self.score_pill.itemconfig(self.score_pill.text_id, text=f"SCORE: {results['cpm']}CPM | {results['wpm']}WPM")
        self.misspelt_list.update_content(results['misspelled'])
        self.skipped_list.update_content(results['skipped'])

    def on_show(self):
        mode_name = "HARD" if self.controller.punctuation_mode else "EASY"
        mode_key = mode_name.lower()
        hs = self.controller.high_score[mode_key]

        score_str = f"{mode_name} MODE - HIGH SCORE: {hs['cpm']}CPM | {hs['wpm']}WPM"
        self.high_score_pill.itemconfig(self.high_score_pill.text_id, text=score_str)


class TestScreen(BaseScreen):
    """Active test screen handling user input, highlighting, and timers."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.test_text = ""
        self.engine = TypingEngine(self.test_text)
        self.timer_id = None
        self.word_indices = []

        self.high_score_pill = PillLabel(self, text="")
        self.high_score_pill.place(relx=0.05, rely=0.05, relwidth=0.35, relheight=0.06)

        self.cancel_btn = PillButton(self, text="CANCEL ROUND", command=self.cancel_round)
        self.cancel_btn.place(relx=0.95, rely=0.05, relwidth=0.2, relheight=0.06, anchor="ne")

        self.text_panel = DynamicRoundedCanvas(self)
        self.text_panel.place(relx=0.5, rely=0.45, relwidth=0.85, relheight=0.55, anchor="c")

        self.dynamic_font = ("Helvetica", 16)
        self.text_widget = tk.Text(self.text_panel, font=self.dynamic_font, bg="#CFD6DD", fg="black", bd=0,
                                   highlightthickness=0, wrap=tk.WORD)
        self.text_widget.insert(tk.END, self.test_text)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.tag_config("highlight", background="white", foreground="black")
        self.text_widget.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.8, anchor="c")

        self.text_widget.bind("<Configure>", self._resize_text)

        self.entry_panel = DynamicRoundedCanvas(self, radius=10)
        self.entry_panel.place(relx=0.5, rely=0.85, relwidth=0.6, relheight=0.08, anchor="c")

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.entry_panel, textvariable=self.entry_var, font=("Helvetica", 16), bg="#CFD6DD", bd=0,
                              highlightthickness=0, justify="center")
        self.entry.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.6, anchor="c")

        self.entry.bind("<space>", self.on_space)
        self.entry.bind("<BackSpace>", self.handle_backspace)
        self.entry.bind("<Key>", self.on_any_key)

        self._map_words()

    def _resize_text(self, event):
        """Scale font size proportionally to widget height."""
        new_size = max(12, int(event.height * 0.07))

        self.dynamic_font = ("Helvetica", new_size)
        self.text_widget.configure(font=self.dynamic_font)

        # Remap coordinates as font scaling alters text wrapping
        self._map_words()
        self.update_highlight()

    def _map_words(self):
        """Cache start and end indices of each word for highlighting."""
        self.word_indices = []
        pos = "1.0"
        for word in self.engine.reference_text:
            start_pos = self.text_widget.search(word, pos, stopindex=tk.END, regexp=False)
            if start_pos:
                end_pos = f"{start_pos}+{len(word)}c"
                self.word_indices.append((start_pos, end_pos))
                pos = end_pos

    def update_highlight(self):
        """Highlight the current target word and scroll it into view."""
        self.text_widget.tag_remove("highlight", "1.0", tk.END)
        idx = self.engine.current_word_index
        if idx < len(self.word_indices):
            start, end = self.word_indices[idx]
            self.text_widget.tag_add("highlight", start, end)
            self.text_widget.see(start)

    def on_space(self, event):
        """Submit current word buffer and advance highlight."""
        word = self.entry_var.get().strip()
        if word or self.engine.current_word_index > 0:
            self.engine.submit_word(word)
            self.entry_var.set("")
            self.update_highlight()

            if self.engine.current_word_index >= len(self.engine.reference_text):
                self.end_test()

        # Prevent the space character from being inserted into the entry
        return "break"

    def handle_backspace(self, event):
        """Revert to previous word if current entry buffer is empty."""
        if len(self.entry_var.get()) == 0 and self.engine.current_word_index > 0:
            prev_word = self.engine.revert_word()
            self.entry_var.set(prev_word)
            self.entry.icursor(tk.END)
            self.update_highlight()
            return "break"
        return None

    def on_any_key(self, event):
        """Trigger the 60-second timer on the first character keystroke."""
        if event.keysym not in ('Shift_L', 'Shift_R', 'Caps_Lock', 'BackSpace', 'space', 'Tab'):
            if not self.engine.is_running:
                self.engine.start()
                self.timer_id = self.after(60000, self.end_test)

    def cancel_round(self):
        """Abort active timer and return to welcome screen."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.controller.show_frame(WelcomeScreen)

    def end_test(self):
        """Stop timer, update high scores, and transition to results."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        results = self.engine.calculate_results()

        mode_key = "hard" if self.controller.punctuation_mode else "easy"
        current_hs = self.controller.high_score[mode_key]

        if results['wpm'] > current_hs['wpm'] or results['cpm'] > current_hs['cpm']:
            current_hs['wpm'] = max(current_hs['wpm'], results['wpm'])
            current_hs['cpm'] = max(current_hs['cpm'], results['cpm'])

            self.controller.save_high_score()

        result_screen = self.controller.frames[ResultScreen]
        result_screen.load_results(results)
        self.controller.show_frame(ResultScreen)

    def on_show(self):
        """Reset engine state and load a new passage for the active mode."""
        mode_name = "HARD" if self.controller.punctuation_mode else "EASY"
        mode_key = mode_name.lower()
        hs = self.controller.high_score[mode_key]

        score_str = f"{mode_name} MODE - HIGH SCORE: {hs['cpm']}CPM | {hs['wpm']}WPM"
        self.high_score_pill.itemconfig(self.high_score_pill.text_id, text=score_str)

        raw_text = random.choice(self.controller.practice_texts)

        if not self.controller.punctuation_mode:
            raw_text = raw_text.translate(str.maketrans('', '', string.punctuation)).lower()

        self.test_text = raw_text

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, self.test_text)
        self.text_widget.config(state=tk.DISABLED)

        self.engine = TypingEngine(self.test_text)
        self.entry_var.set("")
        self.entry.focus_set()

        self._map_words()
        self.update_highlight()

        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None


# Application controller
class TypingApp(tk.Tk):
    """Application root managing geometry, state persistence, and routing."""

    def __init__(self):
        super().__init__()
        self.title("Typing Speed Test")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.app_width = int(self.screen_width * 0.6)
        self.app_height = int(self.screen_height * 0.7)

        self.geometry(f"{self.app_width}x{self.app_height}")
        self.minsize(self.app_width, self.app_height)

        self.high_score = {
            "easy": {"wpm": 0, "cpm": 0},
            "hard": {"wpm": 0, "cpm": 0}
        }
        self.punctuation_mode = True
        self.practice_texts = load_practice_texts()
        self.load_high_scores()

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (WelcomeScreen, TipsScreen, ModeScreen, ResultScreen, TestScreen):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(WelcomeScreen)

    def load_high_scores(self):
        """Read the JSON high score file and merge it into the defaults.

        A missing file is ignored. Using update() keeps the default keys
        in place if the file lacks one.
        """
        if not HIGHSCORE_PATH.exists():
            return

        try:
            with HIGHSCORE_PATH.open("r", encoding="utf-8") as file:
                data = json.load(file)
            for mode in self.high_score:
                self.high_score[mode].update(data.get(mode, {}))
        except (OSError, ValueError, AttributeError, TypeError) as e:
            print(f"Error loading high scores: {e}")

    def save_high_score(self):
        """Overwrite the JSON file with the current high scores."""
        try:
            with HIGHSCORE_PATH.open("w", encoding="utf-8") as file:
                json.dump(self.high_score, file, indent=4)
        except OSError as e:
            print(f"Error saving high scores: {e}")

    def show_frame(self, frame_class):
        """Raise target screen to front and trigger its on_show hook."""
        frame = self.frames[frame_class]
        frame.on_show()
        frame.tkraise()


if __name__ == "__main__":
    app = TypingApp()
    app.mainloop()