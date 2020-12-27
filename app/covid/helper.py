from flask import make_response, jsonify, url_for
from app import app


def response(status, message, code):
    """
    Helper method to make a http response
    :param status: Status message
    :param message: Response message
    :param code: Response status code
    :return: Http Response
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), code

def response_with_covid_data(data):
    """
    Make a http response for BucketList get requests.
    :param data: Covid API filtered response
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': 'success',
        'covid_data': data
    })), 200
