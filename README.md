# 🌤️ Modern Weather Web App (Python)

A modern, responsive, glassmorphic Weather Web Application built with a **Python (Flask)** backend and a real-time responsive frontend.

---

## 🌐 Live Website

Your app is running locally at:
👉 **[http://localhost:5000](http://localhost:5000)** (or `http://127.0.0.1:5000`)

---

## 📁 Project Structure

```text
WEATHER APP/
├── app.py             # Flask web server & /api/weather endpoint
├── api.py             # OpenWeatherMap API integration & error handling
├── weather.py         # Data models, parsing, & weather icon mapping
├── main.py            # Launcher (starts server & opens browser automatically)
├── templates/
│   └── index.html     # Semantic modern HTML5 layout
├── static/
│   ├── style.css      # Dark glassmorphism styling & animations
│   └── app.js         # Frontend interactive logic & live search
└── README.md          # Project guide
```

---

## 🔑 Where to Put Your API Key

1. Sign up for a free key at [OpenWeatherMap API Keys](https://home.openweathermap.org/api_keys).
2. Open [`api.py`](file:///c:/Users/shara/OneDrive/Desktop/wEATHER%20APP/api.py).
3. Find line **13**:
   ```python
   API_KEY = "YOUR_API_KEY_HERE"
   ```
4. Replace `"YOUR_API_KEY_HERE"` with your actual 32-character key:
   ```python
   API_KEY = "your_32_character_api_key_goes_here"
   ```

*(Note: Free OpenWeather keys typically activate within 10 to 30 minutes after registration)*

---

## 🚀 How to Run

To run the web app anytime:

```bash
python main.py
```
This automatically starts the server and opens **`http://localhost:5000`** in your browser.
