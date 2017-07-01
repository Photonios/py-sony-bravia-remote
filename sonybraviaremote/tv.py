from typing import Callable
import json

import requests

from .tvconfig import TVConfig


class TV:
    """Represents a Sony Bravia TV that can
    be controlled remotely."""

    def __init__(self, auth_key: str, config: TVConfig):
        """Initializes a new instance of
        :see:TV with the specified configuration."""

        self.auth_key = auth_key
        self.config = config
        self._irc_codes = self.irc_codes()

    def irc_codes(self) -> dict:
        """Gets a complete list of the supported
        IRC codes from this TV.

        Returns:
            A dictionary of all available
            IRC codes. Where the key is the
            name of the IRC code and the value
            the actual IRC code.
        """

        url = 'http://%s/sony/system' % self.config.host
        payload = {
            'method': 'getRemoteControllerInfo',
            'params':[],
            'id': 10,
            'version':'1.0'
        }

        response = requests.post(
            url,
            data=json.dumps(payload),
            headers={
                'SOAPAction': 'urn:schemas-sony-com:service:IRCC:1#X_SendIRCC'
            }
        )

        if response.status_code != 200:
            raise RuntimeError(response.body)

        original_data = response.json()

        irc_codes = dict()
        for entry in original_data['result'][1]:
            irc_codes[entry['name']] = entry['value']

        return irc_codes

    def is_on(self):
        """Gets whether the TV is turned on or not."""

        url = 'http://%s/sony/system' % self.config.host
        payload = {
            'method': 'getPowerStatus',
            'params':[],
            'id': 10,
            'version':'1.0'
        }

        response = requests.post(url, data=json.dumps(payload))

        if response.status_code != 200:
            raise RuntimeError(response.body)

        data = response.json()
        return data['result'][0]['status'] == 'active'

    def mute(self):
        self._send_irc_code('Mute')

    def volume_up(self, amount=5):
        for _ in range(0, amount):
            self._send_irc_code('VolumeUp')

    def volume_down(self, amount=5):
        for _ in range(0, amount):
            self._send_irc_code('VolumeDown')

    def pause(self):
        self._send_irc_code('Pause')

    def play(self):
        self._send_irc_code('Play')

    def power_off(self):
        self._send_irc_code('PowerOff')

    def wake_up(self):
        self._send_irc_code('WakeUp')

    def home(self):
        self._send_irc_code('Home')

    def netflix(self):
        self._send_irc_code('Netflix')

    def enter(self):
        self._send_irc_code('Enter')

    def confirm(self):
        self._send_irc_code('Confirm')

    @classmethod
    def connect(cls, config: TVConfig, callback: Callable[[], str]) -> 'TV':
        """Attempts to connect to the specified TV.

        Arguments:
            config:
                The configuration describing
                the TV to connect to.

            calback:
                The method to call to resolve
                the authentication challenge.

        Returns:
            A new instance of :see:TV upon a succesful
            connection.
        """

        auth_key = cls._attempt_auth(config)

        if auth_key:
            return TV(auth_key, config)

        pincode = callback()
        auth_key = cls._attempt_auth(config, pincode)

        if auth_key:
            return TV(auth_key, config)

        raise RuntimeError('Could not pair with the TV')

    @staticmethod
    def _attempt_auth(config: TVConfig, pincode=None):
        """Attempts authentication at the TV.

        Arguments:
            config:
                The TV at which to attempt the authentication.

            pincode:
                The pincode displayed on the screen to pair
                with. This is only needed on very first
                authentication.
        """

        url = 'http://%s/sony/accessControl' % config.host
        client_id = '%s:1' % config.device_name
        payload = {
            'id': 13,
            'method': 'actRegister',
            'version': '1.0',
            'params': [
                {
                    'clientid': client_id,
                    'nickname': config.device_name
                },
                [{
                    'clientid': client_id,
                    'value': 'yes',
                    'nickname': config.device_name,
                    'function': 'WOL'
                }]
            ]
        }

        params = dict(data=json.dumps(payload))
        if pincode:
            params['auth'] = ('', pincode)

        response = requests.post(url, **params)
        if response.status_code != 200:
            return False

        return response.headers['Set-Cookie']

    def _send_irc_code(self, code):
        """Sends an IRC code to the TV.

        Each action that can be performed has a IRC code
        associated with it.

        Arguments:
            code:
                The name of the IRC code to send.
        """

        url = 'http://%s/sony/IRCC' % self.config.host
        payload = ('<?xml version="1.0"?>'
                   '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
                   '<s:Body>'
                   '<u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">'
                   '<IRCCCode>%s</IRCCCode>'
                   '</u:X_SendIRCC>'
                   '</s:Body>'
                   '</s:Envelope>') % self._irc_codes[code]

        response = requests.post(
            url,
            data=payload,
            headers={
                'Cookie': self.auth_key,
                'SOAPAction': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"'
            }
        )

        if response.status_code != 200:
            raise RuntimeError(response)
