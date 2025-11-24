import React from 'react';

const Header = ({ onThemeToggle }) => {
  return (
    <header className="navbar-container">
      <h1>Новостной портал</h1>
      <button onClick={onThemeToggle}>
        Сменить тему
      </button>
    </header>
  );
};

export default Header;