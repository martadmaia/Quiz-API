# Distributed Systems Project: Quiz Management System

## Project Overview

This project is a distributed system for managing quizzes, developed as a Flask application. The system provides a RESTful API for creating, and retrieving quizzes, question sets (qsets), and individual questions. Participants can register for quizzes, answer questions, and receive performance results. The project utilizes a combination of Flask, SQLite, Zookeeper, and secure communication with signed certificates.

## Features

- **Quiz Management**: Create, and retrieve quizzes, qsets, and questions.
- **Participant Interaction**: Register for quizzes, answer questions, and get performance results.
- **Secure Communication**: Uses signed certificates for secure communication between server and clients.
- **Database Management**: SQLite database with an SQL schema for quizzes, questions, and answers.
- **Real-time Notifications**: Utilizes Zookeeper for notifying participants of quiz changes and updates.

## Project Structure

```plaintext
.
├── client
    ├── cli.crt
    ├── cli.csr
    ├── cli.key
├── client
    ├── serv.crt
    ├── serv.csr
    ├── serv.key
├── kuko_client.py
├── kuko_data.py
├── kuko_flask.py
├── kuko_stub.py
├── README.md
├── root.key
├── root-pem
├── setup_db.py
├── utils.py
└── schema.sql

```

## API Endpoints

### Quizzes

- **Create a Quiz**: `POST /quiz`
- **Retrieve a Quiz**: `GET /quiz/<quiz_id>`
- **Retrieve a Quiz Status**: `GET /quiz/<quiz_id>`

### Questions

- **Create a Question**: `POST /question`
- **Retrieve a Question**: `GET /question/<question_id>`

### QSets

- **Create a QSet**: `POST /qset`

### Quiz Gameplay

- **Launch a Quiz**: `POST /launch/<quiz_id>`
- **Advance to Next Question**: `POST /next/<quiz_id>`
- **Retrieve Current Question**: `GET /get/<quiz_id>`
- **Answer Current Question**: `POST /ans/<quiz_id>`
- **Register in Quiz**: `POST /reg/quiz_id`
- **Get Performance Results**: `GET /rel/<quiz_id>`

## Secure Communication

The communication between the client and server is secured using SSL/TLS with signed certificates.

## Database Schema

The SQLite database is initialized with the schema defined in `schema.sql`.

## Real-time Notifications

Zookeeper is used to notify participants when a quiz changes. When a participant answers a question, they receive a notification, and the client stub makes an immediate request to get the next question or their performance report.