from django.db import models, connections
from stationspinner.universe.models import EveName


class LatestManager(models.Manager):
    def get_latest(self, owners):
        return self.filter(owner__in=owners).order_by('owner', '-registered').distinct('owner')

    def get_latest_range(self, owners, count):
        if len(owners) == 0 or count == 0:
            return '[]'
        with connections['default'].cursor() as cursor:
            cursor.execute('''
            SELECT
                ARRAY_TO_JSON(ARRAY_AGG(history))::TEXT
            FROM (
                SELECT
                    y.owner,
                    c.name,
                    ARRAY_TO_JSON(ARRAY_AGG(JSON_BUILD_OBJECT('registered', date_trunc('day', y.registered), 'value', y.value))) as entries
                FROM (
                    SELECT
                        owner,
                        registered,
                        value
                    FROM (
                        SELECT
                            ROW_NUMBER()
                            OVER (PARTITION BY owner
                              ORDER BY registered DESC) AS r,
                            t.*
                        FROM
                            {0} t) x
                    WHERE
                        x.r <= %(count)s AND x.owner IN %(owners)s order by registered asc
                    ) y,
                    character_charactersheet c
                WHERE
                    c."characterID"=y.owner
                GROUP BY y.owner, c.name
                ) history;
            '''.format(self.model._meta.db_table),
                           {'owners': tuple(owners),
                            'count': count})
            return cursor.fetchone()[0]


class AssetWorthEntry(models.Model):
    registered = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=30, decimal_places=2)
    owner = models.IntegerField()

    objects = LatestManager()

    def name(self):
        return EveName.objects.get_name(self.owner)


class WalletBalanceEntry(models.Model):
    registered = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=30, decimal_places=2)
    owner = models.IntegerField()
    wallet_division = models.IntegerField(null=True)
    description = models.CharField(max_length=255, null=True)

    objects = LatestManager()

    def name(self):
        return EveName.objects.get_name(self.owner)
