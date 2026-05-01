import { useState, useRef, useEffect } from "react";
import { api } from "../api";

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! I'm LedgerLink Assistant. Ask me about your expenses and invoices!" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);

    try {
      const data = await api.chatbotQuery(userMsg);
      setMessages((prev) => [...prev, { role: "bot", text: data.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "Sorry, I couldn't process that request." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button 
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        💬
      </button>

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
          <h3>LedgerLink Assistant</h3>
          <button onClick={() => setIsOpen(false)}>×</button>
        </div>
        <div className="chatbot-messages">
          {messages.map((m, i) => (
            <div key={i} className={`chatbot-message chatbot-${m.role}`}>
              {m.text}
            </div>
          ))}
          {loading && (
            <div className="chatbot-message chatbot-bot">Typing...</div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className="chatbot-input" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Ask about your finances..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            Send
          </button>
        </form>
        </div>
      )}
    </>
  );
}
