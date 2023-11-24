from .queries import Queries, get_fetch_error, update_error, delete_error
from commons.db_helpers import normalised_response

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, text
from sqlalchemy import insert
import uuid
import csv
import pandas as pd



def generate_uuid4():
    return str(uuid.uuid4())


def get_insert_exception():
    return Exception("Insert table DB operation could not be completed")


def get_update_exception():
    return Exception("Update table DB operation could not be completed")


def get_query_format_exception(e):
    return Exception(f"can not format query: {e}")


def get_delete_exception():
    return Exception("Delete table DB operation could not be completed")


def get_fetch_exception():
    return Exception("Fetch table DB operation could not be completed")


def unique_key_violation():
    return Exception("Unique key violation error")


class DBUtil:
    @staticmethod
    def create_user_table():
        query = Queries["CREATE_USER"]
        try:
            result = db.engine.execute(query)
            return normalised_response(result)
        except Exception:
            raise update_error()

    @staticmethod
    def create_listing_table():
        query = Queries["CREATE_LISTING_TABLE"]
        try:
            result = db.engine.execute(query)
            return normalised_response(result)
        except Exception:
            raise update_error()

    @staticmethod
    def create_user(
        db,
        user_id,
        fullName,
        username,
        password,
        phoneNumber,
        email,
        phoneVerified,
        emailVerified,
        usertype,
    ):
        query = Queries["CREATE_USER"].format(
            id = user_id,
            username = username,
            fullName = fullName,
            password = password,
            phoneNumber = phoneNumber,
            email = email,
            phoneVerified = phoneVerified,
            emailVerified = emailVerified,
            usertype = usertype,
        )
        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            connection.commit()
            # return normalised_response(result)
        except Exception as e:
            print(e)
            raise update_error()

    @staticmethod
    def get_user_by_username(db, username):
        query = Queries["GET_USER_BY_USERNAME"].format(username=username)
        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            return result.mappings()
        except Exception:
            raise get_fetch_error()

    @staticmethod
    def set_user_password(userid, password):
        query = Queries["UPDATE_PASSWORD"].format(user_id=userid, password=password)
        try:
            result = db.engine.execute(query)
            return normalised_response(result)
        except Exception:
            raise update_error()

    @staticmethod
    def get_user_by_id(user_id):
        query = Queries["GET_USER_BY_ID"].format(user_id=user_id)
        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            return result.mappings()
        except Exception:
            raise update_error()

    @staticmethod
    def save_or_update_listing(
        db, list_id, user_id, title, imageUrls, description, status="DONE"
    ):
        try:
            query = Queries["INSERT_UPDATE_LISTING"].format(
                id=list_id,
                user_id=user_id,
                title=title,
                imageUrls=imageUrls,
                description=description,
                status=status,
            )
            connection = db.engine.connect()
            result = connection.execute(text(query))
            connection.commit()
            if result.rowcount < 1:
                raise get_insert_exception()
        except exc.IntegrityError as e:
            return []
        except Exception as e:
            print(e)
            raise get_update_exception()
    
    @staticmethod
    def fetch_listings(db, user_id):
        try:
            query = Queries["GET_LISTING_BY_USER_ID"].format(user_id=user_id)
            connection = db.engine.connect()
            result = connection.execute(text(query))
            return result.mappings()
        except Exception as e:
            raise get_fetch_exception()

    @staticmethod
    def create_products_table(db):
        query = Queries["CREATE_LISTING_TABLE"]
        connection = db.engine.connect()
        connection.execute(text(query))
        connection.commit()

    @staticmethod
    def create_user_table(db):
        query = Queries["CREATE_USER_TABLE"]
        connection = db.engine.connect()
        connection.execute(text(query))
        connection.commit()

    @staticmethod
    def get_paginated_listing(db, user_id, limit, before_id):
        # Create a database connection
        connection = db.engine.connect()
        query = Queries["GET_LISTING_PAGINATED"].format(
            limit=limit, before_id=before_id, user_id=user_id
        )
        # Define the SQL query
        sql = text(query)
        # Execute the SQL query with provided parameters
        result = connection.execute(sql)
        return result.mappings()

    @staticmethod
    def get_paginated_listings_limit_offset(db, user_id, limit, offset):
        # Create a database connection
        connection = db.engine.connect()
        query = Queries["GET_LISTING_PAGINATED_LIMIT_OFFSET"].format(
            limit=limit, offset=offset, user_id=user_id
        )
        # Define the SQL query
        sql = text(query)
        # Execute the SQL query with provided parameters
        result = connection.execute(sql)
        return result.mappings()

    @staticmethod
    def get_listings_total_count(db, user_id):
        # Create a database connection
        connection = db.engine.connect()
        query = Queries["GET_LISTING_TOTAL_COUNT"].format(user_id=user_id)
        # Define the SQL query
        sql = text(query)
        # Execute the SQL query with provided parameters
        result = connection.execute(sql)
        return result.fetchone()[0]

    @staticmethod
    def get_top_paginated_listing(db, user_id, limit):
        # Create a database connection
        connection = db.engine.connect()
        query = Queries["GET_LISTING_PAGINATED_ONLY_LIMIT"].format(
            limit=limit, user_id=user_id
        )
        # Define the SQL query
        sql = text(query)
        # Execute the SQL query with provided parameters
        result = connection.execute(sql)
        return result.mappings()

    @staticmethod
    def insert_listing_using_csv(db, user_id, rows):
        query = Queries["INSERT_LISTING"]
        connection = db.engine.connect()
        connection.execute(text(query))
        connection.commit()

        cursor = connection.cursor()

        for row in csv.reader(rows):
            # format id, title, bahasa, english
            # Assuming the first row contains column headers
            if row[0] != "id":
                description = {"english": row[1], "bahasa": row[2]}
                imageUrls = []
                query = Queries["INSERT_UPDATE_LISTING"].format(
                    id=row[0],
                    user_id=user_id,
                    title=row[0],
                    imageUrls=imageUrls,
                    description=description,
                    status="IN_PROGRESS",
                )
                cursor.execute(text(query))

        connection.commit()
        cursor.close()
        connection.close()


        

    @staticmethod
    def getProductById(db, list_id):
        query = Queries["GET_LISTING_BY_ID"].format(list_id=list_id)
        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            return result.mappings()
        except Exception:
            raise get_fetch_error()

    @staticmethod
    def deleteListById(db, list_id):
        query = Queries["DELETE_LISTING_BY_ID"].format(list_id=list_id)

        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            connection.commit()
            return True
        except Exception:
            raise delete_error()

    @staticmethod
    def bulkDeleteListByIds(db, list_ids):
        list_ids_str = ",".join(['"{}"'.format(item) for item in list_ids])
        print(list_ids_str)
        query = Queries["BULK_DELETE_LISTING_BY_ID"].format(list_ids_str=list_ids_str)
        try:
            connection = db.engine.connect()
            result = connection.execute(text(query))
            connection.commit()
            return True
        except Exception:
            raise delete_error()
