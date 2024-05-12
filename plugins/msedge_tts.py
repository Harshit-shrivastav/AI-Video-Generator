import asyncio
import random
import os
from concurrent.futures import ThreadPoolExecutor
import edge_tts
from edge_tts import VoicesManager

def get_edge_tts(text, language='english'):
    language_mapping = {
        'english': 'en',
        'persian': 'fa',
        'vietnamese': 'vi',
        'zulu': 'zu',
        'afrikaans': 'af',
        'amharic': 'am',
        'arabic': 'ar',
        'azerbaijani': 'az',
        'bulgarian': 'bg',
        'bengali': 'bn',
        'bosnian': 'bs',
        'catalan': 'ca',
        'czech': 'cs',
        'welsh': 'cy',
        'danish': 'da',
        'german': 'de',
        'greek': 'el',
        'spanish': 'es',
        'estonian': 'et',
        'filipino': 'fil',
        'finnish': 'fi',
        'french': 'fr',
        'irish': 'ga',
        'galician': 'gl',
        'gujarati': 'gu',
        'hebrew': 'he',
        'hindi': 'hi',
        'croatian': 'hr',
        'hungarian': 'hu',
        'indonesian': 'id',
        'icelandic': 'is',
        'italian': 'it',
        'japanese': 'ja',
        'javanese': 'jv',
        'georgian': 'ka',
        'kazakh': 'kk',
        'khmer': 'km',
        'kannada': 'kn',
        'korean': 'ko',
        'lao': 'lo',
        'lithuanian': 'lt',
        'latvian': 'lv',
        'macedonian': 'mk',
        'malayalam': 'ml',
        'mongolian': 'mn',
        'marathi': 'mr',
        'malay': 'ms',
        'maltese': 'mt',
        'burmese': 'my',
        'norwegian': 'nb',
        'nepali': 'ne',
        'dutch': 'nl',
        'polish': 'pl',
        'pashto': 'ps',
        'portuguese': 'pt',
        'romanian': 'ro',
        'russian': 'ru',
        'sinhala': 'si',
        'slovak': 'sk',
        'slovenian': 'sl',
        'somali': 'so',
        'albanian': 'sq',
        'serbian': 'sr',
        'sundanese': 'su',
        'swedish': 'sv',
        'swahili': 'sw',
        'tamil': 'ta',
        'telugu': 'te',
        'thai': 'th',
        'turkish': 'tr',
        'ukrainian': 'uk',
        'urdu': 'ur',
        'uzbek': 'uz'
    }

    async def async_generate_audio(text, lang):
        try:
            voices = await VoicesManager.create()
            if lang == "english":
                voice = voices.find(Locale="en-US")
            else:
                voice = voices.find(Language=lang)
            speaker = random.choice(voice)["Name"]
            communicate = edge_tts.Communicate(text, speaker)
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        except Exception as e:
            print("Error generating audio using edge_tts:", e)
            raise

    async def run_async(text, lang):
        try:
            return await async_generate_audio(text, lang)
        except Exception as e:
            print("An error occurred during audio generation:", e)
            raise

    try:
        lang_code = language_mapping.get(language.lower(), 'en')
        return asyncio.run(run_async(text, lang_code))
    except Exception as e:
        print("Error generating text to speech:", e)
        return None
