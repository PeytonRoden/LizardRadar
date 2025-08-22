from django.shortcuts import render
from django.http import JsonResponse
import os

def radar_map_view(request):
    return render(request, 'radar/radar.html')




from django.http import JsonResponse
from django.conf import settings
import s3fs, pyart, numpy as np, os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import re
from datetime import datetime, timedelta
import s3fs


def get_latest_nexrad_file(station):
    fs = s3fs.S3FileSystem(anon=True)
    bucket = 'noaa-nexrad-level2'
    timestamp_pattern = re.compile(rf"{station}(\d{{8}})_(\d{{6}})_V06$")  # Match _V06 files only

    for offset in range(2):
        date = datetime.utcnow() - timedelta(days=offset)
        prefix = date.strftime(f"%Y/%m/%d/{station}/")
        try:
            files = fs.ls(f"{bucket}/{prefix}")
            if files:
                def extract_datetime(f):
                    filename = os.path.basename(f)
                    # Only process files ending in _V06 and not _MDM
                    if filename.endswith('_V06') and not filename.endswith('_MDM'):
                        match = timestamp_pattern.search(filename)
                        if match:
                            date_str, time_str = match.groups()
                            return datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
                    return datetime.min
                # Sort files by datetime, latest first
                filtered_files = [f for f in files if os.path.basename(f).endswith('_V06') and not os.path.basename(f).endswith('_MDM')]
                if not filtered_files:
                    continue  # No matching _V06 files, try previous day
                filtered_files.sort(key=extract_datetime, reverse=True)
                return fs, filtered_files[0]  # Return latest _V06 file
        except FileNotFoundError:
            continue
    raise Exception("No radar data found with _V06 suffix")


from django.http import JsonResponse

def latest_radar_scan(request, station):
    try:
        url = get_latest_nexrad_file(station)
        # print("url: ", url[1])
        url = 'https://noaa-nexrad-level2.s3.amazonaws.com' + url[1][18:]
        # print("url: ", url)
        return JsonResponse({"url": url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=404)


import glob
def render_radar_image(request, icao):
    station = icao.upper()
    try:

        # Prepare directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'radar')
        os.makedirs(output_dir, exist_ok=True)

        # 🧹 Delete all existing PNGs
        for old_file in glob.glob(os.path.join(output_dir, '*.png')):
            try:
                os.remove(old_file)
            except Exception as e:
                print(f"Couldn't delete {old_file}: {e}")

        fs, radar_path = get_latest_nexrad_file(station)
        with fs.open(radar_path, 'rb') as f:
            radar = pyart.io.read_nexrad_archive(f)

        sweep = 0
        lats, lons, _ = radar.get_gate_lat_lon_alt(sweep)
        lat_min, lat_max = float(np.nanmin(lats)), float(np.nanmax(lats))
        lon_min, lon_max = float(np.nanmin(lons)), float(np.nanmax(lons))

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        plt.axis('off')
        display = pyart.graph.RadarDisplay(radar)
        
        display.plot('reflectivity', sweep, ax=ax, title='', colorbar_flag=False, cmap="NWSRef")
        #display.plot('velocity', sweep, ax=ax, title='', colorbar_flag=False, cmap="NWSVel")

        output_dir = os.path.join(settings.MEDIA_ROOT, 'radar')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{station}.png")
        plt.savefig(output_path, dpi=1200, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()

        return JsonResponse({
            "url": f"/media/radar/{station}.png",
            "bounds": [[lat_min, lon_min], [lat_max, lon_max]]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
