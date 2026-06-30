import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

new_parse_ai_code = """const aiResp  = $input.first().json;
const content  = aiResp.choices?.[0]?.message?.content || '';
const phone    = $('Build Messages').item.json.phone;
const userText = $('Build Messages').item.json.userText;

// Extract INTENT
const intentMatch = content.match(/\\[INTENT:([A-Z_]+)\\]/);
const intent = intentMatch ? intentMatch[1] : 'OTHER';

// Extract QUOTE JSON - find from [QUOTE: to ][INTENT:
let quoteData = {};
const quoteStart = content.indexOf('[QUOTE:');
const intentIdx  = content.indexOf('][INTENT:');
if (quoteStart !== -1 && intentIdx !== -1) {
  const jsonStr = content.substring(quoteStart + 7, intentIdx);
  try { quoteData = JSON.parse(jsonStr); } catch(e) {}
}

// Clean reply text - remove everything from [QUOTE: onward
let replyText = quoteStart !== -1 ? content.substring(0, quoteStart) : content;
replyText = replyText.replace(/\\[INTENT:[A-Z_]+\\]/g, '').trim();

// Fallback if reply is empty (AI only sent the QUOTE tag)
if (!replyText && intent === 'QUOTE') {
  replyText = '📄 Your personalised quotation is ready! Please check the PDF below.';
}
if (!replyText) {
  replyText = 'Thank you for your message!';
}

return [{ json: { phone, intent, replyText, quoteData, userText } }];"""

for node in wf['nodes']:
    if node['id'] == 'univ-parse-ai':
        node['parameters']['jsCode'] = new_parse_ai_code
        print('✅ Parse AI Response updated')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
