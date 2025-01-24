from .constants import *

def calculate_total_emission(data):
    return (
        data.get('waterConsumed', 0) * WATER_EMISSION_FACTOR +
        data.get('carUsageDistance', 0) * CAR_EMISSION_FACTOR +
        data.get('electricityUsage', 0) * ELECTRICITY_EMISSION_FACTOR +
        data.get('videoWatchingTime', 0) * VIDEO_EMISSION_FACTOR +
        data.get('internetUsage', 0) * INTERNET_EMISSION_FACTOR
    )

def calculate_carbon_saved(data):
    return (
        data.get('walkingSteps', 0) * WALKING_SAVING_FACTOR +
        data.get('publicTransportTime', 0) * PUBLIC_TRANSPORT_SAVING_FACTOR +
        max(0, 30 - data.get('showerTime', 0)) * SHOWER_SAVING_FACTOR
    )

def calculate_trees_needed(total_emission):
    return round(total_emission / TREE_ABSORPTION_FACTOR, 2)