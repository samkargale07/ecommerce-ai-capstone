"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { askAgent } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTED_QUESTIONS = [
  "What's good for a home gym?",
  "Compare two random products for me",
  "How well does beleza_saude sell?",
];

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm the Mercado shopping assistant. I can search the catalog, compare products, check category sales, and recommend items — ask me anything.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isOpen]);

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await askAgent(text);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer }]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong reaching the assistant. Is the backend running on port 8000?",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-105"
        style={{
          width: 56,
          height: 56,
          background: "var(--primary)",
          color: "white",
        }}
        aria-label={isOpen ? "Close chat" : "Open shopping assistant"}
      >
        {isOpen ? (
          <span className="text-2xl leading-none">×</span>
        ) : (
          <span className="text-xl">💬</span>
        )}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-6 z-50 flex flex-col rounded-xl shadow-2xl border overflow-hidden"
          style={{
            width: 380,
            maxWidth: "calc(100vw - 3rem)",
            height: 520,
            maxHeight: "calc(100vh - 8rem)",
            background: "white",
            borderColor: "var(--sand-line)",
          }}
        >
          {/* Header */}
          <div
            className="px-4 py-3 flex items-center justify-between"
            style={{ background: "var(--primary)", color: "white" }}
          >
            <div>
              <p className="font-display text-lg font-semibold leading-tight">Shopping Assistant</p>
              <p className="text-xs opacity-80">Agentic AI · Day 9</p>
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed ${
                  msg.role === "user" ? "ml-auto whitespace-pre-wrap" : ""
                }`}
                style={
                  msg.role === "user"
                    ? { background: "var(--primary)", color: "white" }
                    : { background: "var(--sand)", color: "var(--ink)" }
                }
              >
                {msg.role === "assistant" ? (
                  <div className="markdown-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
            ))}

            {isLoading && (
              <div
                className="max-w-[85%] rounded-lg px-3 py-2 text-sm"
                style={{ background: "var(--sand)", color: "var(--ink-soft)" }}
              >
                Thinking…
              </div>
            )}

            {messages.length === 1 && !isLoading && (
              <div className="pt-2 space-y-2">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="block w-full text-left text-xs px-3 py-2 rounded-lg border transition hover:shadow-sm"
                    style={{ borderColor: "var(--sand-line)", color: "var(--primary-dark)" }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="flex items-center gap-2 p-3 border-t"
            style={{ borderColor: "var(--sand-line)" }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products, deals, comparisons…"
              className="flex-1 text-sm px-3 py-2 rounded-lg border outline-none"
              style={{ borderColor: "var(--sand-line)" }}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="text-sm px-3 py-2 rounded-lg font-medium disabled:opacity-40"
              style={{ background: "var(--accent)", color: "white" }}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
