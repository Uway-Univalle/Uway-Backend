
from django.db import migrations

def insert_vehicle_types(apps, schema_editor):
    VehicleType = apps.get_model('vehicles', 'VehicleType')
    VehicleType.objects.get_or_create(name='van', defaults={'description': 'Vehículo tipo camioneta'})
    VehicleType.objects.get_or_create(name='bike', defaults={'description': 'Vehículo tipo motocicleta'})
    VehicleType.objects.get_or_create(name='bus', defaults={'description': 'Vehículo tipo bus'})
    VehicleType.objects.get_or_create(name='car', defaults={'description': 'Vehículo tipo automóvil'})
    VehicleType.objects.get_or_create(name='skateboard', defaults={'description': 'Vehículo tipo patineta'})
    VehicleType.objects.get_or_create(name='tricycle', defaults={'description': 'Vehículo tipo triciclo'})


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_vehicle_types),
    ]