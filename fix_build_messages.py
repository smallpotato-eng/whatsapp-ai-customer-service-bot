import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

new_build_messages_code = """const sop = $('Parse SOP').item.json;
const roleName    = sop.role_name      || 'Assistant';
const companyName = sop.company_name   || 'Our Company';
const tone        = sop.tone           || 'Professional and friendly';
const sopContent  = sop.sop_content    || 'Provide helpful customer service.';

const phone    = $('Extract Message').item.json.phone;
const userText = $('Extract Message').item.json.text;
const history  = $('Get History').item.json?.history || [];

const systemPrompt = `You are ${roleName}, a human customer service representative for ${companyName}.
Your personality and tone: ${tone}.

Here is your STRICT SOP:
<SOP>
${sopContent}
</SOP>

ABSOLUTE RULES — NEVER BREAK THESE:
1. You are a HUMAN staff member. NEVER say you are an AI, chatbot, or virtual assistant.
2. NEVER say "I cannot send PDF", "technical limitation", "I'm just a text-based assistant", or anything similar. These phrases are COMPLETELY FORBIDDEN.
3. When you generate a [QUOTE:...][INTENT:QUOTE] tag, our system automatically sends a professional PDF to the customer. You do NOT need to explain this. Just say something warm like "I've prepared your quotation! You'll receive it shortly. 😊"
4. Only answer based on the SOP above.
5. If customer asks for discounts or unavailable services, refuse politely with variety.
6. Reply in the SAME language the customer uses.
7. When you have enough info for a quote, write a warm closing sentence FIRST, then append EXACTLY:
[QUOTE:{json_data}][INTENT:QUOTE]
8. Otherwise append ONE tag: [INTENT:FAQ] or [INTENT:APPOINTMENT] or [INTENT:OTHER]`;

const messages = [{ role: 'system', content: systemPrompt }];
for (const h of history) {
  messages.push({ role: h.role, content: h.content });
}
messages.push({ role: 'user', content: userText });

return [{ json: { phone, messages, userText } }];"""

for node in wf['nodes']:
    if node['id'] == 'univ-build-messages':
        node['parameters']['jsCode'] = new_build_messages_code
        print('✅ Build Messages updated')

with open('${PROJECT_ROOT}/cs-ai/n8n-exports/cs-ai-lite-workflow.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Done.')
