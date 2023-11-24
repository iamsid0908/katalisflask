import PIL
import requests
from PIL import Image
import io
import os
from commons.logger_config import log
from exceptions import NoBase64ImageFound
import base64
from PIL import Image
from io import BytesIO

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        with open(local_path, "wb") as file:
            file.write(response.content)

        print(f"File '{local_path}' has been downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def filter_convert_image_to_rgba(image_path):
    try:
        if image_path != None:
            image = Image.open(image_path)
            image_mode = image.mode
            if image_mode == "RGB":
                image = image.convert("RGBA")

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            return img_byte_arr
        return None

    except PIL.UnidentifiedImageError as e:
        raise PIL.UnidentifiedImageError


def getImageBytesArrayFromBase64(base64_image_data_uri):
    base64_image = extract_base64_image(base64_image_data_uri)
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))
    print(f"{image.size}")
    if image.mode == "RGB":
        image = image.convert("RGBA")

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def extract_base64_image(data_uri):
    # Split the data URI into its parts
    parts = data_uri.split(",")

    if len(parts) != 2:
        raise NoBase64ImageFound

    data_type, base64_data = parts
    allowed_base_64 = [
        "data:image/png;base64",
        "data:image/jpeg;base64",
        "data:image/jpg;base64",
    ]
    if data_type in allowed_base_64:
        return base64_data

    raise NoBase64ImageFound


def delete_file(file_path):
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)


# Function to check if a file has an allowed extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
