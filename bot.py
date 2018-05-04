import re

import bs4 as bs4

from pokespark.config import PRODUCTION
import requests

self_trigger_word = 'self'
poke_url = "http://pokeapi.co/api/v2/pokemon/"

approved_room = ["Y2lzY29zcGFyazovL3VzL1JPT00vZGExMTFhNTAtNGVmOC0xMWU4LWJjZTgtOTU0YzU2NDA1OGU2"]

class Bot:
    def __init__(self, api):
        self.api = api
        self.triggers = {
            '^.*[Pp][Oo][Kk][Ee][Mm][Oo][Nn]\s.*$': self.get_pokemon
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

        if (not PRODUCTION and self.trigger_word_appears) or PRODUCTION:
            if accepted_message and data['data'].get('roomType') == 'direct' or data['data']['roomId'] in approved_room:
                message = message.replace(self.api.people.me().displayName, "", 1).strip()

                for regex, func in self.triggers.items():
                    if re.search(regex, message):
                        message = message.lower().replace('pokemon', "", 1).strip()
                        func(data, message)
                        break

    def get_pokemon(self, data, message):
        message = requests.get(poke_url+message).json()
        if message.get('detail') and message['detail'] == "Not found.":
            self.api.messages.create(
                    markdown="Missed something? This might help you {}"
                             "".format("https://pokemondb.net/pokedex/national"),
                    roomId=data['data']['roomId']
            )
            return

        evolution = self.get_evolution_chain(message['forms'][0]['name'])
        reply = """...
        Name: {name}
        Abilities: {ability},
        weight: {weight} lbs,
        moves: {moves},
        evolution chain: {evo}
        """.format(
                name = message['forms'][0]['name'],
                ability = ', '.join([x['ability']['name'] for x in message['abilities']]),
                weight = message['weight'],
                moves = ", ".join([x['move']['name'] for x in message['moves']]),
                evo = evolution
        )

        self.api.messages.create(
                markdown=reply,
                roomId=data['data']['roomId']
        )
        self.api.messages.create(
                text="Need more info? {website}".format(
                        website="https://pokemondb.net/pokedex/" + message['forms'][0]['name']),
                roomId=data['data']['roomId']
        )

    def get_evolution_chain(self, name):
        evolution = requests.get("https://pokemondb.net/pokedex/"+str(name))
        soup = bs4.BeautifulSoup(evolution.content, 'html.parser')
        lass = soup.select('div span a img')
        return ", ".join([x.get('alt') for x in lass]) if lass else "None"