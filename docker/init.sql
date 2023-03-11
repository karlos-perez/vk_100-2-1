CREATE USER chief WITH password 'chief_paSS';
CREATE DATABASE hundred2one OWNER chief;
GRANT ALL PRIVILEGES ON DATABASE hundred2one TO chief;
CREATE USER test_user WITH password 'test_pass';
CREATE DATABASE test OWNER test_user;
GRANT ALL PRIVILEGES ON DATABASE test TO test_user;

