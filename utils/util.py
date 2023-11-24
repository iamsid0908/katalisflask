from dateutil import tz
from repository.commands import DBUtil
from exceptions import UserNotFoundException
import requests
import random
import string
from io import BytesIO
import uuid
import boto3

from utils.s3_helper import ObjectWrapper
from commons.logger_config import log

s3_resource = boto3.resource("s3")
BUCKET_NAME = "magic-studio-images"
AWS_BUCKET_NAME = "image-upload-base64-normal-image"

s3 = boto3.client(
    "s3",
)

BUCKET_PREFIX = "https://magic-studio-images.s3.ap-south-1.amazonaws.com/"
TEMP_IMAGE_BUCKET_PREFIX = "https://image-upload-base64-normal-image.s3.amazonaws.com/"


def get_ist(now):
    try:
        to_zone = tz.gettz("Asia/Kolkata")
        converted = now.astimezone(to_zone)
        return converted
    except Exception as e:
        return now


def get_utc(now):
    try:
        to_zone = tz.gettz("UTC")
        converted = now.astimezone(to_zone)
        return converted
    except Exception as e:
        return now


def fetch_user_from_id(db, user_id):
    user = DBUtil.get_user_by_id(user_id)
    res = user.one_or_none()
    if res is None:
        raise UserNotFoundException
    return res


def fetch_product_from_id(db, list_id):
    product = DBUtil.getProductById(db, list_id)
    res = product.one_or_none()
    if res is None:
        return False
    return res


def delete_listing_by_id(db, list_id):
    DBUtil.deleteListById(db, list_id)


def bulk_delete_listing_by_id(db, list_ids):
    log.info("bulk delete product ids")
    DBUtil.bulkDeleteListByIds(db, list_ids)


def search_by_username(db, username):
    user = DBUtil.get_user_by_username(db, username)
    res = user.one_or_none()
    if res is None:
        raise UserNotFoundException
    return res


def save_listing(db, list_id, user_id, data, status):
    result = DBUtil.save_or_update_listing(
        db,
        list_id,
        user_id,
        data["title"],
        data["imageUrls"],
        format_description_for_sql_db(data["description"]),
        status,
    )
    return result


def format_description_for_sql_db(input):
    result = input.replace("\\n", "\\\\n")
    result = result.replace("'", "\\'")
    return result


def get_all_listings(db, user_id):
    result = DBUtil.fetch_listings(db, user_id)
    return result.all()


def get_paginated_listings(
    db,
    user_id,
    limit,
    offset,
):
    result = DBUtil.get_paginated_listings_limit_offset(db, user_id, limit, offset)
    return result.all()


def get_total_count(db, user_id):
    result = DBUtil.get_listings_total_count(db, user_id)
    return result


def isBeforeIdPresent(before_id):
    return before_id is None or before_id == ""


def create_user_table(db):
    DBUtil.create_user_table(db)
    return True


def create_products_table(db):
    DBUtil.create_products_table(db)
    return True


def upload_files_to_s3(list_id, request_files):
    files = request_files.getlist("imageFiles")
    result = []
    for file in files:
        object_key = (
            f"{list_id}/" + generate_random_text() + get_extension(file.filename)
        )
        s3.upload_fileobj(file, BUCKET_NAME, object_key)
        result.append(object_key)

    return result


def get_extension(filename):
    if filename.endswith(".png"):
        return ".png"
    else:
        return ".jpg"


def generate_random_text(length=5):
    characters = string.ascii_letters + string.digits
    random_text = "".join(random.choice(characters) for _ in range(length))
    return random_text


def get_s3_url_for_file_urls(list_id, imageUrls):
    result = []
    for imageUrl in imageUrls:
        response = requests.get(imageUrl)
        response.raise_for_status()
        file = response.content
        bucket = s3_resource.Bucket(BUCKET_NAME)
        object_key = f"{list_id}/" + generate_random_text() + ".png"
        obj_wrapper = ObjectWrapper(bucket.Object(object_key))
        obj_wrapper.put(BytesIO(file))
        result.append(object_key)
    return result


def get_temp_s3_url_for_file_single_url(imageUrl):
    response = requests.get(imageUrl)
    response.raise_for_status()
    file = response.content
    bucket = s3_resource.Bucket(AWS_BUCKET_NAME)
    object_key = generate_random_text() + ".png"
    obj_wrapper = ObjectWrapper(bucket.Object(object_key))
    obj_wrapper.put(BytesIO(file))
    return object_key


def generate_uuid4():
    return str(uuid.uuid4())

def upload_csv_rows_to_db(db, user_id, rows):
    DBUtil.insert_listing_using_csv(db,user_id, rows)


def save_listing(db, user_id, title, image_urls,description, status):
   list_id = generate_uuid4() 
   result= DBUtil.save_or_update_listing(db, list_id, user_id, title, image_urls,description ,status)
   return result
    
def upload_temp_image_file_to_s3(image_filename):
    s3.upload_file(image_filename, AWS_BUCKET_NAME, image_filename)


def getTempBucketPrefix():
    return TEMP_IMAGE_BUCKET_PREFIX


def getListingBucketPrefix():
    return BUCKET_PREFIX

def create_new_user(db,fullName,userName,password,phoneNumber,email):
    user_id = generate_uuid4()
    result = DBUtil.create_user(db,user_id,fullName,userName,password,phoneNumber,email,1,1,"user")
    return result
    