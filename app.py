from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Inicjalizacja OpenAI
client = OpenAI()  # Automatycznie pobierze OPENAI_API_KEY ze zmiennych środowiskowych

# Cache na ostatnie generowane opisy
description_cache = {}

def generate_ai_description(hobby, personality, goal, language="pl", max_length=1000):
    cache_key = f"{hobby}-{personality}-{goal}-{language}-{max_length}"
    
    # Sprawdź cache
    if cache_key in description_cache:
        return description_cache[cache_key]
    
    # Konfiguracja języka
    language_prompts = {
        "pl": {
            "system": "Jesteś ekspertem od tworzenia opisów na portale społecznościowe i randkowe w języku polskim.",
            "requirements": "Wymagania: użyj 2-3 emoji, dodaj nutę humoru, bądź oryginalny, zachowaj naturalny ton"
        },
        "en": {
            "system": "You are an expert at creating social media and dating profile descriptions in English.",
            "requirements": "Requirements: use 2-3 emojis, add a touch of humor, be original, maintain a natural tone"
        },
        "de": {
            "system": "Sie sind ein Experte für das Erstellen von Social Media und Dating-Profilbeschreibungen auf Deutsch.",
            "requirements": "Anforderungen: verwenden Sie 2-3 Emojis, fügen Sie Humor hinzu, seien Sie originell"
        },
        "it": {
            "system": "Sei un esperto nella creazione di descrizioni per profili social e di incontri in italiano.",
            "requirements": "Requisiti: usa 2-3 emoji, aggiungi umorismo, sii originale, mantieni un tono naturale"
        },
        "nl": {
            "system": "Je bent een expert in het maken van social media en dating profielbeschrijvingen in het Nederlands.",
            "requirements": "Vereisten: gebruik 2-3 emoji's, voeg humor toe, wees origineel, behoud een natuurlijke toon"
        }
    }

    lang_config = language_prompts.get(language, language_prompts["pl"])
    
    # Główny prompt
    prompt = f"""
    Stwórz unikalny, przyciągający uwagę opis na portale społecznościowe/randkowe, dopasowany do podanych informacji.
    
    Informacje o osobie:
    Hobby: {hobby}
    Osobowość: {personality}
    Cel: {goal}
    Maksymalna długość: {max_length} znaków
    
    Wymagania:
    1. Dostosuj ton i styl do podanego celu ({goal})
    2. Użyj 2-3 pasujących emoji
    3. Zachowaj naturalny, autentyczny ton
    4. Podkreśl unikalne cechy i zainteresowania
    5. Zakończ elementem zachęcającym do interakcji
    
    Stwórz opis, który będzie pasował zarówno do portali randkowych jak i innych mediów społecznościowych, bazując głównie na wybranych przez użytkownika opcjach.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": lang_config["system"]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        description = response.choices[0].message.content.strip()
        
        # Zapisz do cache
        description_cache[cache_key] = description
        return description
        
    except Exception as e:
        print(f"Błąd OpenAI: {e}")
        return None

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate_description():
    start_time = time.time()
    
    data = request.json
    if not data:
        return jsonify({"error": "Brak danych"}), 400
    
    hobby = data.get("hobby", "").strip()
    personality = data.get("personality", "neutralny")
    goal = data.get("goal", "znajomości")
    language = data.get("language", "pl")
    max_length = data.get("max_length", 1000)

    if not hobby:
        return jsonify({"error": "Hobby jest wymagane"}), 400

    description = generate_ai_description(hobby, personality, goal, language, max_length)
    
    if not description:
        return jsonify({"error": "Nie udało się wygenerować opisu"}), 500

    generation_time = round(time.time() - start_time, 2)
    
    return jsonify({
        "description": description,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generation_time": f"{generation_time}s"
    })

if __name__ == '__main__':
    app.run(debug=True)