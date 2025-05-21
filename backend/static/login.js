document.getElementById('addCityBtn').addEventListener('click', function() {
    // gets the timezone input  
    var cityInput = document.getElementById('cityInput');
    document.querySelector('.city').textContent = `${cityInput.value.toUpperCase()}`
    var cityAbbr = cityInput.value.toLowerCase();
    cityAbbr = cityAbbr.replace(" ", "%20");
    
    // get image of city
    fetch(`https://source.unsplash.com/featured/?${cityAbbr}`)
        .then(response=>response.blob())
        .then(blob => {
            const imageUrl = URL.createObjectURL(blob)
            cityImg = document.getElementById("cityImg")
            cityImg.src = imageUrl
        })
    .catch(error=>console.error(error));

    // get weather information using lat and lon
    fetch(`https://nominatim.openstreetmap.org/search?q=${cityAbbr}&format=json`)
        .then(response=>response.json())
        .then(data=> {
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            fetchWeather(lat,lon)
               
        })
        .catch(error=>console.error(error));
});

// gets weather information using lat lon
function fetchWeather(lat, lon) {
    fetch(`https://api.weather.gov/points/${lat},${lon}`)
    .then(response=>response.json())
    .then(data=> {
        const forecastUrl = data.properties.forecast
        console.log(data)
        console.log(data.properties.forecast)
        fetchForecast(forecastUrl)
    })
    .catch(error=>console.error(error));
}

// gets forecast info 
function fetchForecast(forecastUrl) {
    fetch(forecastUrl)
    .then(response=>response.json())
    .then(data=> {
        forecast = data["properties"]["periods"][0]["detailedForecast"]
        document.querySelector('.weather').textContent = `Weather Condition(s): ${forecast}`
        weatherFirst = getFirstWord(forecast)
        fetchweatherImg(weatherFirst)

    })
    .catch(error=>console.error(error));
}

// gets weather image
function fetchweatherImg(weatherFirst) {
    fetch(`https://source.unsplash.com/featured/?${weatherFirst}`)
    .then(response=>response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob)
        weatherImg = document.getElementById("img")
        weatherImg.src = imageUrl
    })
    .catch(error=>console.error(error));
}

function getFirstWord(str) {
    str = str.trim();
    var words = str.split(/\s+/);
    return words[0];
}