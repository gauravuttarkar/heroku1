# Generated by Django 2.2.dev20180521165340 on 2018-05-29 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yellowant_api', '0005_auto_20180529_0635'),
    ]

    operations = [
        migrations.AddField(
            model_name='azure',
            name='AZURE_client_secret',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
