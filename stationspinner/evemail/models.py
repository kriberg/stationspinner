from django.db import models
from stationspinner.character.models import MailMessage
from django_pgjson.fields import JsonBField
from stationspinner.accounting.models import Capsuler
from stationspinner.libs import fields as custom
from stationspinner.settings import EVEMAIL_SEARCH_LANGUAGES
from django.db.models.signals import post_save
from django.dispatch import receiver
from celery.utils.log import get_task_logger
from django.db import connections

log = get_task_logger(__name__)

def update_search_index():
    with connections['default'].cursor() as cursor:
        for language in EVEMAIL_SEARCH_LANGUAGES:
            cursor.execute('''
            INSERT INTO
                evemail_searchindex ("messageID", index_language, document)
            SELECT
                msg."messageID",
                %(language)s::REGCONFIG,
                setweight(to_tsvector(unaccent(msg.title)), 'A') ||
                    setweight(to_tsvector(unaccent(msg."senderName")), 'C') ||
                    setweight(to_tsvector(unaccent(coalesce((string_agg(names.name, ', ')), ''))), 'D') ||
                    setweight(to_tsvector(unaccent(msg.parsed_message)), 'B')
            FROM
                character_mailmessage msg
            JOIN
                character_mailmessage_owners owners ON owners.mailmessage_id = msg."messageID"
            JOIN
                universe_evename names ON names.id = owners.charactersheet_id
            WHERE
                msg."messageID" IN (
                    SELECT
                        DISTINCT(mail."messageID")
                    FROM
                        character_mailmessage mail
                    LEFT JOIN
                        evemail_searchindex idx ON mail."messageID" = idx."messageID" AND
                        index_language = %(language)s::REGCONFIG
                    WHERE
                        idx."messageID" IS NULL
                )
            GROUP BY
                  msg."messageID";
            ''', {'language': language})


class MailStatus(models.Model):
    message = models.ForeignKey(MailMessage)
    read = models.BooleanField(default=False)
    owner = models.ForeignKey(Capsuler)

    class Meta:
        unique_together = ('message', 'owner')


class MailManager(models.Manager):
    def search(self, query, capsuler, language='english'):
        # For some reason, psycopg2 throws ProgrammingError if there's quotes
        # in the search string.
        query = query.replace("'","")
        try:
            return self.raw('''
            SELECT
              mail."messageID",
              mail.title,
              mail."senderName",
              mail."senderID",
              mail."sentDate",
              mail.parsed_message,
              mail.read,
              mail.owner_id,
              mail.receivers,
              ts_rank(index.document, to_tsquery(unaccent( %(query)s ))) as relevancy
            FROM
              evemail_mail mail,
              evemail_searchindex index
            WHERE
              mail."messageID" = index."messageID" AND
              mail.owner_id = %(capsuler)s AND
              index.index_language = %(language)s::REGCONFIG AND
              index.document @@ to_tsquery(unaccent( %(query)s ))
            ORDER BY ts_rank(index.document, to_tsquery(unaccent( %(query)s ))) DESC;
            ''', {'query': query, 'capsuler': capsuler.pk, 'language': language})
        except:
            return []


class Mail(models.Model):
    messageID = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    senderName = models.CharField(max_length=255, blank=True, null=True)
    senderID = models.IntegerField()
    sentDate = custom.DateTimeField()
    parsed_message = models.TextField(null=True)
    read = models.BooleanField(default=False)
    owner = models.ForeignKey(Capsuler)
    receivers = JsonBField(default=[], null=True)
    relevancy = models.FloatField(default=1.0)

    objects = MailManager()

    def __unicode__(self):
        return self.title


    class Meta:
        managed = False


@receiver(post_save, sender=MailMessage)
def update_apidata(sender, instance=None, created=False, **kwargs):
    with connections['default'].cursor() as cursor:
        for language in EVEMAIL_SEARCH_LANGUAGES:
            try:
                cursor.execute('''
                SELECT
                    1
                FROM
                    evemail_searchindex
                WHERE
                    "messageID" = %(messageID)s AND
                    index_language = %(language)s::REGCONFIG;
                ''', {'messageID': instance.pk,
                      'language': language})
                if cursor.rowcount == 0:
                    cursor.execute(
                        '''
                        INSERT INTO
                            evemail_searchindex ("messageID", index_language, document)
                        SELECT
                            %(messageID)s,
                            %(language)s::REGCONFIG,
                            setweight(to_tsvector(unaccent(msg.title)), 'A') ||
                                setweight(to_tsvector(unaccent(msg."senderName")), 'C') ||
                                setweight(to_tsvector(unaccent(coalesce((string_agg(names.name, ', ')), ''))), 'D') ||
                                setweight(to_tsvector(unaccent(msg.parsed_message)), 'B')
                              FROM
                                  character_mailmessage msg
                              JOIN
                                  character_mailmessage_owners owners ON owners.mailmessage_id = msg."messageID"
                              JOIN
                                  universe_evename names ON names.id = owners.charactersheet_id
                              WHERE
                                  msg."messageID" = %(messageID)s
                              GROUP BY
                                  msg."messageID";
                        ''', {'messageID': instance.pk,
                              'language': language})
            except:
                log.warning('Failed to index evemail {0} for language {1}.'.format(
                    instance.messageID, language
                ))
    for character in instance.owners.all():
        MailStatus.objects.get_or_create(message=instance, owner=character.owner)

