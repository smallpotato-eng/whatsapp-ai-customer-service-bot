## What I Built

- WhatsApp message bridge using Baileys and Express.js
- n8n workflow for message routing, session handling, and LLM orchestration
- Flask API for sessions, conversations, appointments, orders, SOP loading, and quotations
- SQLite database for persistent conversation memory and user sessions
- SOP-grounded prompt workflow for business-specific customer service
- Intent detection for FAQ, appointment, quotation, and general support
- PDF quotation generator for multiple business verticals
- Automated WhatsApp document delivery
- Sanitized GitHub-ready structure with `.env.example` and secret separation

## Key Features

- Multi-business support: beauty, insurance, real estate, and online shop
- Conversation history and session persistence
- Business SOP loading for grounded responses
- Structured intent tags for downstream automation
- Personalized PDF quotation generation
- WhatsApp text reply and document sending
- Reset/session handling flow
- Docker Compose support for Evolution API, Postgres, and Redis

## Tech Stack

- Python
- Flask
- SQLite
- JavaScript / Node.js
- Express.js
- Baileys WhatsApp API
- n8n
- Groq LLM API
- FPDF
- Docker Compose

## Why This Project Matters

Many chatbot demos only generate text replies. This project connects an LLM to a real customer service workflow: it remembers users, follows business SOPs, detects intent, generates business documents, and sends outputs back through WhatsApp.

It shows practical LLM application development for customer service, operations automation, and business workflow integration.

## Example Use Cases

- Beauty salon treatment enquiries and quotation generation
- Insurance plan enquiries and estimated premium quotation
- Real estate enquiry handling and commission estimate
- Online shop customer support and order quotation

## Security Notice

This repository is a sanitized portfolio version.

The following are intentionally excluded:

- Real API keys
- WhatsApp sessions
- Customer databases
- Chat logs
- Generated quotation PDFs
- Uploaded files
- Payment or private business data

Use `.env.example` to configure your own local credentials.
