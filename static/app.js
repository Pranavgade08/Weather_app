document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const cityInput = document.getElementById('city-input');
    const searchBtn = document.getElementById('search-btn');
    const errorBox = document.getElementById('error-box');
    const errorMessage = document.getElementById('error-message');
    const welcomeState = document.getElementById('welcome-state');
    const loadingState = document.getElementById('loading-state');
    const weatherContent = document.getElementById('weather-content');

    // Weather display fields
    const wIcon = document.getElementById('w-icon');
    const wCity = document.getElementById('w-city');
    const wCondition = document.getElementById('w-condition');
    const wTemp = document.getElementById('w-temp');
    const wFeels = document.getElementById('w-feels');
    const wHumidity = document.getElementById('w-humidity');
    const wWind = document.getElementById('w-wind');
    const wMinmax = document.getElementById('w-minmax');

    // Quick suggestion pill buttons
    const cityPills = document.querySelectorAll('.city-pill');
    cityPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const city = pill.getAttribute('data-city');
            cityInput.value = city;
            fetchWeatherData(city);
        });
    });

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = cityInput.value.trim();
        if (city) {
            fetchWeatherData(city);
        }
    });

    async function fetchWeatherData(city) {
        hideError();
        showLoading();

        try {
            const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch weather data.');
            }

            renderWeather(data);
        } catch (err) {
            showError(err.message);
            showWelcome();
        } finally {
            hideLoading();
        }
    }

    function renderWeather(data) {
        wIcon.textContent = data.icon_symbol || '🌤️';
        wCity.textContent = data.country ? `${data.city}, ${data.country}` : data.city;
        wCondition.textContent = data.description || data.condition;
        wTemp.textContent = Math.round(data.temperature);
        wFeels.textContent = `${data.feels_like}°C`;
        wHumidity.textContent = `${data.humidity}%`;
        wWind.textContent = `${data.wind_speed} m/s`;
        wMinmax.textContent = `${data.temp_min}° / ${data.temp_max}°C`;

        welcomeState.classList.add('hidden');
        weatherContent.classList.remove('hidden');
    }

    function showLoading() {
        searchBtn.disabled = true;
        searchBtn.textContent = '...';
        welcomeState.classList.add('hidden');
        weatherContent.classList.add('hidden');
        loadingState.classList.remove('hidden');
    }

    function hideLoading() {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
        loadingState.classList.add('hidden');
    }

    function showWelcome() {
        weatherContent.classList.add('hidden');
        welcomeState.classList.remove('hidden');
    }

    function showError(msg) {
        errorMessage.innerHTML = msg.replace(/\n/g, '<br>');
        errorBox.classList.remove('hidden');
    }

    function hideError() {
        errorBox.classList.add('hidden');
        errorMessage.textContent = '';
    }
});
