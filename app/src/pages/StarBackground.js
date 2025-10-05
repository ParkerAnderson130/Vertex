import React, { useEffect } from 'react';

const StarBackground = ({ numStars = 150 }) => {
  useEffect(() => {
    const starsContainer = document.getElementById('stars');
    if (!starsContainer) return;

    for (let i = 0; i < numStars; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      star.style.left = Math.random() * 100 + '%';
      star.style.top = Math.random() * 100 + '%';
      star.style.animationDelay = Math.random() * 3 + 's';
      starsContainer.appendChild(star);
    }

    return () => {
      starsContainer.innerHTML = '';
    };
  }, [numStars]);

  return <div id="stars" className="stars-container"></div>;
};

export default StarBackground;
