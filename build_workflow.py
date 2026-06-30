import sqlite3, json
from datetime import datetime

workflow_id = "Ik4PiPSzowITrzvf"

nodes = [
  {
    "id": "webhook-node",
    "name": "WhatsApp Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [240, 300],
    "parameters": {
      "httpMethod": "POST",
      "path": "whatsapp-webhook",
      "responseMode": "responseNode",
      "options": {}
    }
  },
  {
    "id": "extract-node",
    "name": "Extract Message",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [460, 300],
    "parameters": {
      "jsCode": "const body = $input.first().json.body;\nconst msgs = body?.data?.messages || body?.messages || [];\nif (!msgs.length) return [];\nconst msg = msgs[0];\nconst phone = (msg.key?.remoteJid || '').replace('@s.whatsapp.net','').replace('@c.us','');\nconst text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';\nconst fromMe = msg.key?.fromMe || false;\nif (fromMe || !phone || !text) return [];\nreturn [{ json: { phone, text, instance: body.instance || 'cs-ai-demo 2' } }];"
    }
  },
  {
    "id": "get-session-node",
    "name": "Get Session",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [680, 300],
    "parameters": {
      "method": "GET",
      "url": "=http://localhost:5050/session/{{ $json.phone }}",
      "options": {}
    }
  },
  {
    "id": "route-session-node",
    "name": "New or Existing",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [900, 300],
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
  {
    "id": "send-menu-msg-node",
    "name": "Send Menu",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1120, 160],
    "parameters": {
      "method": "POST",
      "url": "http://192.168.0.10:8080/message/sendText/cs-ai-demo%202",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $('Extract Message').item.json.phone, text: '\\u6b61\\u8fce\\uff01\\u8acb\\u9078\\u64c7\\u670d\\u52d9\\uff1a\\n1\\ufe0f\\u20e3 \\u7f8e\\u5bb9\\u9662 (Bella Beauty)\\n2\\ufe0f\\u20e3 \\u4ea4\\u6613\\u6240 (Alex Exchange)\\n3\\ufe0f\\u20e3 \\u4fdd\\u96aa (Sarah Insurance)\\n4\\ufe0f\\u20e3 \\u5730\\u7522 (Kevin Realty)\\n5\\ufe0f\\u20e3 \\u7db2\\u8cfc (Mia Shop)\\n\\n\\u8acb\\u56de\\u8986\\u6578\\u5b57 1-5' }) }}",
      "options": {}
    }
  },
  {
    "id": "check-selection-node",
    "name": "Select Business",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [1120, 420],
    "parameters": {
      "conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
        "conditions": [
          {
            "leftValue": "={{ $('Extract Message').item.json.text.trim() }}",
            "rightValue": "^[1-5]$",
            "operator": {"type": "string", "operation": "regex"}
          }
        ],
        "combinator": "and"
      },
      "options": {}
    }
  },
  {
    "id": "set-business-node",
    "name": "Set Business Type",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1340, 360],
    "parameters": {
      "jsCode": "const text = $('Extract Message').item.json.text.trim();\nconst map = {'1':'beauty','2':'exchange','3':'insurance','4':'realestate','5':'shop'};\nconst business = map[text] || 'beauty';\nreturn [{ json: { phone: $('Extract Message').item.json.phone, business_type: business, text: $('Extract Message').item.json.text } }];"
    }
  },
  {
    "id": "save-session-node",
    "name": "Save Session",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1560, 360],
    "parameters": {
      "method": "POST",
      "url": "http://localhost:5050/session",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ phone_number: $json.phone, business_type: $json.business_type, status: 'active' }) }}",
      "options": {}
    }
  },
  {
    "id": "invalid-reply-node",
    "name": "Invalid Reply",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1340, 560],
    "parameters": {
      "method": "POST",
      "url": "http://192.168.0.10:8080/message/sendText/cs-ai-demo%202",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $('Extract Message').item.json.phone, text: '\\u8acb\\u56de\\u8986\\u6578\\u5b57 1-5 \\u9078\\u64c7\\u670d\\u52d9 \\ud83d\\ude0a' }) }}",
      "options": {}
    }
  },
  {
    "id": "get-prompt-node",
    "name": "Load Prompt",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1780, 360],
    "parameters": {
      "jsCode": "let business = 'beauty';\nlet phone = '';\ntry {\n  const s = $('Set Business Type').item.json;\n  business = s.business_type;\n  phone = s.phone;\n} catch(e) {\n  try {\n    const s = $('Get Session').item.json;\n    business = s.business_type || 'beauty';\n    phone = $('Extract Message').item.json.phone;\n  } catch(e2) {}\n}\nconst prompts = {\n  beauty: 'You are Bella, a friendly beauty salon assistant at Bella Beauty. Help with appointments, services, pricing. Tag: [INTENT:FAQ] [INTENT:APPOINTMENT] [INTENT:OTHER]. Respond in customer language.',\n  exchange: 'You are Alex, a trading exchange support agent. Help with account FAQ, trading pairs, fees. Do NOT give investment advice. Tag: [INTENT:FAQ] [INTENT:OTHER].',\n  insurance: 'You are Sarah, an insurance advisor at SecureLife. Help with policies, claims, quotes, appointments. For quotes ask: age, coverage type, budget. Tag: [INTENT:FAQ] [INTENT:APPOINTMENT] [INTENT:QUOTE] [INTENT:OTHER].',\n  realestate: 'You are Kevin, a real estate agent at PrimeHome Realty. Help with listings, viewings, cost estimates. For viewings ask: date, time, property type. Tag: [INTENT:FAQ] [INTENT:APPOINTMENT] [INTENT:QUOTE] [INTENT:OTHER].',\n  shop: 'You are Mia, a cheerful shop assistant at MiaMart. Help with products, orders, tracking, shipping quotes. For orders ask: items, quantities, address. Tag: [INTENT:FAQ] [INTENT:ORDER] [INTENT:TRACK] [INTENT:QUOTE] [INTENT:OTHER].'\n};\nreturn [{ json: { phone, business, systemPrompt: prompts[business]||prompts.beauty, userText: $('Extract Message').item.json.text } }];"
    }
  },
  {
    "id": "ollama-node",
    "name": "Qwen AI",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2000, 360],
    "parameters": {
      "method": "POST",
      "url": "http://localhost:11434/api/chat",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ model: 'qwen2.5:7b', stream: false, messages: [{ role: 'system', content: $json.systemPrompt }, { role: 'user', content: $json.userText }] }) }}",
      "options": {"timeout": 60000}
    }
  },
  {
    "id": "parse-ai-node",
    "name": "Parse AI Response",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2220, 360],
    "parameters": {
      "jsCode": "const aiResp = $input.first().json;\nconst content = aiResp.message?.content || '';\nconst phone = $('Load Prompt').item.json.phone;\nconst business = $('Load Prompt').item.json.business;\nconst intentMatch = content.match(/\\[INTENT:([A-Z_]+)\\]/);\nconst intent = intentMatch ? intentMatch[1] : 'OTHER';\nconst replyText = content.replace(/\\[INTENT:[A-Z_]+\\]/g, '').trim();\nreturn [{ json: { phone, business, intent, replyText } }];"
    }
  },
  {
    "id": "save-conv-node",
    "name": "Save Conversation",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2440, 360],
    "parameters": {
      "method": "POST",
      "url": "http://localhost:5050/conversations",
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ phone_number: $json.phone, direction: 'inbound', message: $('Extract Message').item.json.text, intent: $json.intent, business_type: $json.business }) }}",
      "options": {}
    }
  },
  {
    "id": "send-reply-node",
    "name": "Send Reply",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2660, 360],
    "parameters": {
      "method": "POST",
      "url": "http://192.168.0.10:8080/message/sendText/cs-ai-demo%202",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [{"name": "apikey", "value": "changeme123"}]
      },
      "sendBody": True,
      "contentType": "json",
      "body": "={{ JSON.stringify({ number: $json.phone, text: $json.replyText }) }}",
      "options": {}
    }
  },
  {
    "id": "respond-ok-node",
    "name": "Respond OK",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [2880, 360],
    "parameters": {
      "respondWith": "json",
      "responseBody": "{\"ok\":true}",
      "options": {}
    }
  }
]

connections = {
  "WhatsApp Webhook": {
    "main": [[{"node": "Extract Message", "type": "main", "index": 0}]]
  },
  "Extract Message": {
    "main": [[{"node": "Get Session", "type": "main", "index": 0}]]
  },
  "Get Session": {
    "main": [[{"node": "New or Existing", "type": "main", "index": 0}]]
  },
  "New or Existing": {
    "main": [
      [{"node": "Send Menu", "type": "main", "index": 0}],
      [{"node": "Select Business", "type": "main", "index": 0}]
    ]
  },
  "Send Menu": {
    "main": [[{"node": "Respond OK", "type": "main", "index": 0}]]
  },
  "Select Business": {
    "main": [
      [{"node": "Set Business Type", "type": "main", "index": 0}],
      [{"node": "Invalid Reply", "type": "main", "index": 0}]
    ]
  },
  "Set Business Type": {
    "main": [[{"node": "Save Session", "type": "main", "index": 0}]]
  },
  "Save Session": {
    "main": [[{"node": "Load Prompt", "type": "main", "index": 0}]]
  },
  "Invalid Reply": {
    "main": [[{"node": "Respond OK", "type": "main", "index": 0}]]
  },
  "Load Prompt": {
    "main": [[{"node": "Qwen AI", "type": "main", "index": 0}]]
  },
  "Qwen AI": {
    "main": [[{"node": "Parse AI Response", "type": "main", "index": 0}]]
  },
  "Parse AI Response": {
    "main": [[{"node": "Save Conversation", "type": "main", "index": 0}]]
  },
  "Save Conversation": {
    "main": [[{"node": "Send Reply", "type": "main", "index": 0}]]
  },
  "Send Reply": {
    "main": [[{"node": "Respond OK", "type": "main", "index": 0}]]
  }
}

conn = sqlite3.connect('${N8N_HOME}/database.sqlite')
cur = conn.cursor()
cur.execute(
    'UPDATE workflow_entity SET nodes=?, connections=?, active=1, updatedAt=? WHERE id=?',
    (json.dumps(nodes), json.dumps(connections), datetime.now().isoformat(), workflow_id)
)
conn.commit()
print(f'Workflow updated: {cur.rowcount} row(s) affected')
conn.close()
