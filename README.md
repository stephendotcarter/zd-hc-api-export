# zd-hc-api-export
Zendesk Help Center API Export

# Description
This script exports Zendesk Help Center objects to a relational database.
The data can then be used to execute more advanced queries that what are possible through the Zendesk Help Center API.

The following objects are exported:
* Artcles
* Translations
* Sections
* Categories
* Labels
* Access Policies (merged in to the section object)
* Users


# Instructions
Install the required libraries:
```
pip install -r requirements.txt
```

Update run.sh with the following:
```
ZD_BASE_URL="https://*.zendesk.com"
ZD_USER=""
ZD_PWD=""
SQLALCHEMY_CONN_STRING="postgresql://user:password@localhost/database"
```

Run the script:
```
./run.sh
```


# Todo
* Currently the existing tables are dropped and recreated every time the script is run. This needs to be changed so that the existing tables are updated.
