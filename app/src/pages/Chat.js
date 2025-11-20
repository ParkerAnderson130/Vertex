import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { UserMessage, AssistantMessage } from "./MessageTypes.js";
import GraphModal from "./GraphModal.js"
import "./styles/Chat.scss";

export default function Chat() {
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });

  const navigate = useNavigate(); // Initialize navigate
  const inputRef = useRef();

  const openGraph = () => {
    setModalOpen(true);
  }

  const handleGraphItemClick = (item) => {
    setQuestion(item.name || item.label || item.relationship || "");
    inputRef.current?.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);

    const userMessage = { type: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      const assistantMessage = {
        type: "assistant",
        text: data.answer,
        cypher: data.cypher_query,
        dbResults: data.db_results,
      };
      console.log(data.graph)

      setMessages((prev) => [...prev, assistantMessage]);
      setGraphData(data.graph);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { type: "error", text: "Failed to fetch answer from API." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      {/* Home Button - Redirects to Landing */}
      <button className="home-button" onClick={() => navigate("/")} aria-label="Home">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" width="24px" height="24px">
          <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
          <path d="M0 0h24v24H0z" fill="none"/>
        </svg>
      </button>

      <div className="chat-container">
        
        <div className="header">
          <h2>Vertex</h2>
          <p>Lattice 1.0</p>
        </div>
        
        <div className="chat-window">
          {messages.map((msg, idx) => {
            if (msg.type === "user") return <UserMessage key={idx} text={msg.text} />;
            if (msg.type === "assistant")
              return (
                <AssistantMessage
                  key={idx}
                  text={msg.text}
                  cypher={msg.cypher}
                  dbResults={msg.dbResults}
                />
              );
            return <div key={idx} className="message error">{msg.text}</div>;
          })}
          {loading && (
            <div className="message loading">
              Lattice is typing<span className="dots"></span>
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            placeholder="What's on your mind?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
            <button
              type="button"
              className="graph-button"
              disabled={
                !graphData.nodes?.length && !graphData.edges?.length
              }
              onClick={openGraph}
            ></button>
          <button type="submit"></button>
        </form>

        <GraphModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          
          graphData={graphData}
          onNodeClick={handleGraphItemClick}
          onLinkClick={handleGraphItemClick}
        />
      </div>
    </section>
  );
}