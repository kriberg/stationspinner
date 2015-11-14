# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0037_assetworthentry_walletbalanceentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetworthentry',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='walletbalanceentry',
            name='owner',
        ),
        migrations.DeleteModel(
            name='AssetWorthEntry',
        ),
        migrations.DeleteModel(
            name='WalletBalanceEntry',
        ),
    ]
