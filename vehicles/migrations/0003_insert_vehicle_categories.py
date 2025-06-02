from django.db import migrations

def insert_vehicle_categories(apps, schema_editor):
    VehicleCategory = apps.get_model('vehicles', 'VehicleCategory')
    VehicleCategory.objects.get_or_create(name='metropolitan', defaults={'description': 'Vehículo de categoría metropolitana'})
    VehicleCategory.objects.get_or_create(name='campus', defaults={'description': 'Vehículo de categoría campus'})
    VehicleCategory.objects.get_or_create(name='intermunicipal', defaults={'description': 'Vehículo de categoría intermunicipal'})

class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_vehicle_categories),
    ]