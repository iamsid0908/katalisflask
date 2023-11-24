import openai
from flask import jsonify
from commons.logger_config import log
from utils.util import get_temp_s3_url_for_file_single_url, getTempBucketPrefix
import os


def callOpenAI(openai_key, imageFile, maskFile, prompt):
    try:
        log.info("call openAI image API")
        NUM_OF_OUTPUTS = 3
        IMAGE_SIZE = "512x512"
        openai.api_key = openai_key
        response = openai.Image.create_edit(
            image=imageFile,
            mask=maskFile,
            prompt=prompt,
            n=NUM_OF_OUTPUTS,
            size=IMAGE_SIZE,
        )
        return format_response(response), 200
    except openai.error.RateLimitError as e:
        log.error("error while calling openAI image API")
        return jsonify({"message": f"Error: {e}"}), 429
    except openai.error.InvalidRequestError as e:
        log.info("error invalid request to chat gpt")
        return jsonify({"message": f"Error: {e}"}), 400
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        return jsonify({"message": f"Error: {e}"}), 500
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        return jsonify({"message": f"Error: {e}"}), 401


def format_response(response):
    finalResponse = {"created": response["created"]}
    finalData = []
    for res in response["data"]:
        finalData.append({"url": getTempS3Url(res["url"])})
    finalResponse["data"] = finalData
    return finalResponse


def getTempS3Url(chatGptUrl):
    image_filename = get_temp_s3_url_for_file_single_url(chatGptUrl)
    return getTempBucketPrefix() + image_filename
