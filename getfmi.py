from fmiopendata.wfs import download_stored_query
from datetime import datetime as dt, timezone as tz, timedelta

bbox = "18,60,32,71"


def getLightnings(stale):
    end_time = dt.now(tz.utc)
    start_time = end_time - timedelta(seconds=stale)
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp_list = []
    obs = download_stored_query(
        "fmi::observations::lightning::multipointcoverage",
        args=["starttime=" + start_time, "endtime=" + end_time, "bbox=" + bbox],
    )
    for a in range(0, len(obs.latitudes)):
        tmp_list.append(
            {
                "time": obs.times[a],
                "lon": obs.longitudes[a],
                "lat": obs.latitudes[a],
                "cloud": obs.cloud_indicator[a],
                "he": obs.ellipse_major[a] * 1000,
            }
        )
    return tmp_list
