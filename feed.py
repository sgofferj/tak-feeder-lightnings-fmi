import os
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime as dt, timezone as tz, timedelta
from configparser import ConfigParser
import pytak
import getfmi as fmi

COT_URL = os.getenv("COT_URL")
TAK_PROTO = os.getenv("TAK_PROTO", "0")
PYTAK_TLS_CLIENT_CERT = os.getenv("PYTAK_TLS_CLIENT_CERT")
PYTAK_TLS_CLIENT_KEY = os.getenv("PYTAK_TLS_CLIENT_KEY")
PYTAK_TLS_DONT_VERIFY = os.getenv("PYTAK_TLS_DONT_VERIFY", "1")
HISTORY = int(os.getenv("HISTORY", "300"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))


def weather2cot(sensor):
    timenow = dt.now(tz.utc)
    timestart = sensor["time"].replace(tzinfo=tz.utc)
    staleseconds = UPDATE_INTERVAL * 2

    agedelta = timenow - timestart
    ageseconds = agedelta.days * 24 * 3600 + agedelta.seconds

    argb = "-1"
    if (ageseconds) >= 300:
        argb = "-256"
    if (ageseconds) >= 900:
        argb = "-35072"
    if (ageseconds) >= 1800:
        argb = "-65535"
    if (ageseconds) >= 2700:
        argb = "-7864320"

    uid = sensor["uid"]
    root = ET.Element("event")
    root.set("version", "2.0")
    # That should be "b-w-A-S-T-L" but ATAK seems to only displau the spot marker if the type is "b-m-p-s-m"
    root.set("type", "b-m-p-s-m")
    root.set("uid", uid)
    root.set("how", "m-c")
    root.set("time", pytak.cot_time())
    root.set("start", timestart.strftime("%Y-%m-%dT%H:%M:%S.000000Z"))
    root.set("stale", pytak.cot_time(staleseconds))

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
    remarks.text = "Strike time: " + timestart.strftime("%Y-%m-%dT%H:%M:%SZ")
    remarks.text += "\nSäähavainnot: Ilmatieteenlaitos avoin data, CC-BY 4.0"
    remarks.text += (
        "\nWeather observations: Finnish Meteorological Institute open data, CC-BY 4.0"
    )

    iconsetpath = f"COT_MAPPING_SPOTMAP/b-m-p-s-m/{argb}"
    usericon = ET.Element("usericon")
    usericon.set("iconsetpath", iconsetpath)

    color = ET.Element("color")
    color.set("argb", argb)

    detail = ET.Element("detail")
    detail.append(contact)
    detail.append(usericon)
    detail.append(remarks)
    detail.append(color)

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
            sensors = fmi.getLightnings(HISTORY)
            for sensor in sensors:
                data += weather2cot(sensor)
                # self._logger.info("Sent:\n%s\n", data.decode())
            await self.handle_data(data)
            await asyncio.sleep(UPDATE_INTERVAL)


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
