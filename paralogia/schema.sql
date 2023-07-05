-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;


create table user (
    user_id integer primary key autoincrement,
    username text unique not null,
    password text not null
);


