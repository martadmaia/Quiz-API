DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS quiz;
DROP TABLE IF EXISTS qset;
DROP TABLE IF EXISTS question;

CREATE TABLE question (
    id_question INTEGER,
    question TEXT NOT NULL,
    answers TEXT NOT NULL,
    k INT NOT NULL,

    CONSTRAINT pk_question
    PRIMARY KEY (id_question)
);

CREATE TABLE qset (
    id_qset INTEGER,
    questions TEXT NOT NULL,

    CONSTRAINT pk_qset
    PRIMARY KEY (id_qset)
);

CREATE TABLE quiz (
    id_quiz INTEGER,
    id_qset INTEGER,
    state VARCHAR(50) DEFAULT 'PREPARED', -- PREPARED, ONGOING, ENDED 
    points TEXT,
    timestamp_p DATETIME,
    timestamp_e DATETIME,
    question_i INT DEFAULT 0,
    participants TEXT,

    CONSTRAINT pk_quiz
    PRIMARY KEY (id_quiz),

    CONSTRAINT fk_quiz_qset
    FOREIGN KEY (id_qset) REFERENCES qset(id_qset) ON DELETE CASCADE
);

CREATE TABLE results (
    id_quiz INTEGER,
    question_i INT,
    participant INT,
    answer INT,

    CONSTRAINT pk_results
    PRIMARY KEY (id_quiz, question_i, participant),

    CONSTRAINT fk_results_quiz
    FOREIGN KEY (id_quiz) REFERENCES quiz(id_quiz) ON DELETE CASCADE
);

INSERT INTO question (question, answers, k) 
VALUES
('What is the capital of France?', 'Paris;Berlin;London;Madrid', 1),
('Who wrote "Romeo and Juliet"', 'William Shakespeare;Jane Austen;Virgina Woolf;Lord Byron', 1),
('What is the chemical symbol for silver', 'Au;Ag;Fe;Cu', 1),
('What is the capital of Italy?', 'Rome;Berlin;Paris;Madrid', 1),
('What is the chemical symbol for tin', 'Ti;Zr;Sn;At', 3),
('Cleopatra was romantically linked to what historical figure?', 'Alexander the Great;Julius Caesar;King Tut;Genghis Khan', 4),
('King Henry VIII established the Church of England in order to marry what woman?', 'Catherine of Aragon;Jane Seymour;Katherine Parr;Anne Boleyn', 4),
('After their spouse died in 1861, what monarch wore black every day for 40 years?', 'Queen Victoria;Marie Antoinette;Catherine the Great;Queen Elizabeth I', 4),
('Which of these is known as the “love hormone” and “cuddle chemical?', 'oxytocin;cortisol;dopamine;adrenaline', 4),
('Roughly three percent of mammals are monogamous. Which of these mammals mate for life?', 'African elephants;silverback gorillas;prairie voles;fruit bats', 3);

INSERT INTO qset (questions)
VALUES
('1;2;3;4');

INSERT INTO quiz (id_qset, points, timestamp_p)
VALUES
(1, '5;5;5;5', 1714385134);