
# import random
import logging
import threading
import requests

import pandas as pd

import tornado.websocket
import tornado.web
import tornado.ioloop

from perspective import Table, PerspectiveManager, PerspectiveTornadoHandler

from dataValuation import collectApiData
from dataProcessing import welcome_survey,e_survey,match_1,match_2, mall_survey, survey
# from dataprocessing1 import mall_survey


### data token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFscyI6InByaXZhdGUtZGF0YS1wbGF0Zm9ybS1rZXkgZm9yIGFscGhhIiwiY3JlYXRlZEF0IjoiMjAyMS0wNi0yOFQxODoxNjoyOC4yNThaIiwiaWF0IjoxNjI0OTA0MTg4fQ.ITcG3EO90Uzc9JZYjE6g5mbmh4kkHBDO6QEumQ8ZruQ"


### session that can be reused for the answer or survey api type
## this line will need to be updated to take in surveys and answers
s = requests.Session()

# set survey id to change surveys
survey_id = 78

apitype = "answers"

df = collectApiData(session=s, apitype=apitype,token=token, survey_id = survey_id )
# df1 = pd.DataFrame()
# df2 = pd.DataFrame()

## global variable which will increase offset after every function call
offset = 10000

tracker = 1

## Multithread function to update df 
# def update_df():
#     global df
#     global offset
#     global tracker
#     global df1
#     global df2
#     if tracker%2==0:
#         df1= collectApiData(session=s, apitype="answers",token=token,offset=offset )
#         offset = offset+10000
#         tracker = tracker + 1
#     else:
#         df2= collectApiData(session=s, apitype="answers",token=token,offset=offset )
#         offset = offset+10000
#         tracker = tracker + 1
    # pass

limit = 0

def data_source():
    global limit
    global df
    if apitype =="answers":
        df = collectApiData(session=s, apitype=apitype,token=token, survey_id = survey_id)
        if survey_id == 1:
            data = welcome_survey(limit=limit,df=df)
        elif survey_id == 78:
            data = mall_survey(limit=limit,df=df)
        elif survey_id == 79:
            data = e_survey(limit= limit,df=df)
        elif survey_id == 94:
            data = match_2(limit= limit,df=df)
        elif survey_id == 95:
            data = match_1(limit= limit,df=df)
    else:
        df = collectApiData(session=s, apitype=apitype,token=token)
        data = survey(df=df)

    return data


def perspective_thread(manager):
    """Perspective application thread starts its own tornado IOLoop, and
    adds the table with the name "data_source_one", which will be used
    in the front-end."""
    psp_loop = tornado.ioloop.IOLoop()
    manager.set_loop_callback(psp_loop.add_callback)
    if apitype == "answers":
        if survey_id == 1:
            table = Table(
                {
                    "0": str,
                    "1": str,
                    "2": str,
                    "3": str,
                    "4": str,
                    "5": str,
                    "6": str,
                },
                limit = len(df)
            )
        elif survey_id == 78:
            table= Table(
                {
                    "0": str,
                    "1": str,
                    "2": str,
                    "3": str,
                    "4": str,
                    "5": str,
                    "6": str,
                    "7": str,
                    "8": str,
                    "9": str,
                },
                limit = len(df)
            )
        elif survey_id==79:
            table= Table(
                {
                    "0": str,
                    "1": str,
                    "2": str,
                    "3": str,
                    "4": str,
                    "5": str,
                    "6": str,
                    "7": str,
                },
                limit = len(df)
            )
        elif survey_id==94:
            table= Table(
                {
                    "0": str,
                    "1": str,
                },
                limit = len(df)
            )
        elif survey_id==95:
            table= Table(
                {
                    "0": str,
                    "1": str,
                },
                limit = len(df)
            )
    else:
        table= Table(
            {
                "id": int,
                "title": str,
                "questionCount": int,
                "totalTfb": int,
                # "participantLimit": int,
                "answerCount": int,
            },
            limit = len(df)
        )

    # Track the table with the name "data_source_one", which will be used in
    # the front-end to access the Table.
    manager.host_table("data_source_one", table)

    # update with new data every 50ms
    def updater():
        global limit
        if apitype == "answers":
            if limit + 100 < len(df):
                table.update(data_source())
                limit = limit+100
            else:
                limit = 0
                # callback.stop()
                table.replace(data_source())
        else:
            table.replace(data_source())
            

    callback = tornado.ioloop.PeriodicCallback(callback=updater, callback_time=50)
    callback.start()
    
    psp_loop.start()


def make_app():
    manager = PerspectiveManager()

    thread = threading.Thread(target=perspective_thread, args=(manager,))
    thread.daemon = True
    thread.start()
    # data_thread = threading.Thread(target=update_df)
    # data_thread.start()

    return tornado.web.Application(
        [
            # create a websocket endpoint that the client Javascript can access
            (
                r"/websocket",
                PerspectiveTornadoHandler,
                {"manager": manager, "check_origin": True},
            ),
            (
                r"/node_modules/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "./node_modules/@finos/"},
            ),
            (
                r"/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "./", "default_filename": "index.html"},
            ),
        ]
    )


def main():
    app = make_app()
    app.listen(8080)
    logging.critical("Listening on http://localhost:8080")
    loop = tornado.ioloop.IOLoop.current()
    loop.start()

if __name__ == "__main__":
    main()