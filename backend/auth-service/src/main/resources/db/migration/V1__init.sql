CREATE DATABASE auth_db OWNER postgres;
\c auth_db

CREATE TABLE users (
                       id UUID PRIMARY KEY,
                       fio VARCHAR(255) NOT NULL,
                       email VARCHAR(255) UNIQUE NOT NULL,
                       password VARCHAR(255) NOT NULL
);
