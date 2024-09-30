# Generated by Django 4.2.13 on 2024-08-29 11:29

from django.db import migrations, models
import precise_bbcode.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bboard', '0006_alter_bb_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='bb',
            name='_content2_rendered',
            field=models.TextField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='bb',
            name='content2',
            field=precise_bbcode.fields.BBCodeTextField(blank=True, no_rendered_field=True, null=True, verbose_name='Описание'),
        ),
    ]
