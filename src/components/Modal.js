import React from 'react';

const Modal = ({ isOpen, news, onClose }) => {
  if (!isOpen || !news) return null;

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <img src={news.image} alt={news.title} className="modal-image" />
        <h2 className="modal-title">{news.title}</h2>
        <div className="modal-date">{news.date}</div>
        <p className="modal-text">{news.text}</p>
        <div className="modal-footer">
          <span className="modal-category">{news.category}</span>
          <button onClick={onClose}>
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;