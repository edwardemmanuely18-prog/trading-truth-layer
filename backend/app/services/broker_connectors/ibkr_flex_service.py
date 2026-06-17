import requests
import time
import xml.etree.ElementTree as ET

import logging

logger = logging.getLogger(__name__)

logger.info(
    "IBKR Flex request submitted"
)

logger.info(
    "IBKR Flex report ready"
)


def download_flex_report(
    token: str,
    query_id: str,
):

    response = requests.get(
        "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest",
        params={
            "t": token,
            "q": query_id,
            "v": "3",
        },
        timeout=30,
    )

    response.raise_for_status()

    print("\n========== FLEX SEND REQUEST ==========")
    print(response.text)
    print("=======================================\n")

    root = ET.fromstring(
        response.text
    )

    status = root.findtext(
        ".//Status"
    )

    if status != "Success":

        print(response.text)

        raise Exception(
            f"IBKR Flex request failed: {status}"
        )

    reference_code = root.findtext(
        ".//ReferenceCode"
    )

    if not reference_code:

        raise Exception(
            "Missing ReferenceCode"
        )


    for attempt in range(20):

        time.sleep(2)

        result = requests.get(
            "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement",
            params={
                "t": token,
                "q": reference_code,
                "v": "3",
            },
            timeout=30,
        )

        result.raise_for_status()

        xml_text = result.text

        print(
            f"\n========== FLEX POLL {attempt + 1} =========="
        )
        print(xml_text[:3000])
        print("===========================================\n")

        if "<ErrorCode>" in xml_text:

            raise Exception(
                f"IBKR Flex error: {xml_text}"
            )

        if (
            "<FlexQueryResponse"
            in xml_text
            or "<FlexStatements"
            in xml_text
        ):
            return xml_text

    raise Exception(
        "Timed out waiting for Flex report"
    )