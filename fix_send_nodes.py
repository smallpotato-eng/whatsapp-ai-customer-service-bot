import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for node in wf['nodes']:
    nid = node.get('id')

    if nid == 'univ-send-reset':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone: $('Extract Message').item.json.phone, text: '對話已重置，請重新開始 😊' }) }}"
        print('✅ Send Reset fixed')

    if nid == 'univ-send-welcome':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone: $('Extract Message').item.json.phone, text: $('Parse SOP').item.json.welcome_message || 'Hi! How can I help you today?' }) }}"
        print('✅ Send Welcome fixed')

    if nid == 'univ-send-reply':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone: $('Parse AI Response').item.json.phone, text: $('Parse AI Response').item.json.replyText }) }}"
        print('✅ Send Reply fixed')

    if nid == 'univ-send-doc':
        node['parameters']['contentType'] = 'raw'
        node['parameters']['rawContentType'] = 'application/json'
        node['parameters']['body'] = "={{ JSON.stringify({ phone: $('Parse AI Response').item.json.phone, base64: $json.base64, filename: $json.filename }) }}"
        print('✅ Send Document fixed')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
