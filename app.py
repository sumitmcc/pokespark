from flask import Flask, request
from ciscosparkapi import CiscoSparkAPI
from pokespark.bot import Bot
from pokespark.config import SUMIT_KEY

app = Flask(__name__)
api = CiscoSparkAPI(SUMIT_KEY)


@app.route('/', methods=['POST'])
def home():

    if hasattr(request, 'json') and request.get_json('data'):
        bot = Bot(api)
        bot.handle(request.get_json('data'))
        return ''


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=9988, debug=True)