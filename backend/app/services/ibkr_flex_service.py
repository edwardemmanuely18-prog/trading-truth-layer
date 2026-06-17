import time
import requests
import xml.etree.ElementTree as ET


class IBKRFlexService:

    def __init__(
        self,
        token: str,
        query_id: str,
    ):
        self.token = token
        self.query_id = query_id

    def request_statement(self):

        response = requests.get(
            "https://gdcdyn.interactivebrokers.com/"
            "Universal/servlet/"
            "FlexStatementService.SendRequest",
            params={
                "t": self.token,
                "q": self.query_id,
                "v": 3,
            },
        )

        root = ET.fromstring(
            response.text
        )

        reference_code = (
            root.findtext(
                ".//ReferenceCode"
            )
        )

        return reference_code

    def download_statement(
        self,
        reference_code,
    ):

        time.sleep(3)

        response = requests.get(
            "https://gdcdyn.interactivebrokers.com/"
            "Universal/servlet/"
            "FlexStatementService.GetStatement",
            params={
                "t": self.token,
                "q": reference_code,
                "v": 3,
            },
        )

        return response.text