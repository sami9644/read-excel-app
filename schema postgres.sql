CREATE TABLE students (
    studid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fullname TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    birthdate DATE NOT NULL,
    CEFR VARCHAR(2) CHECK (CEFR IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    paiduntil DATE,
    password TEXT NOT NULL
);

-- SELECT * FROM audiorec;

CREATE TABLE passages (
    passage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    passage TEXT NOT NULL,
    CEFR VARCHAR(2) CHECK (CEFR IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2'))
);

ALTER TABLE passages
ADD COLUMN age VARCHAR(10) NOT NULL CHECK (age IN ('3-6', '7-12', '13-19', '20+'));

CREATE TABLE quizzes (
    quizid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    passage UUID,
    FOREIGN KEY (passage) REFERENCES passages(passage_id) ON DELETE CASCADE
);

ALTER TABLE quizzes
ADD COLUMN isevaluated VARCHAR(10) DEFAULT 'NO';

CREATE TABLE audiorec (
    audioid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio TEXT NOT NULL,
    student UUID NOT NULL,
    passage UUID NOT NULL,
    feedback TEXT,
    FOREIGN KEY (student) REFERENCES students(studid) ON DELETE CASCADE,
    FOREIGN KEY (passage) REFERENCES passages(passage_id) ON DELETE CASCADE
);

SELECT * FROM quizzes;