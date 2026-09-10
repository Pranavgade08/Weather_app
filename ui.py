import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from api import fetch_weather
from weather import WeatherData, parse_weather_data


# Color Palette (Modern Dark Theme)
BG_MAIN = "#0F172A"       # Slate 900
BG_CARD = "#1E293B"       # Slate 800
BG_INPUT = "#334155"      # Slate 700
ACCENT_BLUE = "#38BDF8"   # Sky 400
ACCENT_HOVER = "#0284C7"  # Sky 600
TEXT_MAIN = "#F8FAFC"     # Slate 50
TEXT_MUTED = "#94A3B8"    # Slate 400
CARD_BORDER = "#334155"   # Slate 700
ERROR_COLOR = "#F87171"   # Red 400


class ModernWeatherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("460x640")
        self.root.minsize(420, 580)
        self.root.configure(bg=BG_MAIN)

        # Center the window on the screen
        self._center_window()

        self._build_ui()

    def _center_window(self):
        self.root.update_idletasks()
        width = 460
        height = 640
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        # Main container with padding
        self.container = tk.Frame(self.root, bg=BG_MAIN, padx=24, pady=20)
        self.container.pack(fill="both", expand=True)

        # App Header
        header_frame = tk.Frame(self.container, bg=BG_MAIN)
        header_frame.pack(fill="x", pady=(0, 15))

        title_lbl = tk.Label(
            header_frame,
            text="Weather Forecast",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_MAIN,
            bg=BG_MAIN
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_frame,
            text="Check real-time weather anywhere in the world",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_MAIN
        )
        subtitle_lbl.pack(anchor="w")

        # Search Bar
        search_frame = tk.Frame(self.container, bg=BG_MAIN)
        search_frame.pack(fill="x", pady=(0, 16))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 12),
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            highlightcolor=ACCENT_BLUE
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.on_search())
        self.search_entry.focus_set()

        self.search_btn = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_BLUE,
            fg="#0F172A",
            activebackground=ACCENT_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            command=self.on_search
        )
        self.search_btn.pack(side="right", ipady=6)

        # Status / Message Banner
        self.status_label = tk.Label(
            self.container,
            text="",
            font=("Segoe UI", 10),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            wraplength=380,
            justify="center"
        )
        self.status_label.pack(fill="x", pady=(0, 10))

        # Main Weather Display Card
        self.card_frame = tk.Frame(
            self.container,
            bg=BG_CARD,
            padx=20,
            pady=18,
            highlightthickness=1,
            highlightbackground=CARD_BORDER
        )
        self.card_frame.pack(fill="both", expand=True)

        self._build_weather_card_contents()

        # Initial Empty State
        self.show_welcome_state()

    def _build_weather_card_contents(self):
        # Weather Icon
        self.icon_label = tk.Label(
            self.card_frame,
            text="🌍",
            font=("Segoe UI Emoji", 58),
            fg=TEXT_MAIN,
            bg=BG_CARD
        )
        self.icon_label.pack(pady=(4, 0))

        # City Name & Country
        self.city_label = tk.Label(
            self.card_frame,
            text="Ready to search",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_MAIN,
            bg=BG_CARD
        )
        self.city_label.pack()

        # Temperature
        self.temp_label = tk.Label(
            self.card_frame,
            text="-- °C",
            font=("Segoe UI", 36, "bold"),
            fg=ACCENT_BLUE,
            bg=BG_CARD
        )
        self.temp_label.pack(pady=(0, 2))

        # Condition Description Badge
        self.desc_label = tk.Label(
            self.card_frame,
            text="Enter a city above to see current weather",
            font=("Segoe UI", 11),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        self.desc_label.pack(pady=(0, 16))

        # Grid of Details (Feels like, Humidity, Wind, Min/Max)
        self.details_grid = tk.Frame(self.card_frame, bg=BG_CARD)
        self.details_grid.pack(fill="x", pady=(4, 0))
        self.details_grid.columnconfigure(0, weight=1)
        self.details_grid.columnconfigure(1, weight=1)

        # 4 Metric Blocks
        self.feels_val = self._create_metric_box(self.details_grid, 0, 0, "🌡️ Feels Like", "-- °C")
        self.humidity_val = self._create_metric_box(self.details_grid, 0, 1, "💧 Humidity", "-- %")
        self.wind_val = self._create_metric_box(self.details_grid, 1, 0, "💨 Wind Speed", "-- m/s")
        self.minmax_val = self._create_metric_box(self.details_grid, 1, 1, "📊 Min / Max", "-- / -- °C")

    def _create_metric_box(self, parent, row, col, title, initial_value):
        frame = tk.Frame(parent, bg=BG_INPUT, padx=12, pady=10, relief="flat")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl_title = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_INPUT
        )
        lbl_title.pack(anchor="w")

        lbl_value = tk.Label(
            frame,
            text=initial_value,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_MAIN,
            bg=BG_INPUT
        )
        lbl_value.pack(anchor="w", pady=(3, 0))

        return lbl_value

    def show_welcome_state(self):
        self.icon_label.config(text="🌤️")
        self.city_label.config(text="Search a City", fg=TEXT_MAIN)
        self.temp_label.config(text="-- °C", fg=ACCENT_BLUE)
        self.desc_label.config(text="Type any city name (e.g. London, Tokyo, Mumbai)", fg=TEXT_MUTED)
        self.feels_val.config(text="-- °C")
        self.humidity_val.config(text="-- %")
        self.wind_val.config(text="-- m/s")
        self.minmax_val.config(text="-- / -- °C")
        self.status_label.config(text="", fg=TEXT_MUTED)

    def on_search(self):
        city = self.search_entry.get().strip()
        if not city:
            self.show_error("Please enter a city name to search.")
            return

        # Disable search button while loading
        self.search_btn.config(state="disabled", text="Loading...")
        self.status_label.config(text=f"Fetching weather for '{city}'...", fg=ACCENT_BLUE)

        # Run fetch in background thread to keep UI responsive
        threading.Thread(target=self._fetch_weather_worker, args=(city,), daemon=True).start()

    def _fetch_weather_worker(self, city: str):
        try:
            raw_data = fetch_weather(city)
            weather_data = parse_weather_data(raw_data)
            # Update UI on main thread
            self.root.after(0, self._update_ui_with_weather, weather_data)
        except PermissionError as e:
            self.root.after(0, self.show_error, str(e))
        except LookupError as e:
            self.root.after(0, self.show_error, str(e))
        except ConnectionError as e:
            self.root.after(0, self.show_error, str(e))
        except Exception as e:
            self.root.after(0, self.show_error, f"Error: {str(e)}")
        finally:
            self.root.after(0, self._reset_search_button)

    def _reset_search_button(self):
        self.search_btn.config(state="normal", text="Search")

    def _update_ui_with_weather(self, data: WeatherData):
        self.status_label.config(text="")
        self.icon_label.config(text=data.icon_symbol)

        city_display = f"{data.city}, {data.country}" if data.country else data.city
        self.city_label.config(text=city_display, fg=TEXT_MAIN)
        self.temp_label.config(text=f"{data.temperature}°C", fg=ACCENT_BLUE)
        self.desc_label.config(text=f"{data.description}", fg=TEXT_MAIN)

        self.feels_val.config(text=f"{data.feels_like}°C")
        self.humidity_val.config(text=f"{data.humidity}%")
        self.wind_val.config(text=f"{data.wind_speed} m/s")
        self.minmax_val.config(text=f"{data.temp_min}° / {data.temp_max}°C")

    def show_error(self, message: str):
        self.status_label.config(text=message, fg=ERROR_COLOR)


def create_app():
    root = tk.Tk()
    app = ModernWeatherApp(root)
    return root, app
