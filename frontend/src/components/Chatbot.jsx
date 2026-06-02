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

  const quickReplies = [
    "Total expenses this month?",
    "Show pending invoices?",
    "Dashboard overview?",
    "What's my total revenue?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    if (!text.trim() || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: text.trim() }]);
    setInput("");
    setLoading(true);

    try {
      const data = await api.chatbotQuery(text.trim());
      setMessages((prev) => [...prev, { role: "bot", text: data.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "Sorry, I couldn't process that request." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend(input);
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
          {!loading && messages.length === 1 && (
            <div className="quick-replies" style={{ display: "flex", flexWrap: "wrap", gap: "8px", padding: "0 12px", marginBottom: "8px" }}>
              {quickReplies.map((reply, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(reply)}
                  style={{
                    padding: "8px 12px",
                    borderRadius: "20px",
                    border: "1px solid #6366f1",
                    background: "white",
                    color: "#6366f1",
                    fontSize: "14px",
                    cursor: "pointer"
                  }}
                >
                  {reply}
                </button>
              ))}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className="chatbot-input" onSubmit={handleSubmit}>
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
