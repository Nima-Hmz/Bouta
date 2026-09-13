from nurse_users.models import NurseLocation
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.utils.timezone import now

def find_nearby_nurses(location_form, radius, selected_skill_instance, nurse_limit=10):
    # Get user's location from form input
    user_location = location_form.cleaned_data["location"]  # e.g., 'SRID=4326;POINT(51.3890 35.6892)'
    search_radius_degrees = radius

    # Compute bounding box coordinates around user_location
    min_x = user_location.x - search_radius_degrees
    min_y = user_location.y - search_radius_degrees
    max_x = user_location.x + search_radius_degrees
    max_y = user_location.y + search_radius_degrees

    # Create a bounding box polygon (WKT) and convert it to a GEOSGeometry object
    bbox_wkt = (
        f"POLYGON(({min_x} {min_y}, {min_x} {max_y}, "
        f"{max_x} {max_y}, {max_x} {min_y}, {min_x} {min_y}))"
    )
    bbox = GEOSGeometry(bbox_wkt, srid=4326)

    # Build the queryset using the bounding box and dwithin filters.
    locations = NurseLocation.objects.filter(
        location__within=bbox,
        location__dwithin=(user_location, search_radius_degrees),
        nurse_user_additional_info__nurse_skills__skill=selected_skill_instance,
        nurse_user_additional_info__nurse__subscription__status=True,
        nurse_user_additional_info__nurse__subscription__end_date__gt=now(),
        nurse_user_additional_info__nurse__is_active=True  # Ensure nurse is active
    ).annotate(distance=Distance("location", user_location)) \
    .order_by("distance") \
    .select_related("nurse_user_additional_info__nurse")[:nurse_limit]  # Eager load related NurseUserAdditionalInfo

    return locations

