# Project Scope

## Project Goal

Build a production-like Personal Finance Backend API.

## MVP Features

### User

- Register
- Login
- View Profile

### Account

Examples:

- Cash
- Bank Account
- Credit Card
- E-Wallet

Functions:

- Create
- Read
- Update
- Delete

### Category

Examples:

- Salary
- Food
- Transportation
- Childcare
- Rent
- Entertainment

Functions:

- Create
- Read
- Update
- Delete

### Transaction

Functions:

- Create transaction
- View transaction
- Update transaction
- Delete transaction
- Filter transactions

### Reports

- Monthly income summary
- Monthly expense summary
- Category summary

## Database Tables

### users

- id
- email
- password_hash
- created_at

### accounts

- id
- user_id
- name
- type
- currency

### categories

- id
- user_id
- name
- type

### transactions

- id
- user_id
- account_id
- category_id
- amount
- transaction_type
- transaction_date
- description

## Out of Scope (Current Phase)

- Redis
- Kafka
- Microservices
- DDD
- CQRS
- Multi-tenant Architecture
