from flask import Flask, render_template, request, jsonify
from api import fetch_weather
from weather import parse_weather_data

app = Flask(__name__)

# Disable all caching so changes reflect immediately in the browser
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    """Renders the main weather application web page."""
    return render_template("index.html")


@app.route("/api/weather")
def get_weather():
    """
    API endpoint to fetch weather data for a city.
    Query param: ?city=<city_name>
    """
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City parameter is required."}), 400

    try:
        raw_data = fetch_weather(city)
        weather_data = parse_weather_data(raw_data)
        return jsonify(weather_data.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 401
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


if __name__ == "__main__":
    print("\n=======================================================")
    print(" Weather App Server is running!")
    print(" Open in your browser: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
