# Generated by Django 3.1.13 on 2021-12-03 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='authority_email',
            field=models.CharField(blank=True, default='sarwar15-8988@diu.edu.bd', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='authority_no',
            field=models.CharField(blank=True, default='+8801710144505', max_length=200, null=True),
        ),
    ]
