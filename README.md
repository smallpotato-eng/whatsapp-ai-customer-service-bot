# WhatsApp AI Customer Service Automation Bot

An end-to-end WhatsApp AI customer service automation system that connects WhatsApp, n8n, Flask, SQLite, Groq LLM, SOP-grounded prompts, and automated PDF quotation generation.

This project demonstrates how LLMs can be integrated into real customer service workflows instead of remaining as standalone chat interfaces.

## Demo Flow

1. Customer sends a message on WhatsApp.
2. Baileys WhatsApp bridge forwards the message to an n8n webhook.
3. n8n loads the customer session, conversation history, and business SOP.
4. Groq LLM generates a response based on the SOP and conversation context.
5. The workflow detects customer intent such as FAQ, appointment, or quotation.
6. For quotation requests, Flask generates a personalized PDF quotation.
7. The WhatsApp bridge sends the reply and PDF back to the customer.

## Architecture

```mermaid
flowchart LR
    A[WhatsApp Customer] --> B[Baileys WhatsApp Bridge]
    B --> C[n8n Webhook Workflow]
    C --> D[Flask API]
    D --> E[SQLite Database]
    C --> F[Groq LLM]
    F --> C
    C --> G[PDF Quotation Generator]
    G --> B
    B --> H[Customer Receives Reply or PDF]
