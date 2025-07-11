import os
import uuid
import asyncio
import xml.etree.ElementTree as ET
from configparser import ConfigParser
import pytak
import getfmi as fmi

COT_URL = os.getenv("COT_URL")
TAK_PROTO = os.getenv("TAK_PROTO", "0")
PYTAK_TLS_CLIENT_CERT = os.getenv("PYTAK_TLS_CLIENT_CERT")
PYTAK_TLS_CLIENT_KEY = os.getenv("PYTAK_TLS_CLIENT_KEY")
PYTAK_TLS_DONT_VERIFY = os.getenv("PYTAK_TLS_DONT_VERIFY", "1")
HISTORY = int(os.getenv("HISTORY", "120"))


def weather2cot(sensor):
    uid = "lightning-" + str(uuid.uuid4())
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "b-w-A-S-T-L")
    root.set("uid", uid)
    root.set("how", "m-c")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(30))

    pt_attr = {
        "lat": f'{sensor["lat"]}',
        "lon": f'{sensor["lon"]}',
        "hae": "5000",
        "ce": f'{sensor["he"]}',
        "le": "10",
    }

    ET.SubElement(root, "point", attrib=pt_attr)

    callsign = f"Lightning strike"
    contact = ET.Element("contact")
    contact.set("callsign", callsign)

    remarks = ET.Element("remarks")
    remarks.text = f"Säähavainnot: Ilmatieteenlaitos avoin data, CC-BY 4.0\nWeather observations: Finnish Meteorological Institute open data, CC-BY 4.0"

    iconsetpath = "ad78aafb-83a6-4c07-b2b9-a897a8b6a38f/Shapes/thunderstorm.png"
    usericon = ET.Element("usericon")
    usericon.set("iconsetpath", iconsetpath)

    detail = ET.Element("detail")
    detail.append(contact)
    detail.append(usericon)
    detail.append(remarks)

    root.append(detail)

    return ET.tostring(root)


class sendWeather(pytak.QueueWorker):

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, then puts on queue."""
        event = data
        await self.put_queue(event)

    async def run(self):
        """Run the loop for processing or generating pre-CoT data."""
        while 1:
            data = bytes()
            sensors = fmi.getLightnings(COT_STALE)
            for sensor in sensors:
                data += weather2cot(sensor)
                self._logger.info("Sent:\n%s\n", data.decode())
            await self.handle_data(data)
            await asyncio.sleep(30)


async def main():
    config = ConfigParser()
    config["mycottool"] = {
        "COT_URL": COT_URL,
        "TAK_PROTO": TAK_PROTO,
        "PYTAK_TLS_CLIENT_CERT": PYTAK_TLS_CLIENT_CERT,
        "PYTAK_TLS_CLIENT_KEY": PYTAK_TLS_CLIENT_KEY,
        "PYTAK_TLS_DONT_VERIFY": PYTAK_TLS_DONT_VERIFY,
    }
    config = config["mycottool"]

    clitool = pytak.CLITool(config)
    await clitool.setup()

    clitool.add_tasks(
        set(
            [
                sendWeather(clitool.tx_queue, config),
            ]
        )
    )

    await clitool.run()


if __name__ == "__main__":
    asyncio.run(main())
