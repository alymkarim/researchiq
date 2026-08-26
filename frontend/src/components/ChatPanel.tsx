import { FormEvent, useRef, useState } from "react";
import { LoaderCircle, MessageSquare, Send, Sparkles } from "lucide-react";
import { chatWithDocument } from "../api";
import type { ChatMessage } from "../types";

interface ChatPanelProps {
  documentId: number;
  documentTitle: string;
  hasAnalysis?: boolean;
}

// TODO: add streaming responses instead of waiting for full response
export function ChatPanel({ documentId, documentTitle, hasAnalysis = false }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  if (!hasAnalysis) {
    return (
      <section className="chat-panel">
        <div className="chat-header">
          <MessageSquare size={18} />
          <span>Chat with Paper</span>
        </div>
        <div className="feature-locked">
          <div className="feature-locked-icon">
            <MessageSquare size={40} />
          </div>
          <h3>Paper analysis required</h3>
          <p>To chat with this paper, you need to analyse it first.</p>
          <div className="feature-locked-steps">
            <span>1. Select a paper from the vault</span>
            <span>2. Click the <strong>Analyse</strong> button</span>
            <span>3. Wait for analysis to complete</span>
            <span>4. Then chat will be available</span>
          </div>
        </div>
      </section>
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const result = await chatWithDocument(question, documentId, messages);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      });
    }
  }

  return (
    <section className="chat-panel">
      <div className="chat-header">
        <MessageSquare size={18} />
        <span>Chat with Paper</span>
        <span className="chat-title">{documentTitle}</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <Sparkles size={32} />
            <p>Ask questions about this paper</p>
            <div className="chat-suggestions">
              {[
                "What is the main finding?",
                "What methodology was used?",
                "What are the limitations?",
              ].map((q) => (
                <button
                  key={q}
                  type="button"
                  className="chat-suggestion"
                  onClick={() => setInput(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div className="chat-bubble">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="chat-bubble loading">
              <LoaderCircle className="spin" size={16} />
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this paper..."
          disabled={loading}
        />
        <button type="submit" disabled={!input.trim() || loading}>
          <Send size={16} />
        </button>
      </form>
    </section>
  );
}
