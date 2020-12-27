import os
from flask import Blueprint, request, abort
from app.auth.helper import token_required
from app.covid.helper import response, response_with_covid_data
from app.models import User
from app.covid.mail_helper import send_email
from pycountry import countries
import requests
import json
from datetime import datetime, timedelta
import plotly.express as px

# Initialize blueprint
covid = Blueprint('covid', __name__)

URL = "http://corona-api.com/countries/{}"
CURRENT_TIME = datetime.utcnow()
DIR = os.path.abspath(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(DIR, "images")


def is_valid_date(from_date, to_date):
    try:
        datetime.strptime(from_date, "%Y-%m-%d")
        datetime.strptime(to_date, "%Y-%m-%d")
    except Exception as e:
        return False

    if from_date > to_date:
        return False

    return True


def get_filtered_data(country_code, from_date, to_date):

    url = URL.format(country_code)
    param = json.dumps({"include": "timeline"})
    resp = requests.get(url=url, params=param, timeout=30)
    data = resp.json().get('data')

    start = 0
    end = 0

    for each in data.get('timeline'):
        if each.get('date') <= to_date:
            break
        start += 1
        end += 1

    for each in data.get('timeline')[start:]:
        if each.get('date') < from_date:
            break
        end += 1

    data['timeline'] = data['timeline'][start:end]
    return data


@covid.route('/get_covid_data/', methods=['GET'])
@token_required
def get_covid_data(current_user):
    """
    Return response of covid api with from and to date filter
    :param current_user:
    :return:
    """
    user = User.get_by_id(current_user.id)
    country = request.args.get('country', user.country)
    country = countries.get(name=country)
    if not country:
        return response(
            status='failed',
            message='Invalid Country',
            code=400
        )
    country_code = country.alpha_2
    from_date = request.args.get('from_date', (CURRENT_TIME-timedelta(days=15)).strftime("%Y-%m-%d"))
    to_date = request.args.get('to_date', CURRENT_TIME.strftime("%Y-%m-%d"))

    if not is_valid_date(from_date, to_date):
        return response(
            status='failed',
            message='Invalid from_date and to_date supplied. from_date shoud be <= to_date and in YYYY-MM-DD fromat',
            code=400
        )

    data = get_filtered_data(country_code, from_date, to_date)

    return response_with_covid_data(data=data)


@covid.route('/export_covid_data/', methods=['GET'])
@token_required
def export_covid_data(current_user):
    """
    send email with image of covid api data with from and to date filter
    :param current_user:
    :return:
    """
    user = User.get_by_id(current_user.id)
    country = request.args.get('country', user.country)
    country = countries.get(name=country)
    if not country:
        return response(
            status='failed',
            message='Invalid Country',
            code=400
        )

    country_code = country.alpha_2
    from_date = request.args.get('from_date', (CURRENT_TIME-timedelta(days=15)).strftime("%Y-%m-%d"))
    to_date = request.args.get('to_date', CURRENT_TIME.strftime("%Y-%m-%d"))

    if not is_valid_date(from_date, to_date):
        return response(
            status='failed',
            message='Invalid from_date and to_date supplied. from_date shoud be <= to_date and in YYYY-MM-DD fromat',
            code=400
        )

    data = get_filtered_data(country_code, from_date, to_date)

    timeline_data = data.get('timeline')
    date = []
    active_cases = []

    for each in timeline_data:
        date.append(each.get('date'))
        active_cases.append(each.get('active'))

    if not os.path.exists(IMAGES_DIR):
        os.mkdir(IMAGES_DIR)

    fig = px.bar(x=date, y=active_cases)
    file_path = os.path.join(IMAGES_DIR, 'fig1.png')
    fig.write_image(file_path)
    if send_email(file_path, user.email):
        return response(
                status='success',
                message='Successfully sent E-mail to {}'.format(user.email),
                code=200
            )
    else:
        return response(
                status='fail',
                message='Please configure sender_email and password in app.covid.mail_helper.sendail',
                code=400
            )
