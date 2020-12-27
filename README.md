# covid_api


## Install Dependencies

pip install -r requirements.txt


## Setup Database

python manage.py db init  
python manage.py db migrate  
python manage.py db upgrade  


## Run Server

python run.py


## To send E-mail with image of COVID API Response

Configure Sender's Email and Password in app/covid/mail_helper.py file


### Register
* POST
* endpoint: /v1/auth/register
* body: {
            "first_name": "{f_name}",
            "last_name": "{l_name}",
            "email": "{e-mail}",
            "password": "{pwd}",
            "country": "{country}"
        }


### Login
* POST
* endpoint: /v1/auth/login
* body: {
            "email": "{registered_email}",
            "password": "{password}"
        }


### Logout
* POST
* endpoint: /v1/auth/logout
* Header: Authorization Bearer {token}


### Get Covid Data
* GET
* endpoint: /v1/get_covid_data
* parameters: country, from_date {YYYY-MM-DD}, to_date {YYYY-MM-DD}


### Export Data
* GET
* endpoint: /v1/export_covid_data
* parameters: country, from_date {YYYY-MM-DD}, to_date {YYYY-MM-DD}
