#!/usr/bin/env python
import os
import sys
import requests
import json
from sqlalchemy import create_engine, select, Table, Column, Integer, String, DateTime, Boolean, Text, MetaData
from sqlalchemy.orm import sessionmaker

zd_base_url = os.environ['ZD_BASE_URL']
user = os.environ['ZD_USER']
pwd = os.environ['ZD_PWD']
conn_string = os.environ['SQLALCHEMY_CONN_STRING']

zd = requests.session()

# Get all Zendesk Objects for a given URL
def get_all(url, key, options):

    per_page = 100
    page = 1

    objs = {}
    print "\nHTTP GET {0}".format(url)
    while True:
        page_url = "{0}?page={1}&per_page={2}{3}".format(url, page, per_page, options)
        response = zd.get(page_url, auth=(user, pwd))
        data = response.json()

        # Labels are all in a single page so extract them directly
        if key == 'labels':
            for obj in data[key]:
                objs[obj['id']] = obj
            break
        else:
            page_total = int(data['count'] / per_page)
            print "{0}/{1}".format(page, page_total),
            sys.stdout.flush()

            for obj in data[key]:
                objs[obj['id']] = obj

            #break  # Stop at 1 page for debugging

            if data['next_page'] is None:
                break
            else:
                page += 1
    return objs

# SQLAlchemy Connection
engine = create_engine(conn_string)

Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.bind = engine

# SQLAlchemy Objects
users = Table('users', metadata,
    Column('id', Integer, unique=True),
    Column('url', String(255)),
    Column('name', String(255)),
    Column('external_id', String(255)),
    Column('alias', String(255)),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
    Column('active', Boolean),
    Column('verified', Boolean),
    Column('shared', Boolean),
    Column('shared_agent', Boolean),
    Column('locale', String(16)),
    Column('locale_id', Integer),
    Column('time_zone', String(255)),
    Column('last_login_at', DateTime(timezone=True)),
    Column('email', String(255)),
    Column('phone', String(255)),
    Column('signature', Text),
    Column('details', Text),
    Column('notes', String(255)),
    Column('organization_id', Integer),
    Column('role', String(255)),
    Column('custom_role_id', Integer),
    Column('moderator', Boolean),
    Column('ticket_restriction', String(255)),
    Column('only_private_comments', Boolean),
    Column('suspended', Boolean),
    Column('restricted_agent', Boolean),
)


articles = Table('articles', metadata,
    Column('id', Integer, unique=True),
    Column('body', Text),
    Column('title', String(255)),
    Column('url', String(255)),
    Column('vote_sum', Integer),
    Column('created_at', DateTime(timezone=True)),
    Column('source_locale', String(16)),
    Column('comments_disabled', Boolean),
    Column('html_url', String(255)),
    Column('updated_at', DateTime(timezone=True)),
    Column('section_id', Integer, index=True),
    Column('locale', String(16)),
    Column('vote_count', Integer),
    Column('draft', Boolean),
    Column('promoted', Boolean),
    Column('position', Integer),
    Column('author_id', Integer, index=True),
    Column('outdated', Boolean),
)


translations = Table('translations', metadata,
    Column('id', Integer, unique=True),
    Column('url', String(255)),
    Column('html_url', String(255)),
    Column('source_id', Integer, index=True),
    Column('source_type', String(16)),
    Column('locale', String(16)),
    Column('title', String(255)),
    Column('body', Text),
    Column('outdated', Boolean),
    Column('draft', Boolean),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
)


# viewable_by and manageable_by fields are included directly in the sections table
sections = Table('sections', metadata,
    Column('id', Integer, unique=True),
    Column('name', String(255)),
    Column('description', Text),
    Column('locale', String(16)),
    Column('source_locale', String(16)),
    Column('url', String(255)),
    Column('html_url', String(255)),
    Column('category_id', Integer, index=True),
    Column('outdated', Boolean),
    Column('position', Integer),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
    Column('viewable_by', String(255)),
    Column('manageable_by', String(255)),
)


categories = Table('categories', metadata,
    Column('id', Integer, unique=True),
    Column('name', String(255)),
    Column('description', Text),
    Column('locale', String(16)),
    Column('source_locale', String(16)),
    Column('url', String(255)),
    Column('html_url', String(255)),
    Column('outdated', Boolean),
    Column('position', Integer),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
)


labels = Table('labels', metadata,
    Column('id', Integer, unique=True),
    Column('url', String(255)),
    Column('name', String(255), unique=True),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
)


# Custom table to hold the article <> label relationships
article_labels = Table('article_labels', metadata,
    Column('article_id', Integer, index=True),
    Column('label_id', Integer, index=True),
)

# Currently all tables are dropped and recreated on each execution
# This will be updated in the future to update all rows
metadata.drop_all()
metadata.create_all()

# Pair up the SQLAlchemy objects with the corresponding Zendesk Help Center API calls
tables = [{
    'object': 'users',
    'sqlobject': users,
    'url': zd_base_url + '/api/v2/users.json',
    'options': '',
}, {
    'object': 'labels',
    'sqlobject': labels,
    'url': zd_base_url + '/api/v2/help_center/articles/labels.json',
    'options': '',
}, {
    'object': 'articles',
    'sqlobject': articles,
    'url': zd_base_url + '/api/v2/help_center/articles.json',
    'options': '&include=translations',
}, {
    'object': 'sections',
    'sqlobject': sections,
    'url': zd_base_url + '/api/v2/help_center/sections.json',
    'options': '',
}, {
    'object': 'categories',
    'sqlobject': categories,
    'url': zd_base_url + '/api/v2/help_center/categories.json',
    'options': '',
}]

for table in tables:
    print "\n------------------------------------------------------------"
    print "Getting {0}".format(table['object'])

    # Get all objects
    data = get_all(table['url'], table['object'], table['options'])

    inserted = 0
    if table['object'] == 'articles':
        for id, row in data.iteritems():
            #print "\t", row['id'], row['title']

            # Insert article
            session.execute(table['sqlobject'].insert(), [row])

            # Insert all translations of the article
            for trans in row['translations']:
                session.execute(translations.insert(), trans)

            # Get all the label details
            if len(row['label_names']) > 0:
                # First get the label id and names from the database that match the current labels
                label_ids = session.execute(
                    select(
                        [labels.c.id, labels.c.name],
                        labels.c.name.in_((row['label_names']))
                    )
                ).fetchall()

                # Create list of article_id <> label_id pairs
                label_inserts = []
                for label in label_ids:
                    label_inserts.append({
                        'article_id': row['id'],
                        'label_id': label[0]
                    })

                # If we have some labels then insert them
                if len(label_inserts) > 0:
                    session.execute(article_labels.insert(), label_inserts)

            inserted += 1
    elif table['object'] == 'sections':
        for id, row in data.iteritems():
            #print "\t", row['id'], row['name']
            
            response = zd.get(zd_base_url + "/api/v2/help_center/sections/{0}/access_policy.json".format(row['id']), auth=(user, pwd))
            access_policy = response.json()['access_policy']
            row['viewable_by'] = access_policy['viewable_by']
            row['manageable_by'] = access_policy['manageable_by']
            session.execute(table['sqlobject'].insert(), [row])

            inserted += 1
    else:
        for id, row in data.iteritems():
            #print "\t", row['id'], row['name']

            session.execute(table['sqlobject'].insert(), [row])

            inserted += 1

    print "\nInserted {0}: {1}/{2}".format(table['object'], inserted, len(data))

# Commit the SQLAlchemy session
session.commit()
session.close()

print "\nMy work here is done..."