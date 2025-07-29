from fmiopendata.wfs import download_stored_query
from datetime import datetime as dt, timezone as tz, timedelta


def getLightnings(history):
    end_time = dt.now(tz.utc)
    start_time = end_time - timedelta(seconds=history)
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp_list = []
    obs = download_stored_query(
        "fmi::observations::lightning::multipointcoverage",
        args=["starttime=" + start_time, "endtime=" + end_time],
    )
    for a in range(0, len(obs.latitudes)):
        uid = uid = (
            "lightning-"
            + obs.times[a].strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + str(obs.longitudes[a])
            + "-"
            + str(obs.latitudes[a])
        )
        tmp_list.append(
            {
                "uid": uid,
                "time": obs.times[a],
                "lon": obs.longitudes[a],
                "lat": obs.latitudes[a],
                "cloud": obs.cloud_indicator[a],
                "he": obs.ellipse_major[a] * 1000,
            }
        )
    return tmp_list
