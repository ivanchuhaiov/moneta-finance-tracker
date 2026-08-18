import client from './client'

export async function getAiSummary(currency, date_from, date_to) {
  const { data } = await client.get('/api/ai/summary', { params: { currency, date_from, date_to } })
  return data
}

export async function suggestCategory({ description, operation_code }) {
  const { data } = await client.post('/api/ai/categorize/suggest', { description, operation_code })
  return data
}

export async function sendChatMessage({ conversation_id, message }, currency) {
  const { data } = await client.post('/api/ai/chat', { conversation_id, message }, { params: { currency } })
  return data
}

export async function getChatMessages(conversationId) {
  const { data } = await client.get(`/api/ai/chat/${conversationId}/messages`)
  return data
}