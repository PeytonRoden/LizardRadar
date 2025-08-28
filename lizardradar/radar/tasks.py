from celery import shared_task
import requests
from django.utils.dateparse import parse_datetime
from .models import Warning
from django.utils.timezone import now
from datetime import timezone



@shared_task
def get_regional_warnings():
    events = [
        "Tornado Warning",
        "Severe Thunderstorm Warning",
        "Flash Flood Warning",
        "Special Weather Statement",
        "Special Marine Warning",
        "Coastal Flood Warning",
        "Winter Storm Warning"
    ]
    
    url = "https://api.weather.gov/alerts/active?event=" + \
      ",".join(requests.utils.quote(e) for e in events)
    
    print("url: " , url)


    headers = {
        "Accept": "application/geo+json",
        "User-Agent": "MyWeatherApp (myemail@example.com)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        geojson = response.json()
        
        # Get all existing nws_ids
        existing_ids = set(Warning.objects.values_list('nws_id', flat=True))

        # Remove expired warnings
        current_utc = now().astimezone(timezone.utc)
        expired_count, _ = Warning.objects.filter(expires__lt=current_utc).delete()
        print(f"Removed {expired_count} expired warnings")

        new_count = 0
        for feature in geojson.get("features", []):
            props = feature["properties"]
            nws_id = props["id"]

            if nws_id in existing_ids:
                continue  # skip existing warnings

            Warning.objects.create(
                nws_id=nws_id,
                event=props["event"],
                headline=props.get("headline", ""),
                area_desc=props.get("areaDesc", ""),
                effective=parse_datetime(props.get("effective")),
                expires=parse_datetime(props.get("expires")) if props.get("expires") else None,
                geojson=feature
            )
            new_count += 1

        print(f"Added {new_count} new warnings")

    except Exception as e:
        print(f"Failed to fetch warnings: {e}")
