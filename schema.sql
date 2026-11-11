CREATE DATABASE readdb;
USE readdb;

CREATE TABLE students(
studid VARCHAR(100) PRIMARY KEY,
fullname TEXT NOT NULL,
phone VARCHAR(20) NOT NULL UNIQUE,
birthdate DATE NOT NULL,
CEFR ENUM('A1','A2','B1','B2','C1','C2'),
paiduntil DATE,
password TEXT NOT NULL
);
-- SELECT * FROM audiorec
CREATE TABLE passages(
passage_id VARCHAR(100) PRIMARY KEY,
title TEXT NOT NULL,
passage TEXT NOT NULL,
CEFR ENUM('A1','A2','B1','B2','C1','C2')
);
ALTER TABLE passages ADD COLUMN age ENUM("3-6","7-12","13-19","20+") NOT NULL;


CREATE TABLE quizzes(
quizid VARCHAR(100) PRIMARY KEY,
question TEXT NOT NULL,
passage VARCHAR(100),
FOREIGN KEY(passage) REFERENCES passages(passage_id) ON DELETE CASCADE
);
ALTER TABLE quizzes ADD COLUMN isevaluated VARCHAR(10) DEFAULT "NO";



CREATE TABLE audiorec(
audioid VARCHAR(100) PRIMARY KEY,
audio TEXT NOT NULL,
student VARCHAR(100) NOT NULL,
passage VARCHAR(100) NOT NULL,
feedback TEXT,
FOREIGN KEY (student) REFERENCES students(studid) ON DELETE CASCADE,
FOREIGN KEY(passage) REFERENCES passages(passage_id) ON DELETE CASCADE
);

SELECT * FROM quizzes