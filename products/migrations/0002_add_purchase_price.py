"""
This migration is intentionally a NO-OP.

The field `purchase_price` is already created in 0001_initial, so adding it
again causes "column ... already exists" on fresh databases. We keep this
migration in history but without any database operations so both new and old
databases can migrate consistently.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = []