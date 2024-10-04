# pic.calander.service

This is a simple project for implementation of calander service.

to build project: docker-compose build

to run project in docker container: docker-compose up

the above command should start the project

The following endpoints are exposed


a) add events one at a time
http://<. . .>:5000/add_event

{
    "id": 1,
    "time": "2021-09-23T14:00:00",
    "description": "Meeting with Bob-1"
}

b) get all events
http://<. . .>:5000/events

c) get specific event in datetime_format
http://127.0.0.1:5000/events/1?datetime_format='%Y-%m-%d'

d) get events as per the date range
http://<. . .>:5000/events?datetime_format='%Y-%m-%d'&from_time=2022-09-24T00:00:00&to_time=2025-09-21T23:59:59
