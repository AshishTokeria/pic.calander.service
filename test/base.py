import requests
import datetime
from hstest import correct, WrongAnswer


def test_correct_request(self):
    tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))

    response = post(
        self.get_url('/event'),
        data={
            "event": "Video conference",
            "date": tomorrow
        }
    )

    check_status_code(
        response,
        200,
        "After making a correct POST request for '/event' URL the server should return HTTP status code 200"
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'message',
        'The event has been added!'
    )

    check_key_value_in_dict(
        data, 'event',
        'Video conference'
    )

    check_key_value_in_dict(
        data, 'time',
        tomorrow
    )

    return correct()


def test_bad_request(self):
    response = post(
        self.get_url('/event'),
        data={
            "date": str(datetime.datetime.now().date())
        }
    )

    data = get_json_from_response(response)

    check_key_object_value_in_dict(
        data, 'message'
    )

    check_key_value_in_dict(
        data['message'], 'event',
        'The event name is required!'
    )

    response = post(
        self.get_url('/event/1'),
        data={
            "description": "Video conference",
        }
    )

    data = get_json_from_response(response)

    check_key_object_value_in_dict(
        data, 'description'
    )

    check_key_value_in_dict(
        data['description'], 'time',
        'The event date with the correct format is required! The correct format is YYYY-MM-DD!'
    )

    response = post(
        self.get_url('/event'),
        data={
            "event": "Video conference",
            "date": '15-11-2020'
        }
    )

    data = get_json_from_response(response)

    check_key_object_value_in_dict(
        data, 'description'
    )

    check_key_value_in_dict(
        data['description'], 'time',
        'The event date with the correct format is required! The correct format is YYYY-MM-DD!'
    )

    return correct()


def test_get_events(self):
    post(
        self.get_url('/event'),
        data={
            "description": "Today's first event",
            "time": str(datetime.date.today())
        }
    )

    post(
        self.get_url('/event'),
        data={
            "description": "Today's second event",
            "time": str(datetime.date.today())
        }
    )

    post(
        self.get_url('/event'),
        data={
            "description": "Tomorrow event",
            "time": str(datetime.date.today() + datetime.timedelta(days=1))
        }
    )

    response = get(
        self.get_url('/event')
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) < 3:
        raise WrongAnswer("The response list should contain at least 3 events!")

    find_event(data, str(datetime.date.today()), "Today's first event")
    find_event(data, str(datetime.date.today()), "Today's second event")

    return correct()