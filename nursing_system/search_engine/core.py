from .filter import find_nearby_nurses

def search_core(location_form, selected_skill_instance):
    # the core of the search engine
    radius_10km = 10 / 111.0  # ~0.09 degrees (~10 km)
    radius_50km = 50 / 111.0  # ~0.09 degrees (~10 km)
    nurse_limit = 10

    result = find_nearby_nurses(location_form=location_form, radius=radius_10km, \
                                      selected_skill_instance=selected_skill_instance, \
                                        nurse_limit=nurse_limit)
    if not result:
        # set the radius to 50 km
      result = find_nearby_nurses(location_form=location_form, radius=radius_50km, \
                                      selected_skill_instance=selected_skill_instance, \
                                        nurse_limit=nurse_limit)

    return result



    




    



