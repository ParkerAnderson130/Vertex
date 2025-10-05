import React, { useRef, useEffect } from "react";
import Modal from "react-modal";
import ForceGraph2D from "react-force-graph-2d";
import "./styles/Chat.scss"

Modal.setAppElement("#root");

export default function GraphModal({ isOpen, onClose, graphData, onNodeClick, onLinkClick }) {
  const fgRef = useRef();

  const safeGraphData = {
    nodes: graphData?.nodes || [],
    links: graphData?.edges || [],
  };

  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force("charge").strength(-200);
    }
  }, [safeGraphData]);

  return (
    <Modal
      contentLabel="Graph Modal"
      isOpen={isOpen}
      onRequestClose={onClose}

      style={{
        content: {
          backgroundColor: "#FCFCFC",
          border: "none",
          outline: "none",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "50%",
          height: "75%",
          padding: "1rem 2rem",
        },
      }}
    >
      <div className="graph-nav">
        <h2>Graph Visualization</h2>
        <button onClick={onClose} style={{ float: "right" }}>X</button>
      </div>

      {safeGraphData.nodes.length === 0 && safeGraphData.links.length === 0 ? (
        <p>No graph data available.</p>
      ) : (
        <ForceGraph2D
          linkDirectionalArrowLength={5}
          linkDirectionalArrowRelPos={1}
          linkLabel={(link) => link.relationship}
          graphData={safeGraphData}
          nodeLabel={node => node.name || node.label}
          nodeAutoColorBy="id"
          onNodeClick={onNodeClick}
          onLinkClick={onLinkClick}
          ref={fgRef}

          width={fgRef.current?.clientWidth || 750}
          height={fgRef.current?.clientHeight || 500}
        />
      )}
    </Modal>
  );
}
