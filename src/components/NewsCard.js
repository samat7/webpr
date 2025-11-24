import React from 'react';

const NewsCard = ({ news, onCardClick }) => {
  return (
    <div className="news-card" onClick={() => onCardClick(news)}>
      <img src={news.image} alt={news.title} className="news-image" />
      <div className="news-content">
        <h3 className="news-title">{news.title}</h3>
        <div className="news-date">{news.date}</div>
        <p className="news-summary">{news.text.slice(0, 100)}...</p>
        <span className="news-category">{news.category}</span>
      </div>
    </div>
  );
};

export default NewsCard;