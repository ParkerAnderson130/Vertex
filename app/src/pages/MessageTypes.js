import React, { useState } from "react";

// User message component
export function UserMessage({ text }) {
  return (
    <div className="message user">
      <p>{text}</p>
    </div>
  );
}

// Assistant message component
export function AssistantMessage({ text, cypher, dbResults }) {
  const [showCypher, setShowCypher] = useState(false);

  return (
    <>
      <div className="message assistant">
        <p>{text}</p>
      </div>
      {cypher && (
        <div className="chain">
          <button
            onClick={() => setShowCypher(!showCypher)}
            className="chain-toggle"
          >
            <i>{showCypher ? "Hide chain of thought" : "Show chain of thought"}</i>
          </button>

          {showCypher && (
            <p className="chain-content">{cypher}</p>
          )}
        </div>
      )}
    </>
  );
}
