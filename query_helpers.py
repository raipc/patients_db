# -*- coding: utf-8 -*-
def sex_str_to_int(sex):
    if sex == u"мужской":
        return '1'
    elif sex == u"женский":
        return '2'
    return None


def clear_filter(filter_list):
    return filter(lambda x: x[1], filter_list)


def generate_query(last_name,
                   first_name,
                   patr_name,
                   document_type,
                   serial,
                   number,
                   sex,
                   birth_date_from,
                   birth_date_to,
                   age_from,
                   age_to,
                   snils):
    if birth_date_to:
        age_from = ""
    if birth_date_from:
        age_to = ""
    select = u"""
SELECT
    CONCAT (
        Client.lastName, " ", Client.firstName, " ", Client.patrName
    ) AS `ФИО`,
    Client.birthDate AS `Дата рождения`,
    TIMESTAMPDIFF(YEAR, Client.birthDate, CURRENT_DATE()) AS `Возраст`,
    CASE Client.sex
        WHEN 1 THEN "мужской"
        WHEN 2 THEN "женский"
    END AS `Пол`,
    Client.SNILS AS `СНИЛС`,
    t.name AS `Документ`,
    t.num AS `Серия номер`
FROM Client LEFT JOIN
    (SELECT CONCAT (
        ClientDocument.serial, " ", ClientDocument.number
        ) AS num, ClientDocument.serial, ClientDocument.number,
        ClientDocument.client_id AS client_id,
        rbDocumentType.name, rbDocumentType.id AS doc_type_id
    FROM ClientDocument INNER JOIN rbDocumentType
        ON rbDocumentType.id = ClientDocument.documentType_id
    WHERE ClientDocument.deleted = 0) AS t
    ON Client.id = t.client_id
WHERE"""

    filters = [('Client.deleted', ' = 0'),
               ('Client.lastName like "%', last_name, '%"'),
               ('Client.firstName like "%', first_name, '%"'),
               ('Client.patrName like "%', patr_name, '%"'),
               ('t.doc_type_id = ', document_type),
               ('t.serial like "%', serial, '%"'),
               ('t.number like "%', number, '%"'),
               ('Client.sex = ', sex_str_to_int(sex)),
               ('Client.birthDate >= STR_TO_DATE("',
                birth_date_from, '", "%Y-%m-%d")'),
               ('Client.birthDate <= STR_TO_DATE("',
                birth_date_to, '", "%Y-%m-%d")'),
               ('SNILS  like "%', snils, '%"'),
               ('TIMESTAMPDIFF(YEAR, Client.birthDate, CURRENT_DATE()) >= ',
                age_from),
               ('TIMESTAMPDIFF(YEAR, Client.birthDate, CURRENT_DATE()) <= ',
                age_to)
               ]

    filter_string = " AND\n\t".join(
        [u''.join(condition) for condition in clear_filter(filters)])
    return " \n\t".join([select, filter_string, ";"])


def get_document_types_query():
    return u"SELECT name, id FROM rbDocumentType ORDER BY id"
