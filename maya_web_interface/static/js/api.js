class ChatAPI {
    constructor() {
        this.baseUrl = '/api/chat';
    }

    async sendMessage(message, conversationId = null) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data: data.response,
                conversationId: data.conversation_id || conversationId
            };
        } catch (error) {
            console.error('Error sending message:', error);
            return {
                success: false,
                error: error.message || 'Failed to get response from the server'
            };
        }
    }

    // Add other API methods as needed
}

// Export as a singleton
const chatAPI = new ChatAPI();
export default chatAPI;
