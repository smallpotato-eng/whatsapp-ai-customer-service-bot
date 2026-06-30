import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

updates = {
    # Extract Message: parse Baileys format { phone, text, name }
    'univ-extract': {
        'jsCode': """const body = $input.first().json.body;
const phone = body?.phone || '';
const text  = body?.text  || '';
const name  = body?.name  || phone;
if (!phone || !text) return [];
return [{ json: { phone, text, name } }];"""
    },

    # Send Reset: Baileys /send
    'univ-send-reset': {
        'url': 'http://127.0.0.1:3000/send',
        'body': "={{ JSON.stringify({ phone: $('Extract Message').item.json.phone, text: '對話已重置，請重新開始 😊' }) }}"
    },

    # Send Welcome: Baileys /send
    'univ-send-welcome': {
        'url': 'http://127.0.0.1:3000/send',
        'body': "={{ JSON.stringify({ phone: $('Extract Message').item.json.phone, text: $('Parse SOP').item.json.welcome_message || 'Hi! How can I help you today?' }) }}"
    },

    # Send Reply: Baileys /send
    'univ-send-reply': {
        'url': 'http://127.0.0.1:3000/send',
        'body': "={{ JSON.stringify({ phone: $('Parse AI Response').item.json.phone, text: $('Parse AI Response').item.json.replyText }) }}"
    },

    # Send Document: Baileys /send-document
    'univ-send-doc': {
        'url': 'http://127.0.0.1:3000/send-document',
        'body': "={{ JSON.stringify({ phone: $('Parse AI Response').item.json.phone, base64: $json.base64, filename: $json.filename }) }}"
    }
}

for node in wf['nodes']:
    nid = node.get('id')
    if nid not in updates:
        continue

    patch = updates[nid]

    if 'jsCode' in patch:
        node['parameters']['jsCode'] = patch['jsCode']

    if 'url' in patch:
        node['parameters']['url'] = patch['url']
        # Remove Evolution API headers
        node['parameters'].pop('sendHeaders', None)
        node['parameters'].pop('headerParameters', None)

    if 'body' in patch:
        node['parameters']['body'] = patch['body']
        node['parameters']['sendBody'] = True
        node['parameters']['contentType'] = 'json'
        node['parameters'].pop('rawContentType', None)

    print(f'✅ {node["name"]} updated')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
