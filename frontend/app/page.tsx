"use client";

import { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "ai";
  content: string;
  route?: string;
  sources?: string[];
  requiresApproval?: boolean;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => "session_" + Math.random().toString(36).substring(7));
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    console.log("🚀 React is loaded and ready!"); // If you don't see this in F12 console, React is broken.
  }, [messages]);

  // Notice we removed the 'e: React.FormEvent' because we aren't using a form anymore
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput(""); 
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      console.log("📡 Sending to FastAPI..."); 
      
      const response = await fetch("http://127.0.0.1:8000/api/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      console.log("✅ Received:", data); 

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: data.answer,
          route: data.route_taken,
          sources: data.sources,
          requiresApproval: data.requires_approval,
        },
      ]);
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "Error connecting to backend. Check F12 Console." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle pressing the "Enter" key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Stop enter from doing anything weird
      sendMessage();
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-gray-100 p-4 md:p-10">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-xl overflow-hidden flex flex-col h-[85vh]">
        
        <div className="bg-blue-600 p-6 text-white">
          <h1 className="text-2xl font-bold">AI Operations Hub</h1>
          <p className="text-blue-100 text-sm">Multi-Agent System (Session: {sessionId})</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>Ask a question about policies, sales, or escalations!</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === "user" ? "bg-blue-600 text-white rounded-br-none" : "bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm"
              }`}>
                
                {msg.role === "ai" && (
                  <div className="flex gap-2 mb-2">
                    <span className="text-xs font-bold px-2 py-1 bg-gray-100 text-gray-600 rounded-full uppercase">
                      Route: {msg.route}
                    </span>
                    {msg.requiresApproval && (
                      <span className="text-xs font-bold px-2 py-1 bg-red-100 text-red-600 rounded-full uppercase">
                        Requires Approval
                      </span>
                    )}
                  </div>
                )}

                <p className="whitespace-pre-wrap">{msg.content}</p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 font-semibold">Sources:</p>
                    <ul className="text-xs text-gray-400 list-disc list-inside">
                      {msg.sources.map((src, i) => <li key={i}>{src}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl p-4 rounded-bl-none shadow-sm text-gray-500">
                AI is thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* NO MORE FORM TAG. JUST A DIV. */}
        <div className="p-4 bg-white border-t border-gray-200 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
          >
            Send
          </button>
        </div>

      </div>
    </main>
  );
}