import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../pages/styles/Landing.scss';

const Landing = () => {
  const navigate = useNavigate(); 

  const handleStartChat = () => {
    navigate('/chat');
  };

  return (
    <div className="landing-wrapper">
      <section className="hero">
        
        <div className="hero-content">
          <div className="left-section">
            <div className="vertex-logo">Vertex</div>
            <p className="subtitle">
              Access comprehensive space research, publications, and mission data through 
              intelligent conversation. Your gateway to NASA's knowledge base.
            </p>
            <button onClick={handleStartChat} className="cta-button">
              Launch Assistant
            </button>
          </div>

          <div className="right-section">
            <div className="orbit-container">
              <div className="orbit orbit-1">
                <div className="planet planet-1"></div>
              </div>
              <div className="orbit orbit-2">
                <div className="planet planet-2"></div>
              </div>
              <div className="orbit orbit-3">
                <div className="planet planet-3"></div>
              </div>
              <div className="center-star"></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;