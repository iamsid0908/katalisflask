import openai
from flask import jsonify

DEFAULT_ENGLISH_SYSTEM_SETTING = "You will be given product specifications. Your job is to write the product specification in an inspiring and energetic in a marketing language in a natural language used by e-commerce shoppers in English in a human relatable form. Make into bullet points with relevant emojis. Any number that is there in technical details should also be converted to human understandable format. Make it max 8 bullet points."
# DEFAULT_BAHASA_SYSTEM_SETTING = "Rewrite in bahasa indonesia for all bullet points, use key points, and use a natural language used in every day life but still professional."
DEFAULT_BAHASA_SYSTEM_SETTING = "You will be given product specifications. Your job is to write the product specification in an inspiring and energetic in a marketing language in a natural language used by e-commerce shoppers in Bahasa in a human relatable form. Make into bullet points with relevant emojis. Any number that is there in technical details should also be converted to human understandable format. Make it max 8 bullet points."
from commons.logger_config import log

OPEN_API_KEY = "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"


def generatePromptOutput(data):
    language = data.get("language")
    brandVoice = data.get("brandVoice", [])
    keywords = data.get("keywords", [])
    keyPoints = data.get("keyPoints", [])
    promptSetting = (
        data.get("promptSetting") + f". Write it in {language} language"
        if data.get("promptSetting") != None and data.get("promptSetting") != ""
        else (
            f"You will be given product decription, rewrite it in {language} language and {brandVoice} {', '.join(brandVoice)} tone,it should contain{', '.join(keywords)},and phrase of keypoints in {', '.join(keyPoints)}"
        )
    )
    prompt = data.get("prompt")
    return generateDescription(OPEN_API_KEY, prompt, promptSetting)


def generateDescription(openai_key, my_input, promptSetting):
    try:
        openai.api_key = openai_key
        log.info("calling openAI for English output")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": promptSetting},
                {"role": "user", "content": my_input},
            ],
            temperature=1,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        output = (
            response["choices"][0]["message"]["content"]
            .encode("utf-16", "surrogatepass")
            .decode("utf-16")
        )
        log.info("successfully Received english output")
        return jsonify({"data": output}), 200
    except openai.error.RateLimitError as e:
        return jsonify({"message": f"Error: {e}"}), 429
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        return jsonify({"message": f"Error: {e}"}), 500
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        return jsonify({"message": f"Error: {e}"}), 401


def generateEnglishOutput(openai_key, my_input, promptSetting):
    try:
        openai.api_key = openai_key
        log.info("calling openAI for English output")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": promptSetting},
                {"role": "user", "content": my_input},
            ],
            temperature=1,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        output = (
            response["choices"][0]["message"]["content"]
            .encode("utf-16", "surrogatepass")
            .decode("utf-16")
        )
        log.info("successfully Received english output")
        return jsonify({"data": output}), 200
    except openai.error.RateLimitError as e:
        return jsonify({"message": f"Error: {e}"}), 429
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        return jsonify({"message": f"Error: {e}"}), 500
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        return jsonify({"message": f"Error: {e}"}), 401


def generateBahasaOutput(openai_key, my_input, promptSetting):
    try:
        openai.api_key = openai_key
        log.info("calling openAI for Bahasa output")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {
                    "role": "system",
                    "content": promptSetting
                    if promptSetting != None
                    else DEFAULT_BAHASA_SYSTEM_SETTING,
                },
                {"role": "user", "content": my_input},
            ],
            temperature=1,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        output = (
            response["choices"][0]["message"]["content"]
            .encode("utf-16", "surrogatepass")
            .decode("utf-16")
        )
        log.info("successfully Received Bahasa output")
        return jsonify({"data": output}), 200
    except openai.error.RateLimitError as e:
        return jsonify({"data": f"Error: {e}"}), 500
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        return jsonify({"message": f"Error: {e}"}), 500
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        return jsonify({"message": f"Error: {e}"}), 401
