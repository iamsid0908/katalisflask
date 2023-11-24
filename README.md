## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   $ cd Katalis-Backend
   ```

4. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

8. Run the app:

   ```bash
   $ flask run
   $ flask run -h localhost -p 7000
   ```

9. Check if system running by pasting url to chrome

   ```bash
   $ http://127.0.0.1:5000/health
   ```


# Connecting database

1. Install MySQL server on your local computer
2. Add db connetion url to SQLALCHEMY_DATABASE_URI in .env file
3. Uncommment create table API
4. Run create Table API with Postman

# Postman Collection URL
