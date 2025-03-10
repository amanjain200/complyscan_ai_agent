const BASE_URL = import.meta.env.VITE_API_URL;

async function createChat() {
  const res = await fetch(BASE_URL + '/chats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  const data = await res.json();
  
  if (!res.ok) {
    return Promise.reject({ status: res.status, data });
  }
  return data;
}

async function sendChatMessage(chatId, message) {
  const res = await fetch(BASE_URL + `/chats/${chatId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });

  const data = await res.json(); // Extract response JSON

  if (!res.ok) {
    return Promise.reject({ status: res.status, data });
  }
  return data; // Return parsed response JSON
}

export default {
  createChat,
  sendChatMessage
};
