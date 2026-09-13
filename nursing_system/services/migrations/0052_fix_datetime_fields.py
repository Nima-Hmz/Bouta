# Generated manually to fix datetime fields with redundant defaults

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('services', '0051_wallettransaction_j_time'),
    ]

    operations = [
        # Fix the NurseReport and UserReport created_at fields from migration 0043
        migrations.AlterField(
            model_name='nursereport',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='userreport',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        
        # Fix the ServiceRequest created_at field from migration 0011
        migrations.AlterField(
            model_name='servicerequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ] 