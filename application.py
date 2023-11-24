import PIL
from commons.logger_config import log
import os
import json
import openai
import pandas as pd

from flask import Flask, request, jsonify
import math
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from dto.request.ConvertBase64ImageSchema import ConvertBase64ImageSchema
from dto.request.CreateMaskSchema import CreateMaskSchema
from dto.request.RemoveBackgroundImageSchema import RemoveBackgroundImageSchema
from utils.gptImage import callOpenAI
from utils.util import (
    create_products_table,
    create_user_table,
    getListingBucketPrefix,
    getTempBucketPrefix,
)
import base64
from PIL import Image, ImageOps
from io import BytesIO

from dto.request.CSVUploadSchema import CSVUploadSchema
from dto.request.BulkDeleteSchema import BulkDeleteSchema

from dto.request.GetPaginatedListingSchema import GetPaginatedListingSchema
from utils.gptTranslate import (
    generatePromptOutput,
)
from rembg import remove, new_session
from utils.fileUtils import (
    download_file,
    filter_convert_image_to_rgba,
    delete_file,
    extract_base64_image,
    getImageBytesArrayFromBase64,
)
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dto.request.LoginSchema import LoginSchema
from dto.request.RegistrationSchema import RegistrationSchema
from dto.request.OpenAiDescriptionSchema import OpenAiDescriptionSchema
from dto.request.OpenAiImageSchema import OpenAiImageSchema
from dto.request.SaveListingSchema import SaveListingSchema
from dto.response.GetListingResponseSchema import GetListingResponseSchema
from utils.util import (
    get_paginated_listings,
    get_s3_url_for_file_urls,
    get_total_count,
    save_listing,
    search_by_username,
    upload_csv_rows_to_db,
    upload_files_to_s3,
    fetch_product_from_id,
    upload_temp_image_file_to_s3,
    bulk_delete_listing_by_id,
    save_listing,
    create_new_user
)
from exceptions import (
    NoBase64ImageFound,
    UserNotFoundException,
    NoCredentialsError,
    WrongImageUrlException,
)
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import timedelta
import logging
from webargs.flaskparser import use_args

application = Flask(__name__)



# os.environ.get("OPENAI_API_KEY")
OPEN_API_KEY = "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"
JWT_TOKEN_EXPIRY_TIME_HRS = 24

# Directory where uploaded images will be temporarily stored
UPLOAD_FOLDER = "uploads"

application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
application.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI"
)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(application)

# Configure the Flask app for JWT
application.config[
    "JWT_SECRET_KEY"
] = "your-1231231-3213131-bhbubadbfh-bhjbhjbsab"  # os.getenv("JWT_SECRET_KEY") Change this to a strong secret key in production
jwt = JWTManager(application)


@application.route("/health", methods=["GET"])
@cross_origin(origin="*")
def index():
    return {"message": "katalis Ver-1.0 running fine"}


CORS(application, origins="*")

# Create a route for user login and issue JWT token


@application.route("/create-table", methods=["POST"])
@cross_origin(origin="*")
def create_table():
    log.info("request /create_basic tables")
    data = request.get_json()
    if data["table"] == "user":
        create_user_table(db)
        return jsonify({"message": "successfully created user table"}), 200
    elif data["table"] == "product":
        create_products_table(db)
        return jsonify({"message": "successfully created products table"}), 200
    return jsonify({"message": "please choose correct method"}), 400


# Create a route for user login and issue JWT token
@application.route("/login", methods=["POST"])
def login():
    try:
        log.info("request /login")
        error = LoginSchema().validate(request.get_json())
        if error != {}:
            return {"details": error}, 400
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        result = search_by_username(db, username)

        expires = timedelta(hours=JWT_TOKEN_EXPIRY_TIME_HRS)
        if match_password(result["password"], password):
            access_token = create_access_token(
                identity=result["id"], expires_delta=expires
            )
            return jsonify(access_token=access_token), 200
        else:
            log.info("wrong password can not return token")
            return jsonify(message="Invalid credentials"), 401

    except UserNotFoundException:
        return jsonify({"message": "User not found exception"}), 404


def match_password(password, db_password):
    return password == db_password



@application.route("/internal/create", methods=["POST"])
def create_user():
    log.info("request /internal/create")
    error = RegistrationSchema().validate(request.get_json())
    if error != {}:
        return {"details": error}, 400
    try:
        data = request.get_json()
        fullName = data.get("fullName")
        userName = data.get("userName")
        password = data.get("password")
        phoneNumber = data.get("phoneNumber")
        email = data.get("email")
        create_new_user(db,fullName,userName,password,phoneNumber,email)
        return jsonify({"message": "User created successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error in creating user"},e), 404
    


@application.route("/magic/description", methods=["POST"])
@jwt_required()
def open_ai_description():
    log.info("request /magic/description")
    error = OpenAiDescriptionSchema().validate(request.get_json())
    if error != {}:
        return {"details": error}, 400
    prompt = request.get_json()
    log.info(prompt.get("type"))

    return generatePromptOutput(request.get_json())


@application.route("/magic/listings", methods=["GET"])
@jwt_required()
def fetch_listings():
    log.info("request GET : /magic/listings")

    items_per_page = 40

    page = int(request.args.get("page", 1))
    offset = (page - 1) * items_per_page
    user_id = get_jwt_identity()

    results = get_paginated_listings(db, user_id, items_per_page, offset)
    myprod = GetListingResponseSchema(many=True)

    # TODO : find how to properly do it without looping
    sa = myprod.dump(results)
    finalResult = []
    for r in sa:
        r["description"] = (
            json.loads(r["description"])
            if r["description"] != None
            else {"bahasa": "", "english": ""}
        )
        images = json.loads(r["imageUrls"]) if r["imageUrls"] != None else []
        result = []
        for image in images:
            image = getListingBucketPrefix() + image
            result.append(image)
        r["imageUrls"] = result
        finalResult.append(r)

    total_items = get_total_count(db, user_id)
    total_pages = math.ceil(total_items / items_per_page)

    return {"current_page": page, "total_pages": total_pages, "data": finalResult}, 200


def generate_uuid4():
    return str(uuid.uuid4())


@application.route("/get/listing/id", methods=["POST"])
def fetch_listing_by_id():
    product = request.get_json().get("id")
    if product:
        product_data = fetch_product_from_id(db, product)
        if product_data != False:
            data = {
                "id": product_data.id,
                "title": product_data.title,
                "imageUrls": json.loads(product_data.imageUrls),
                "description": json.loads(product_data.description),
            }
            return jsonify(data)
        else:
            return jsonify({"message": "Product not found"}, 404)
    else:
        return jsonify({"message": "Product not found"}, 404)


@application.route("/delete/listings", methods=["DELETE"])
@cross_origin(origin="*")
@jwt_required()
def delete_product_by_id():
    error = BulkDeleteSchema().validate(request.get_json())
    if error != {}:
        return {"details": error}, 400

    product_ids = request.get_json().get("ids")
    log.info(product_ids)
    if len(product_ids) > 0:
        # check product id is correct or not
        bulk_delete_listing_by_id(db, product_ids)
        return jsonify({"message": "Successfully deleted"}), 200
    return jsonify({"message": "No ids input"}), 400


@application.route("/convert_base64_image", methods=["POST"])
def convert_base64_image():
    # Get the Base64 image URL from the request

    try:
        data = request.get_json()
        log.info("request /convert_base64_image")
        error = ConvertBase64ImageSchema().validate(data)
        if error != {}:
            return {"details": error}, 400

        base64_image_data_uri = data["base64_image"]

        # Extract the Base64 image data from the data URI
        base64_image = extract_base64_image(base64_image_data_uri)

        image_data = base64.b64decode(base64_image)

        image = Image.open(BytesIO(image_data))
        if image.mode == "RGB":
            image = image.convert("RGBA")

        # Save the image with a unique name
        image_filename = f"image_{os.urandom(4).hex()}.png"
        image.save(image_filename, "PNG")

        # Upload the image to AWS S3
        upload_temp_image_file_to_s3(image_filename)

        # Remove the locally saved image
        os.remove(image_filename)
        return jsonify(
            {
                "message": "Saved temporary file",
                "imageUrl": getTempBucketPrefix() + f"{image_filename}",
            }
        )

    except NoBase64ImageFound:
        return (
            jsonify(
                {
                    "error": "Invalid data URI or unsupported image format. Make sure base64 Image starts with data:image/png;base64 or data:image/jpg;base64"
                }
            ),
            400,
        )
    except Exception as e:
        os.remove(image_filename)
        return jsonify({"error": str(e)}), 500


@application.route("/magic/listing", methods=["POST"])
@cross_origin(origin="*")
@jwt_required()
def save_or_update_listings():
    log.info("request POST : /magic/listing")
    error = SaveListingSchema().validate(request.form)
    if error != {}:
        return {"details": error}, 400

    # TODO : Request filter every file size max 6-8 mb and
    # TODO : Request filter max number of files allowed

    data = SaveListingSchema().load(request.form)
    list_id = get_list_id_if_not_present(data)
    result_new_file_urls = upload_files_to_s3(list_id, request.files)
    result_new_file_urls += get_s3_url_for_file_urls(
        list_id, json.loads(data["imageUrls"])
    )
    data["imageUrls"] = json.dumps(result_new_file_urls)
    user_id = get_jwt_identity()
    save_listing(db, list_id, user_id, data, "DONE")
    return jsonify({"message": "successfully saved listing into DB"}), 200


def get_list_id_if_not_present(data):
    if "id" in data and data["id"] != "":
        return data["id"]
    return generate_uuid4()


@application.route("/magic/image", methods=["POST"])
@jwt_required()
def open_ai_image_edit():
    try:
        log.info("request /magic/image")
        error = OpenAiImageSchema().validate(request.form)
        if error != {}:
            return {"details": error}, 400

        # TODO : Can also validate if image is in required ratio
        # Check if the POST request has the file part
        if request.form["image"] == None and (request.form["imageUrl"] == None):
            return jsonify({"error": "No image found"}), 400

        # Check if the file is empty
        if request.form["image"] == "" and request.form["imageUrl"] == "":
            return jsonify({"error": "No image found"}), 400

        file = request.form["image"] if "image" in request.form else None
        mask = (
            request.form["mask"]
            if ("mask" in request.form and request.form["mask"] != "")
            else None
        )
        prompt = request.form["prompt"]
        imageUrl = request.form["imageUrl"]

        if imageUrlExist(imageUrl):
            return imageEditThroughImageUrl(
                imageUrl=imageUrl, maskFileBase64=mask, prompt=prompt
            )
        else:
            return imageEditThroughImageFile(
                imageFileBase64=file, maskFileBase64=mask, prompt=prompt
            )
    except WrongImageUrlException:
        log.info(
            f"error : Unable to open image after download from the imageUrl, imageUrl may not contain image"
        )
        return (
            jsonify(
                {"message": "Wrong image url, imageUrl may not contain url of a image"}
            ),
            400,
        )
    except NoBase64ImageFound:
        log.info(f"error : No base 64 image found error")
        return (
            jsonify(
                {
                    "message": "No base64 Image found, Make sure base64 Image starts with data:image/png;base64 or data:image/jpg;base64"
                }
            ),
            400,
        )
    except openai.error.RateLimitError as e:
        log.error(f"error : {e}")
        return jsonify({"message": f"Error: {e}"}), 429
    except openai.error.InvalidRequestError as e:
        log.error(f"error : {e}")
        return jsonify({"message": f"Error: {e}"}), 400


def imageEditThroughImageUrl(imageUrl, maskFileBase64, prompt):
    try:
        log.info("calling image optimise api with image URL")
        imageFilename = generateTempFileName()
        download_file(
            imageUrl, os.path.join(application.config["UPLOAD_FOLDER"], imageFilename)
        )
        imageFile = filter_convert_image_to_rgba(
            os.path.join(application.config["UPLOAD_FOLDER"], imageFilename)
        )
        maskFile = None
        if maskFileExist(maskFileBase64):
            log.info("adding mask to the image")
            maskFile = getImageBytesArrayFromBase64(maskFileBase64)
        response = callOpenAI(OPEN_API_KEY, imageFile, maskFile, prompt)
        delete_file(os.path.join(application.config["UPLOAD_FOLDER"], imageFilename))

        return response
    except PIL.UnidentifiedImageError as e:
        log.info(f"unable top open uploaded url {e}")
        delete_file(os.path.join(application.config["UPLOAD_FOLDER"], imageFilename))
        raise WrongImageUrlException


def imageEditThroughImageFile(imageFileBase64, maskFileBase64, prompt):
    log.info("calling image optimise api with image binary file")
    imageFile = getImageBytesArrayFromBase64(imageFileBase64)
    maskFile = None
    if maskFileExist(maskFileBase64):
        log.info("adding mask to the image")
        maskFile = getImageBytesArrayFromBase64(maskFileBase64)
    response = callOpenAI(OPEN_API_KEY, imageFile, maskFile, prompt)
    return response


def maskFileExist(mask):
    return mask != None and mask != ""


def imageUrlExist(imageUrl):
    return imageUrl != None and imageUrl != ""


def generateTempFileName():
    return str(uuid.uuid4()) + ".png"


def process_image_file(file):
    # Check if the file has an allowed extension
    # Generate a secure filename
    filename = secure_filename(file.filename)

    # Save the file to the UPLOAD_FOLDER

    return filename


@application.route("/magic/upload-prods", methods=["POST"])
@jwt_required()
def upload_listings_csv():
    log.info("request POST : /magic/upload-prods")
    error = CSVUploadSchema().validate(request.form)
    if error != {}:
        return {"details": error}, 400
        # Validate the request data

    data = CSVUploadSchema().load(request.form)
    file_data = data["file"]

    # Perform additional validations for file size and row count
    max_file_size = 10 * 1024 * 1024  # 10MB
    max_rows = 1000

    if file_data.content_length > max_file_size:
        return {"message": "File size exceeds the maximum allowed : 10mb"}, 400

    # Split CSV data into rows and validate row count
    rows = file_data.split("\n")
    if len(rows) > max_rows:
        return {"message": "Number of rows exceeds the maximum allowed."}, 400

    if validate_header_columns(rows):
        return {"message": "invalid csv format : id, title, english, bahasa"}, 400

    user_id = get_jwt_identity()
    
    upload_csv_rows_to_db(db, user_id, rows)

    return {"message": "CSV data saved successfully.", "pre_signed_url": ""}, 201


@application.route("/magic/bulk-upload", methods=["POST"])
@cross_origin(origin="*")
@jwt_required()
def upload_product_list_csv():
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return {"error": "No selected file"}, 400

    # Check if the file is a CSV
    max_file_size = 10 * 1024 * 1024
    if file and file.filename.endswith('.csv') and file.content_length <= max_file_size:
        try:
            df = pd.read_csv(file)
            print(type( df))
            user_id = get_jwt_identity()
            if len(df) > 1000:
                return {"error": "CSV length is too much (more than 1000 rows)"}, 400


            for index, row in df.iterrows():
                
                if validate_csvfile_columns(row):
                    return {"message": "invalid csv format :  title, english, bahasa"}, 400
                description = {"english": row["english"], "bahasa": row["bahasa"]}
                
                title = row['title']
                image_urls = '{"url": "hii"}'
                description = json.dumps(description)
                save_listing(db,user_id, title, image_urls,description,"IN_PROGRESS")
                
            return {"message": "CSV data uploaded and processed successfully"}, 200
        except Exception as e:
            return {"error": "An error occurred while processing the CSV file"}, 500
    else:
        return {"error": "Uploaded file is not a CSV"}, 400
        





@application.route("/magic/remove-bg", methods=["POST"])
@jwt_required()
def remove_background():
    log.info("request POST : /magic/remove-bg")
    error = RemoveBackgroundImageSchema().validate(request.form)
    if error != {}:
        return {"details": error}, 400
    base64_image_data_uri = request.form["image"]
    base64_image = extract_base64_image(base64_image_data_uri)
    image_data = base64.b64decode(base64_image)
    input_image = Image.open(BytesIO(image_data))
    output_image = remove(
        input_image,
        session=new_session("u2net"),
        only_mask=False,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
        alpha_matting_base_size=4000,
    )
    log.info("successfully removed background")
    if output_image.mode == "RGB":
        output_image = output_image.convert("RGBA")
    image_filename = f"image_{os.urandom(4).hex()}.png"
    output_image.save(image_filename, "PNG")
    upload_temp_image_file_to_s3(image_filename)
    os.remove(image_filename)
    # output_image = remove(input_image, bgcolor=(255, 25, 25, 25))
    # Write the output image
    return {"imageUrl": f"{getTempBucketPrefix()}{image_filename}"}, 200


@application.route("/magic/mask", methods=["POST"])
@jwt_required()
def create_mask():
    log.info("request POST : /magic/mask")
    error = CreateMaskSchema().validate(request.form)
    if error != {}:
        return {"details": error}, 400
    base64_image_data_uri = request.form["image"]
    base64_image = extract_base64_image(base64_image_data_uri)
    image_data = base64.b64decode(base64_image)
    input_image = Image.open(BytesIO(image_data))
    output_image = remove(
        input_image,
        session=new_session("u2net"),
        only_mask=True,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )
    if "invertMask" in request.form and request.form["invertMask"] == "True":
        output_image = ImageOps.invert(output_image)
    log.info("successfully removed background")
    if output_image.mode == "RGB":
        output_image = output_image.convert("RGBA")
    image_filename = f"image_{os.urandom(4).hex()}.png"
    output_image.save(image_filename, "PNG")
    upload_temp_image_file_to_s3(image_filename)
    os.remove(image_filename)
    # output_image = remove(input_image, bgcolor=(255, 25, 25, 25))
    # Write the output image
    return {"imageUrl": f"{getTempBucketPrefix()}{image_filename}"}, 200


def validate_header_columns(row):
    if (
        row[0] == "id"
        and row[1] == "title"
        and row[2] == "english"
        and row[3] == "bahasa"
    ):
        return True
    return False

def validate_csvfile_columns(row):
    if(
        row[0] == "title"
        and row[2] == "english"
        and row[3] == "bahasa"
    ):
        return True
    return False
    


if __name__ == "__main__":
    application.run()

    # application.run(port=8001)
