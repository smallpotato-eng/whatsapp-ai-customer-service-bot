import json
from datetime import datetime

nodes = [
  # 1. Webhook
  {
    "id": "univ-webhook",
    "name": "Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [240, 300],
    "parameters": {
      "httpMethod": "POST",
      "path": "cs-lite",
      "responseMode": "responseNode",
      "options": {}
    }
  },

  # 2. Extract Message
  {
    "id": "univ-extract",
    "name": "Extract Message",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [460, 300],
    "parameters": {
      "jsCode": """const body = $input.first().json.body;
const msgs = body?.data?.messages || body?.messages || [];
if (!msgs.length) return [];
const msg = msgs[0];
const phone = (msg.key?.remoteJid || '').replace('@s.whatsapp.net','').replace('@c.us','');
const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
const fromMe = msg.key?.fromMe || false;
if (fromMe || !phone || !text) return [];
return [{ json: { phone, text } }];"""
    }
  },

  # 3. Is Reset
  {
    "id": "univ-is-reset",
    "name": "Is Reset",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [680, 300],
    "parameters": {
      "conditions": {
        "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose"},
        "conditions": [
          {
            "leftValue": "={{ $json.text.trim() }}",
            "rightValue": "/start",
            "operator": {"type": "string", "operation": "equals"}
          }
        ],
        "combinator": "and"
      },
      "options": {}
    }
  },

  # 4. Delete Session (reset path)
  {
    "id": "univ-delete-session",
    "name": "Delete Session",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [900, 160],
    "parameters": {
      "method": "DELETE",
      "url": "=http://127.0.0.1:5050/session/{{ $('Extract Message').item.json.phone }}",
      "options": {}
    }
  },

  # 5. Send Reset Confirm
  {
    "id": "univ-send-reset",
    "name": "Send Reset",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1120, 160],
    "parameters": {
      "method": "POST",
      "url": "http://YOUR_EVOLUTION_IP:8080/message/sendText/YOUR_INSTANCE_NAME",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $('Extract Message').item.json.phone, text: '對話已重置，請重新開始 😊' }) }}",
      "options": {}
    }
  },

  # 6. Respond Reset OK
  {
    "id": "univ-respond-reset",
    "name": "Respond Reset OK",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [1340, 160],
    "parameters": {
      "respondWith": "json",
      "responseBody": "{\"ok\":true}",
      "options": {}
    }
  },

  # 7. Load SOP (Google Sheets CSV)
  {
    "id": "univ-load-sop",
    "name": "Load SOP",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [900, 300],
    "parameters": {
      "method": "GET",
      "url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0",
      "options": {}
    }
  },

  # 8. Parse SOP
  {
    "id": "univ-parse-sop",
    "name": "Parse SOP",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1120, 300],
    "parameters": {
      "jsCode": """const raw = $input.first().json.data || '';
const lines = raw.split('\\n').filter(l => l.trim());
const sop = {};

for (const line of lines) {
  // Robust CSV parse: key in col A, value in col B
  const firstComma = line.indexOf(',');
  if (firstComma === -1) continue;
  const key = line.substring(0, firstComma).trim().replace(/^\"|\"$/g, '').toLowerCase().replace(/\\s+/g, '_');
  let value = line.substring(firstComma + 1).trim();
  // Remove surrounding quotes and unescape double quotes
  if (value.startsWith('"') && value.endsWith('"')) {
    value = value.slice(1, -1).replace(/""/g, '"');
  }
  sop[key] = value;
}

return [{ json: sop }];"""
    }
  },

  # 9. Get Session
  {
    "id": "univ-get-session",
    "name": "Get Session",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1340, 300],
    "parameters": {
      "method": "GET",
      "url": "=http://127.0.0.1:5050/session/{{ $('Extract Message').item.json.phone }}",
      "options": {}
    }
  },

  # 10. New or Existing
  {
    "id": "univ-new-existing",
    "name": "New or Existing",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [1560, 300],
    "parameters": {
      "conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
        "conditions": [
          {
            "leftValue": "={{ $json.statusCode }}",
            "rightValue": 404,
            "operator": {"type": "number", "operation": "equals"}
          }
        ],
        "combinator": "and"
      },
      "options": {}
    }
  },

  # 11. Save Session (new user)
  {
    "id": "univ-save-session",
    "name": "Save Session",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1780, 160],
    "parameters": {
      "method": "POST",
      "url": "http://127.0.0.1:5050/session",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ phone_number: $('Extract Message').item.json.phone, business_type: 'universal', status: 'active' }) }}",
      "options": {}
    }
  },

  # 12. Send Welcome (new user)
  {
    "id": "univ-send-welcome",
    "name": "Send Welcome",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2000, 160],
    "parameters": {
      "method": "POST",
      "url": "http://YOUR_EVOLUTION_IP:8080/message/sendText/YOUR_INSTANCE_NAME",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $('Extract Message').item.json.phone, text: $('Parse SOP').item.json.welcome_message || '👋 你好！有什麼可以幫到你？' }) }}",
      "options": {}
    }
  },

  # 13. Respond Welcome OK
  {
    "id": "univ-respond-welcome",
    "name": "Respond Welcome OK",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [2220, 160],
    "parameters": {
      "respondWith": "json",
      "responseBody": "{\"ok\":true}",
      "options": {}
    }
  },

  # 14. Get History (existing user)
  {
    "id": "univ-get-history",
    "name": "Get History",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1780, 300],
    "parameters": {
      "method": "GET",
      "url": "=http://127.0.0.1:5050/conversations/{{ $('Extract Message').item.json.phone }}?limit=10",
      "options": {"response": {"response": {"alwaysOutputData": True}}}
    }
  },

  # 15. Build Messages
  {
    "id": "univ-build-messages",
    "name": "Build Messages",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2000, 300],
    "parameters": {
      "jsCode": """const sop = $('Parse SOP').item.json;
const roleName    = sop.role_name      || 'Assistant';
const companyName = sop.company_name   || 'Our Company';
const tone        = sop.tone           || 'Professional and friendly';
const sopContent  = sop.sop_content    || 'Provide helpful customer service.';

const phone    = $('Extract Message').item.json.phone;
const userText = $('Extract Message').item.json.text;
const history  = $('Get History').item.json?.history || [];

const systemPrompt = `You are ${roleName}, the customer service representative for ${companyName}.
Your personality and tone should be: ${tone}.

Here is the STRICT SOP and all information you must follow:
<SOP>
${sopContent}
</SOP>

CRITICAL RULES (YOU MUST OBEY):
1. Never break character. Never reveal you are an AI.
2. Only answer based on the <SOP> above. Do not make up information.
3. If a customer asks something unrelated to ${companyName}'s business, politely decline and guide them back.
4. If a customer asks for discounts or services not in the <SOP>, refuse politely. Do not repeat the same refusal phrase every time — vary your wording naturally.
5. When you have enough info to generate a quote, append EXACTLY: [QUOTE:{json_data}][INTENT:QUOTE]
6. Otherwise append ONE tag only: [INTENT:FAQ] or [INTENT:APPOINTMENT] or [INTENT:OTHER]`;

const messages = [{ role: 'system', content: systemPrompt }];
for (const h of history) {
  messages.push({ role: h.role, content: h.content });
}
messages.push({ role: 'user', content: userText });

return [{ json: { phone, messages, userText } }];"""
    }
  },

  # 16. Groq AI
  {
    "id": "univ-groq",
    "name": "Groq AI",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2220, 300],
    "parameters": {
      "method": "POST",
      "url": "https://api.groq.com/openai/v1/chat/completions",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "Authorization", "value": "Bearer YOUR_GROQ_API_KEY"}]
      },
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": "={{ JSON.stringify({ model: 'llama-3.3-70b-versatile', temperature: 0.3, messages: $json.messages }) }}",
      "options": {"timeout": 60000}
    }
  },

  # 17. Parse AI Response
  {
    "id": "univ-parse-ai",
    "name": "Parse AI Response",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2440, 300],
    "parameters": {
      "jsCode": """const aiResp  = $input.first().json;
const content  = aiResp.choices?.[0]?.message?.content || '';
const phone    = $('Build Messages').item.json.phone;
const userText = $('Build Messages').item.json.userText;

const intentMatch = content.match(/\\[INTENT:([A-Z_]+)\\]/);
const intent = intentMatch ? intentMatch[1] : 'OTHER';

const quoteMatch = content.match(/\\[QUOTE:({[\\s\\S]*?})\\]/);
let quoteData = {};
if (quoteMatch) {
  try { quoteData = JSON.parse(quoteMatch[1]); } catch(e) {}
}

const replyText = content
  .replace(/\\[QUOTE:{[\\s\\S]*?}\\]/g, '')
  .replace(/\\[INTENT:[A-Z_]+\\]/g, '')
  .trim();

return [{ json: { phone, intent, replyText, quoteData, userText } }];"""
    }
  },

  # 18. Save User Msg
  {
    "id": "univ-save-user",
    "name": "Save User Msg",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2660, 300],
    "parameters": {
      "method": "POST",
      "url": "http://127.0.0.1:5050/conversations",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ phone_number: $json.phone, role: 'user', content: $json.userText }) }}",
      "options": {}
    }
  },

  # 19. Save AI Reply
  {
    "id": "univ-save-ai",
    "name": "Save AI Reply",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2880, 300],
    "parameters": {
      "method": "POST",
      "url": "http://127.0.0.1:5050/conversations",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ phone_number: $json.phone, role: 'assistant', content: $('Parse AI Response').item.json.replyText }) }}",
      "options": {}
    }
  },

  # 20. Send Reply
  {
    "id": "univ-send-reply",
    "name": "Send Reply",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [3100, 300],
    "parameters": {
      "method": "POST",
      "url": "http://YOUR_EVOLUTION_IP:8080/message/sendText/YOUR_INSTANCE_NAME",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $('Parse AI Response').item.json.phone, text: $('Parse AI Response').item.json.replyText }) }}",
      "options": {}
    }
  },

  # 21. Is Quote
  {
    "id": "univ-is-quote",
    "name": "Is Quote",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [3320, 300],
    "parameters": {
      "conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
        "conditions": [
          {
            "leftValue": "={{ $('Parse AI Response').item.json.intent }}",
            "rightValue": "QUOTE",
            "operator": {"type": "string", "operation": "equals"}
          }
        ],
        "combinator": "and"
      },
      "options": {}
    }
  },

  # 22. Generate Quote
  {
    "id": "univ-gen-quote",
    "name": "Generate Quote",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [3540, 160],
    "parameters": {
      "method": "POST",
      "url": "http://127.0.0.1:5050/quotation",
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": "={{ JSON.stringify({ business_type: $('Parse SOP').item.json.business_type || 'shop', phone: $('Parse AI Response').item.json.phone, quote_data: $('Parse AI Response').item.json.quoteData, lang: $('Parse SOP').item.json.lang || 'zh-hk' }) }}",
      "options": {"timeout": 30000}
    }
  },

  # 23. Send Document
  {
    "id": "univ-send-doc",
    "name": "Send Document",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [3760, 160],
    "parameters": {
      "method": "POST",
      "url": "http://YOUR_EVOLUTION_IP:8080/message/sendMedia/YOUR_INSTANCE_NAME",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "raw",
      "rawContentType": "application/json",
      "body": "={{ JSON.stringify({ number: $('Parse AI Response').item.json.phone, mediatype: 'document', mimetype: 'application/pdf', media: $json.base64, fileName: $json.filename, caption: '📄 報價單已生成，請查收！' }) }}",
      "options": {}
    }
  },

  # 24. Respond OK
  {
    "id": "univ-respond-ok",
    "name": "Respond OK",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [3540, 300],
    "parameters": {
      "respondWith": "json",
      "responseBody": "{\"ok\":true}",
      "options": {}
    }
  },

  # 25. Respond Quote OK
  {
    "id": "univ-respond-quote-ok",
    "name": "Respond Quote OK",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [3980, 160],
    "parameters": {
      "respondWith": "json",
      "responseBody": "{\"ok\":true}",
      "options": {}
    }
  }
]

connections = {
  "Webhook": {
    "main": [[{"node": "Extract Message", "type": "main", "index": 0}]]
  },
  "Extract Message": {
    "main": [[{"node": "Is Reset", "type": "main", "index": 0}]]
  },
  "Is Reset": {
    "main": [
      [{"node": "Delete Session", "type": "main", "index": 0}],   # true → reset
      [{"node": "Load SOP", "type": "main", "index": 0}]          # false → main
    ]
  },
  "Delete Session": {
    "main": [[{"node": "Send Reset", "type": "main", "index": 0}]]
  },
  "Send Reset": {
    "main": [[{"node": "Respond Reset OK", "type": "main", "index": 0}]]
  },
  "Load SOP": {
    "main": [[{"node": "Parse SOP", "type": "main", "index": 0}]]
  },
  "Parse SOP": {
    "main": [[{"node": "Get Session", "type": "main", "index": 0}]]
  },
  "Get Session": {
    "main": [[{"node": "New or Existing", "type": "main", "index": 0}]]
  },
  "New or Existing": {
    "main": [
      [{"node": "Save Session", "type": "main", "index": 0}],     # true → new user
      [{"node": "Get History", "type": "main", "index": 0}]       # false → existing
    ]
  },
  "Save Session": {
    "main": [[{"node": "Send Welcome", "type": "main", "index": 0}]]
  },
  "Send Welcome": {
    "main": [[{"node": "Respond Welcome OK", "type": "main", "index": 0}]]
  },
  "Get History": {
    "main": [[{"node": "Build Messages", "type": "main", "index": 0}]]
  },
  "Build Messages": {
    "main": [[{"node": "Groq AI", "type": "main", "index": 0}]]
  },
  "Groq AI": {
    "main": [[{"node": "Parse AI Response", "type": "main", "index": 0}]]
  },
  "Parse AI Response": {
    "main": [[{"node": "Save User Msg", "type": "main", "index": 0}]]
  },
  "Save User Msg": {
    "main": [[{"node": "Save AI Reply", "type": "main", "index": 0}]]
  },
  "Save AI Reply": {
    "main": [[{"node": "Send Reply", "type": "main", "index": 0}]]
  },
  "Send Reply": {
    "main": [[{"node": "Is Quote", "type": "main", "index": 0}]]
  },
  "Is Quote": {
    "main": [
      [{"node": "Generate Quote", "type": "main", "index": 0}],   # true → quote
      [{"node": "Respond OK", "type": "main", "index": 0}]        # false → done
    ]
  },
  "Generate Quote": {
    "main": [[{"node": "Send Document", "type": "main", "index": 0}]]
  },
  "Send Document": {
    "main": [[{"node": "Respond Quote OK", "type": "main", "index": 0}]]
  }
}

workflow = {
  "name": "CS-AI Lite",
  "nodes": nodes,
  "connections": connections,
  "active": False,
  "settings": {
    "executionOrder": "v1"
  },
  "tags": []
}

output_path = "${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"Workflow saved to: {output_path}")
print(f"Total nodes: {len(nodes)}")
