"""Websupport DNS Authenticator."""

import logging
import hmac
import hashlib
import time
import requests
import json
import collections.abc

from datetime import datetime, timezone

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """Websupport DNS Authenticator

    This Authenticator uses a Websupport DNS server to fulfill a dns-01 challenge.
    """

    description = "Obtain certificates using an Websupport DNS server using Rest API v2"

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials: CredentialsConfiguration = None

    @classmethod
    def add_parser_arguments(
        cls, add, default_propagation_seconds: int = 60
    ):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="Websupport API credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return "This plugin configures a DNS TXT record to respond to a dns-01 challenge using the Websupport REST API v2."

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Websupport API credentials INI file",
            {
                "api_key": "API key (Identifier)",
                "secret": "API secret (Secret key)",
                "service": "ID of targeted service",
            },
        )

    def _perform(self, domain, validation_name, validation):
        self._get_websupport_client().add_txt_record(validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_websupport_client().del_txt_record(validation_name)

    def _get_websupport_client(self) -> "_WebsupportRestApiV2Client":
        if not self.credentials:  # pragma: no cover
            raise errors.Error("Plugin has not been prepared.")
        return _WebsupportRestApiV2Client(
            self.credentials.conf("api_key"),
            self.credentials.conf("secret"),
            self.credentials.conf("service"),
        )


class _WebsupportRestApiV2Client:
    api = "https://rest.websupport.sk"

    def __init__(self, api_key, secret, service):
        self.api_key = api_key
        self.secret = secret
        self.service = service

    def get_signature(self, method, path, timestamp):
        canonicalRequest = "%s %s %s" % (method, path, timestamp)
        signature = hmac.new(
            bytes(self.secret, "UTF-8"), bytes(canonicalRequest, "UTF-8"), hashlib.sha1
        ).hexdigest()
        return signature

    def get_headers(self, timestamp):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Date": datetime.fromtimestamp(timestamp, timezone.utc).isoformat(),
        }
        return headers

    def get_validation_name_without_base_domain(self, validation_name):
        splitted = validation_name.split(".")
        if len(splitted) >= 2:
            splitted.pop()
            splitted.pop()
        subdomain = ".".join(splitted)
        return subdomain

    def add_txt_record(self, validation_name, validation):
        _validation_name = self.get_validation_name_without_base_domain(validation_name)
        method = "POST"
        path = "/v2/service/%s/dns/record" % (self.service)
        data = {
            "type": "TXT",
            "name": _validation_name,
            "content": validation,
            "ttl": 30,
            "priority": 0,
            "port": 0,
            "weight": 0,
        }
        timestamp = int(time.time())
        headers = self.get_headers(timestamp)
        try:
            requests.post(
                "%s%s" % (self.api, path),
                json=data,
                headers=headers,
                auth=(self.api_key, self.get_signature(method, path, timestamp)),
            ).content
            print(
                'Record with name "%s" and _validation_name "%s" created'
                % (_validation_name, validation)
            )
        except:
            print("An error occured while creating record")

    def _find_txt_record(self, validation_name):
        _validation_name = self.get_validation_name_without_base_domain(validation_name)
        method = "GET"
        path = "/v2/service/%s/dns/record" % (self.service)
        timestamp = int(time.time())
        query = "?filters%5Bname%5D={}&filters%5Btype%5D%5B0%5D=TXT".format(_validation_name)
        headers = self.get_headers(timestamp)

        record_id = None
        try:
            response = requests.get(
                "%s%s%s" % (self.api, path, query),
                headers=headers,
                auth=(self.api_key, self.get_signature(method, path, timestamp)),
            ).content
            jsonReponse = json.loads(response)
            if "data" in jsonReponse:
                if (
                    isinstance(jsonReponse["data"], collections.abc.Sequence)
                    and not isinstance(jsonReponse["data"], (str))
                    and len(jsonReponse["data"])
                    == 1  # only if exactly one record found
                ):
                    if "id" in jsonReponse["data"][0]:
                        record_id = jsonReponse["data"][0]["id"]
                        print("Record with id %s found" % (record_id))
        except:
            print("An error occured while searching for record_id")

        return record_id

    def _del_txt_record(self, record_id):
        method = "DELETE"
        path = "/v2/service/%s/dns/record/%s" % (self.service, record_id)
        timestamp = int(time.time())
        headers = self.get_headers(timestamp)

        try:
            requests.delete(
                "%s%s" % (self.api, path),
                headers=headers,
                auth=(self.api_key, self.get_signature(method, path, timestamp)),
            )
            print("Record with id %s deleted" % (record_id))
        except:
            print("An error occured while removing record")

    def del_txt_record(self, validation_name):
        record_id = self._find_txt_record(validation_name)
        if record_id != None:
            self._del_txt_record(record_id)
        else:
            print("No record found!")
