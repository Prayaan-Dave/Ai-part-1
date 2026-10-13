import requests
from config import HF_API_KEY



HF_URL = "https://router.huggingface.co/v1/chat/completions"

HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


def ask_ai(question):

    data = {
        "model": "Qwen/Qwen2.5-7B-Instruct",

        "messages": [
            {
                "role": "system",
                "content": """
You are an AI Student Assistant.

Answer questions clearly and accurately.

If the user asks a normal question:
- Explain the answer clearly.
- Use examples when useful.

If the user asks a math or science question:
- Identify what is being asked.
- Identify the information given.
- Show the relevant formula.
- Substitute the values.
- Calculate the answer step by step.
- Clearly state the final answer.
- Use appropriate units.

Never skip important calculation steps.
"""
            },

            {
                "role": "user",
                "content": question
            }
        ],

        "temperature": 0.2,
        "max_tokens": 1500,
        "stream": False
    }

    try:

        response = requests.post(
            HF_URL,
            headers=HF_HEADERS,
            json=data,
            timeout=90
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:

        return "AI Error: " + str(e)


# ============================================================
# MATH SOLVER
# ============================================================

def solve_math(problem):

    prompt = f"""
You are an expert mathematics tutor.

Solve the following mathematics problem.

PROBLEM:
{problem}

Your response MUST follow this structure:

1. What is given?
2. What do we need to find?
3. Formula / method
4. Step-by-step calculation
5. Final answer

Rules:

- Carefully read the entire problem.
- If it is a word problem, extract the numerical information.
- Show every important calculation.
- Do not simply give the final answer.
- Check the calculation before giving the final answer.
- Include units where appropriate.
- If multiple steps are required, number them.
- If the problem is ambiguous, explain what information is missing.

Solve the actual problem rather than giving a generic explanation.
"""

    return ask_ai(prompt)


# ============================================================
# SCIENCE SOLVER
# ============================================================

def solve_science(problem):

    prompt = f"""
You are an expert science tutor.

Solve and explain the following science problem.

PROBLEM:
{problem}

First determine which branch of science the problem belongs to,
such as:

- Physics
- Chemistry
- Biology
- Earth Science
- Environmental Science

Then answer using this structure:

1. Topic
2. Information given
3. What needs to be found
4. Relevant concept or formula
5. Step-by-step solution
6. Final answer
7. Short explanation

For numerical problems:

- Show the formula.
- Substitute the values.
- Calculate step by step.
- Include units.
- Check whether the final answer makes physical sense.

For conceptual problems:

- Explain the concept in simple language.
- Give an example if helpful.

Do not skip the reasoning needed to understand the answer.
"""

    return ask_ai(prompt)


# ============================================================
# AUTO DETECT MATH / SCIENCE
# ============================================================

def detect_subject(question):

    text = question.lower()

    math_words = [
        "calculate",
        "solve",
        "equation",
        "algebra",
        "geometry",
        "probability",
        "percentage",
        "percent",
        "average",
        "ratio",
        "fraction",
        "factor",
        "square root",
        "area",
        "volume",
        "perimeter",
        "distance",
        "speed",
        "time",
        "profit",
        "loss",
        "interest",
        "mean",
        "median",
        "mode",
        "equivalent",
        "triangle",
        "circle",
        "angle",
        "quadratic",
        "linear",
        "derivative",
        "integral"
    ]

    science_words = [
        "physics",
        "chemistry",
        "biology",
        "force",
        "velocity",
        "acceleration",
        "momentum",
        "energy",
        "power",
        "gravity",
        "newton",
        "joule",
        "watt",
        "electricity",
        "voltage",
        "current",
        "resistance",
        "circuit",
        "atom",
        "molecule",
        "chemical",
        "reaction",
        "acid",
        "base",
        "ph",
        "electron",
        "proton",
        "neutron",
        "cell",
        "dna",
        "rna",
        "photosynthesis",
        "respiration",
        "mitosis",
        "ecosystem",
        "evolution",
        "organism",
        "temperature",
        "pressure",
        "mass",
        "density",
        "wave",
        "frequency",
        "wavelength"
    ]

    math_score = 0
    science_score = 0

    for word in math_words:

        if word in text:
            math_score += 1

    for word in science_words:

        if word in text:
            science_score += 1

    # Mathematical symbols/numbers can also indicate math
    if any(symbol in text for symbol in ["+", "-", "*", "/", "=", "%"]):

        math_score += 1

    # Decide subject

    if math_score > science_score and math_score > 0:

        return "math"

    elif science_score > math_score and science_score > 0:

        return "science"

    else:

        return "general"


# ============================================================
# WIKIPEDIA API
# ============================================================

def wikipedia(topic):

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + requests.utils.quote(topic)
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        if response.status_code == 404:

            return "I couldn't find that topic on Wikipedia."

        response.raise_for_status()

        data = response.json()

        title = data.get(
            "title",
            topic
        )

        description = data.get(
            "description",
            ""
        )

        extract = data.get(
            "extract",
            ""
        )

        answer = f"\n📚 {title}\n"

        if description:

            answer += description + "\n\n"

        answer += extract

        return answer

    except Exception as e:

        return "Wikipedia Error: " + str(e)


# ============================================================
# WEATHER API
# ============================================================

def weather(city):

    try:

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            geo_url,
            params=geo_params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if "results" not in data:

            return "City not found."

        location = data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location["name"]

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        weather_params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "wind_speed_10m"
            )
        }

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=15
        )

        response.raise_for_status()

        weather_data = response.json()

        current = weather_data["current"]

        return f"""
🌤️ Weather for {city_name}

Temperature: {current["temperature_2m"]}°C

Feels like: {current["apparent_temperature"]}°C

Humidity: {current["relative_humidity_2m"]}%

Wind speed: {current["wind_speed_10m"]} km/h
"""

    except Exception as e:

        return "Weather Error: " + str(e)


# ============================================================
# JOKE API
# ============================================================

def get_joke():

    url = (
        "https://v2.jokeapi.dev/joke/"
        "Programming,Miscellaneous"
        "?safe-mode"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data["type"] == "single":

            return "😂 " + data["joke"]

        else:

            return (
                "😂 "
                + data["setup"]
                + "\n"
                + data["delivery"]
            )

    except Exception as e:

        return "Joke API Error: " + str(e)


# ============================================================
# COUNTRY API
# ============================================================

def country_info(country):

    url = (
        "https://restcountries.com/v3.1/name/"
        + requests.utils.quote(country)
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        country_data = data[0]

        name = country_data["name"]["common"]

        capital = country_data.get(
            "capital",
            ["Unknown"]
        )[0]

        population = country_data.get(
            "population",
            0
        )

        region = country_data.get(
            "region",
            "Unknown"
        )

        return f"""
🌍 Country Information

Country: {name}

Capital: {capital}

Population: {population:,}

Region: {region}
"""

    except Exception as e:

        return "Country API Error: " + str(e)


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

def sentiment_analysis(text):

    url = (
        "https://router.huggingface.co/"
        "hf-inference/models/"
        "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
    )

    headers = {
        "Authorization":
        f"Bearer {HF_API_KEY}"
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json={
                "inputs": text
            },
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        if isinstance(result[0], list):

            result = result[0]

        best = max(
            result,
            key=lambda x: x["score"]
        )

        label = best["label"]

        score = best["score"]

        emoji = (
            "😊"
            if label == "POSITIVE"
            else "😔"
        )

        return (
            f"{emoji} Sentiment: {label}\n"
            f"Confidence: {score:.2%}"
        )

    except Exception as e:

        return "Sentiment Error: " + str(e)


# ============================================================
# MAIN QUESTION PROCESSOR
# ============================================================

def process_question(question):

    lower = question.lower().strip()


    # ----------------------------------------
    # SPECIAL COMMANDS
    # ----------------------------------------

    if lower == "weather":

        city = input("Enter city: ")

        return weather(city)


    if lower == "wiki":

        topic = input("Enter topic: ")

        return wikipedia(topic)


    if lower == "joke":

        return get_joke()


    if lower == "country":

        country = input("Enter country: ")

        return country_info(country)


    if lower == "sentiment":

        text = input(
            "Enter text to analyze: "
        )

        return sentiment_analysis(text)


    # ----------------------------------------
    # AUTOMATIC MATH / SCIENCE DETECTION
    # ----------------------------------------

    subject = detect_subject(question)


    if subject == "math":

        print("\n🧮 Mathematics problem detected...\n")

        return solve_math(question)


    if subject == "science":

        print("\n🔬 Science problem detected...\n")

        return solve_science(question)


    # ----------------------------------------
    # NORMAL AI QUESTION
    # ----------------------------------------

    return ask_ai(question)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)

    print("🤖 AI STUDENT ASSISTANT")

    print("=" * 65)

    print("""
Ask me anything.

I can handle:

🤖 General questions
🧮 Mathematics problems
🔬 Science problems
📚 Wikipedia
🌤️ Weather
🌍 Country information
😊 Sentiment analysis
😂 Jokes

You don't need special commands for math or science.

Just type the complete question.

Type "exit" to quit.
""")

    while True:

        question = input("\nYou: ")

        if question.lower().strip() == "exit":

            print("\nAI: Goodbye! 👋")

            break

        if not question.strip():

            continue

        answer = process_question(question)

        print("\n" + answer)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()