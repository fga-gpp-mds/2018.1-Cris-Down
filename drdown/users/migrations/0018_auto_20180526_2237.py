# Generated by Django 2.0.3 on 2018-05-26 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_patient_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, help_text='Photo of user.', max_length=500, null=True, upload_to='media/', verbose_name='Photo'),
        ),
    ]
