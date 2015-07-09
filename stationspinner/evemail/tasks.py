from stationspinner.celery import app
from django.db import connection
from stationspinner.settings import EVEMAIL_SEARCH_LANGUAGES

@app.task(name='evemail.update_search_index')
def update_search_index():
    with connection.cursor() as cursor:
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
