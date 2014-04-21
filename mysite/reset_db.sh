#!/bin/bash

cd mysite
rm users.sql
printf ".mode insert auth_user\n select * from auth_user;" | sqlite3 db.sqlite3 >> users.sql
printf ".mode insert petetwitt_profile\n select * from petetwitt_profile;" | sqlite3 db.sqlite3 >> users.sql
printf ".mode insert petetwitt_profile_following\n select * from petetwitt_profile_following;" | sqlite3 db.sqlite3 >> users.sql
cd ..

rm mysite/db.sqlite3
yes 'no' | ./manage.py syncdb
cd mysite
cat users.sql | sqlite3 -echo db.sqlite3
cd ..
