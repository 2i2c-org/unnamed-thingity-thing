# Generated by Django 5.0.7 on 2024-09-23 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0014_alter_contentfile_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="mimetype",
            field=models.CharField(
                default="text/markdown",
                help_text="Mimetype used to render this page",
                max_length=32,
            ),
        ),
    ]
