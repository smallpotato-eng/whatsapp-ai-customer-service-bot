import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# 1. Replace Load SOP node (Read/Write Files from Disk -> HTTP Request to Flask)
new_load_sop = {
    "id": "univ-load-sop",
    "name": "Load SOP",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [900, 300],
    "parameters": {
        "method": "GET",
        "url": "http://127.0.0.1:5050/sop?path=${N8N_FILES_DIR}/SOP.txt",
        "options": {}
    }
}

# 2. Replace Parse SOP node (Code -> simple Code that extracts from Flask response)
new_parse_sop = {
    "id": "univ-parse-sop",
    "name": "Parse SOP",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1120, 300],
    "parameters": {
        "jsCode": """const resp = $input.first().json;
if (!resp.ok) throw new Error('Failed to load SOP: ' + resp.error);
const sop = resp.sop;
return [{ json: sop }];"""
    }
}

# 3. Update Build Messages code to use correct references
new_build_messages_code = """const sop = $('Parse SOP').item.json;
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
4. If a customer asks for discounts or services not in the <SOP>, refuse politely. Do not repeat the same refusal phrase every time.
5. When you have enough info to generate a quote, append EXACTLY: [QUOTE:{json_data}][INTENT:QUOTE]
6. Otherwise append ONE tag only: [INTENT:FAQ] or [INTENT:APPOINTMENT] or [INTENT:OTHER]`;

const messages = [{ role: 'system', content: systemPrompt }];
for (const h of history) {
  messages.push({ role: h.role, content: h.content });
}
messages.push({ role: 'user', content: userText });

return [{ json: { phone, messages, userText } }];"""

# Also update Send Welcome to use sop welcome_message
new_send_welcome_body = "={{ JSON.stringify({ number: $('Extract Message').item.json.phone, text: $('Parse SOP').item.json.welcome_message || 'Hi! How can I help you today?' }) }}"

updated = {"load_sop": False, "parse_sop": False, "build_messages": False, "send_welcome": False}

for i, n in enumerate(wf['nodes']):
    if n['id'] == 'univ-load-sop':
        wf['nodes'][i] = new_load_sop
        updated['load_sop'] = True

    if n['id'] == 'univ-parse-sop':
        wf['nodes'][i] = new_parse_sop
        updated['parse_sop'] = True

    if n['id'] == 'univ-build-messages':
        n['parameters']['jsCode'] = new_build_messages_code
        updated['build_messages'] = True

    if n['id'] == 'univ-send-welcome':
        n['parameters']['body'] = new_send_welcome_body
        updated['send_welcome'] = True

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

for k, v in updated.items():
    print(f'{k}: {"OK" if v else "NOT FOUND"}')
print('Done.')
