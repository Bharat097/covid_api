from flask import Blueprint, request, abort
from app.auth.helper import token_required
from app.covid.helper import response, response_with_covid_data
from app.models import User
from pycountry import countries
import requests
import json
from datetime import datetime, timedelta

# Initialize blueprint
covid = Blueprint('covid', __name__)

URL = "http://corona-api.com/countries/{}"
CURRENT_TIME = datetime.utcnow()


@covid.route('/covid-data/', methods=['GET'])
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
    from_date = request.args.get('from', (CURRENT_TIME-timedelta(days=15)).strftime("%Y-%m-%d"))
    to_date = request.args.get('to', CURRENT_TIME.strftime("%Y-%m-%d"))
    try:
        datetime.strptime(from_date, "%Y-%m-%d")
        datetime.strptime(to_date, "%Y-%m-%d")
    except Exception as e:
        return response(
            status='failed',
            message=str(e),
            code=400
        )
    if from_date > to_date:
        return response(
            status='failed',
            message='from_date shoud be <= to_date',
            code=400
        )
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

    return response_with_covid_data(data=data)
