# Generated by Django 4.2.16 on 2024-10-04 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword_text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_period', models.CharField(max_length=60)),
                ('result_count', models.IntegerField()),
                ('search_date', models.DateTimeField(auto_now_add=True)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.keyword')),
            ],
        ),
    ]
