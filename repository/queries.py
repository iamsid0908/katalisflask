def get_fetch_error():
    return Exception("Fetch record operation could not be completed")


def update_error():
    return Exception("Error Occured while updating record")


def delete_error():
    return Exception("Error Occured while deleting record")


CREATE_DATABASE_KATALIS = """
create database katalis;
"""

CREATE_USER_TABLE = """
CREATE TABLE user (
    pk int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id varchar(255) NOT NULL UNIQUE,
    fullName VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phoneNumber VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phoneVerified BOOLEAN DEFAULT 0,
    emailVerified BOOLEAN DEFAULT 0,
    usertype VARCHAR(50) NOT NULL,
    rowCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
    rowUpdated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

CREATE_LISTING_TABLE = """
CREATE TABLE katalis.products (
    pk int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id varchar(255) NOT NULL UNIQUE,
    user_id varchar(255) NOT NULL,
    title VARCHAR(255),
    imageUrls JSON,
    description JSON,
    status VARCHAR(50) NOT NULL,
    rowCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
    rowUpdated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES katalis.user(id)
);
"""

GET_LISTING_PAGINATED = """
    SELECT *
    FROM katalis.products
    where 
    pk < '{before_id}' and
    user_id= '{user_id}'
    ORDER BY pk DESC
    LIMIT {limit}
"""

GET_LISTING_PAGINATED_ONLY_LIMIT = """
    SELECT *
    FROM katalis.products
    where 
    user_id= '{user_id}'
    ORDER BY pk DESC
    LIMIT {limit}
"""


GET_LISTING_TOTAL_COUNT = """
    SELECT COUNT(*)
    FROM katalis.products
    where 
    user_id= '{user_id}'
"""
GET_LISTING_PAGINATED_LIMIT_OFFSET = """
    SELECT *
    FROM katalis.products
    where 
    user_id= '{user_id}'
    ORDER BY pk DESC
    LIMIT {limit}
    OFFSET {offset}
"""

# imageUrls = '["https://example.com/image1.jpg", "https://example.com/image2.jpg"]'
# description = '{"english": "Product description in English", "bahasa": "Product description in Bahasa"}'
# status = 'IN_PROGRESS' or 'DONE'
INSERT_LISTING = """
INSERT INTO katalis.products (id, user_id, title, imageUrls, description, status)
VALUES
    ('{id}','{user_id}', '{title}', '{imageUrls}', '{description}', '{status}')
"""

INSERT_UPDATE_LISTING = """
INSERT INTO katalis.products (id, user_id, title, imageUrls, description, status)
VALUES
    ('{id}','{user_id}', '{title}', '{imageUrls}', '{description}', '{status}')
ON DUPLICATE KEY UPDATE
  title = VALUES(title),
  imageUrls = VALUES(imageUrls),
  description = VALUES(description),
  status = VALUES(status);
"""


INSERT_BULK_LISTING = """
INSERT INTO katalis.products (id, user_id, title, imageUrls, description, status)
VALUES
    (:id, :user_id, :title, :imageUrls, :description, :status)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    imageUrls = VALUES(imageUrls),
    description = VALUES(description),
    status = VALUES(status);
"""


CREATE_USER = """
INSERT INTO katalis.user (id, fullName, username, password, phoneNumber, email, phoneVerified, emailVerified, usertype)
VALUES
    ('{id}', '{fullName}', '{username}', '{password}', '{phoneNumber}', '{email}', '{phoneVerified}', '{phoneVerified}','{usertype}')
"""

BULK_INSERT_LISTING = """
INSERT INTO katalis.products (user_id, title, imageUrls, description, status)
VALUES
    {bulkListingValues}
"""

GET_USER_BY_USERNAME = """
    SELECT id,
        usertype,
        phoneNumber,
        email,
        phoneVerified,
        emailVerified,
        password,
        rowCreated,
        rowUpdated
    FROM
    katalis.user
    WHERE 
        username='{username}';
    """


GET_LISTING_BY_ID = """
    SELECT 
    id,
    title ,
    imageUrls,
    description FROM katalis.products WHERE id='{list_id}';
     """


GET_LISTING_BY_USER_ID = """
    SELECT * FROM
    katalis.products
    WHERE user_id ='{user_id}';
    """

GET_USER_BY_ID = """
    SELECT id, 
        fullName,
        usertype,
        phone_number,
        email,
        phone_verified,
        email_verified,
        row_created
    FROM
    katalis.user
    WHERE 
        id='{user_id}';
    """

UPDATE_PASSWORD = """
    UPDATE
    katalis.user
        SET password='{password}'
    WHERE 
        id='{user_id}'
    RETURNING *;
    """

DELETE_LISTING_BY_ID = """
DELETE FROM katalis.products
WHERE id='{list_id}';
"""

BULK_DELETE_LISTING_BY_ID = """
DELETE FROM katalis.products
WHERE id in ({list_ids_str});
"""

Queries = {
    "CREATE_USER_TABLE": CREATE_USER_TABLE,
    "GET_LISTING_PAGINATED": GET_LISTING_PAGINATED,
    "GET_LISTING_PAGINATED_ONLY_LIMIT": GET_LISTING_PAGINATED_ONLY_LIMIT,
    "GET_LISTING_PAGINATED_LIMIT_OFFSET": GET_LISTING_PAGINATED_LIMIT_OFFSET,
    "GET_LISTING_TOTAL_COUNT": GET_LISTING_TOTAL_COUNT,
    "CREATE_LISTING_TABLE": CREATE_LISTING_TABLE,
    "INSERT_UPDATE_LISTING": INSERT_UPDATE_LISTING,
    "INSERT_LISTING": INSERT_LISTING,
    "CREATE_USER": CREATE_USER,
    "GET_USER_BY_USERNAME": GET_USER_BY_USERNAME,
    "UPDATE_PASSWORD": UPDATE_PASSWORD,
    "GET_USER_BY_ID": GET_USER_BY_ID,
    "BULK_INSERT_LISTING": BULK_INSERT_LISTING,
    "GET_LISTING_BY_ID": GET_LISTING_BY_ID,
    "GET_LISTING_BY_USER_ID": GET_LISTING_BY_USER_ID,
    "DELETE_LISTING_BY_ID": DELETE_LISTING_BY_ID,
    "BULK_DELETE_LISTING_BY_ID": BULK_DELETE_LISTING_BY_ID,
    "INSERT_BULK_LISTING":INSERT_BULK_LISTING
}
