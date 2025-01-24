from django.utils import timezone
from .models import DailyRecord
from .utils import calculate_total_emission, calculate_carbon_saved, calculate_trees_needed

def create_or_update_daily_record(user, data, serializer):
    total_emission = calculate_total_emission(data)
    carbon_saved = calculate_carbon_saved(data)
    trees_needed = calculate_trees_needed(total_emission)

    instance = serializer.save(
        user=user,
        totalCarbonEmission=round(total_emission, 3),
        carbonSaved=round(carbon_saved, 3),
        treesNeeded=trees_needed
    )
    
    return instance

def get_existing_record(user, date=None):
    if date is None:
        date = timezone.now().date()
    return DailyRecord.objects.filter(
        user=user,
        date=date
    ).first() 