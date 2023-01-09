#fake port obviously.
mongosh "mongdb://127.0.0.1:12345/";
use admin;
db.createUser
#Fake username and password, obviously.
db.createUser({ user: "username", pwd: "password", roles: [ "readWrite", "dbAdmin" ]})
