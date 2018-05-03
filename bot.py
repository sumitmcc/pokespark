import re
from sparkbot.config import PRODUCTION
import requests

self_trigger_word = 'self'
poke_url = "http://pokeapi.co/api/v2/pokemon/"

approved_room = ["Y2lzY29zcGFyazovL3VzL1JPT00vZGExMTFhNTAtNGVmOC0xMWU4LWJjZTgtOTU0YzU2NDA1OGU2"]

class Bot:
    def __init__(self, api):
        self.api = api
        self.triggers = {
            '^.*[Pp][Oo][Kk][Ee][Mm][Oo][Nn].*$': self.get_pokemon
        }

        self.trigger_word_appears = False

    def handle(self, data):
        if data['data']['personId'] == self.api.people.me().id:
            message = self.api.messages.get(data['data']['id']).text
            if message:
                accepted_message = message.strip().startswith(self_trigger_word)
                if accepted_message:
                    message = message.replace(self_trigger_word, '', 1)
                    self.trigger_word_appears = True
            else:
                accepted_message = False
        else:
            message = self.api.messages.get(data['data']['id']).text
            accepted_message = True

        if not PRODUCTION and self.trigger_word_appears or PRODUCTION:
            if accepted_message and data['data'].get('roomType') == 'direct' or data['data']['roomId'] in approved_room:
                message = message.replace(self.api.people.me().displayName, "", 1).strip()

                for regex, func in self.triggers.items():
                    if re.search(regex, message):
                        message = message.replace('pokemon', "", 1).strip()
                        func(data, message)
                        break

    def get_pokemon(self, data, message):
        message = requests.get(poke_url+message).json()
        reply = """...
        Abilities: {ability},
        weight: {weight} lbs,
        moves: {moves}
        """.format(
                ability = ','.join([x['ability']['name'] for x in message['abilities']]),
                weight = message['weight'],
                moves = ",".join([x['move']['name'] for x in message['moves']])
        )

        self.api.messages.create(
                markdown=reply,
                roomId=data['data']['roomId']
        )

