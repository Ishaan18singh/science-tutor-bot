import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import "./App.css";

const API_URL = "http://localhost:8000/api/chat";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      // Build chat history for multi-turn memory (exclude sources, keep last 6 messages)
      const history = newMessages
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await axios.post(API_URL, {
        question: userMessage.content,
        chat_history: history.slice(0, -1), // exclude the current question
      });

      const botMessage = {
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources,
      };

      setMessages([...newMessages, botMessage]);
    } catch (err) {
      const errorMessage = {
        role: "assistant",
        content: "⚠️ Something went wrong connecting to the tutor. Please check the backend server.",
        sources: [],
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <span className="header-icon">🔬</span>
        <span className="header-title">Science Tutor</span>
      </header>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state">
            Ask anything from your Class 11/12 Physics, Chemistry,
            Mathematics, or Biology syllabus.
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">
              <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                {msg.content}
              </ReactMarkdown>

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  📎 {msg.sources[0].subject} / {msg.sources[0].class} /{" "}
                  {msg.sources[0].chapter.replace(/_/g, " ")}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble typing">Thinking...</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything from Class 11/12 Science..."
          rows={1}
        />
        <button onClick={sendMessage} disabled={loading}>
          ➤
        </button>
      </div>
    </div>
  );
}

export default App;