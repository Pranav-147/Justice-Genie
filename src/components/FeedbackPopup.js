import React, { useState } from 'react';
import './FeedbackPopup.css';

const FeedbackPopup = ({ isOpen, onClose, onSubmitFeedback }) => {
  const [feedback, setFeedback] = useState('');

  const handleFeedbackSubmit = () => {
    onSubmitFeedback(feedback);
    setFeedback('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="popupOverlay">
      <div className="popup">
        <h2>Submit Feedback</h2>
        <textarea
          className="feedbackInput"
          placeholder="Write your feedback here..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        <div className="popupActions">
          <button className="btn closeBtn" onClick={onClose}>Cancel</button>
          <button
            className="btn submitBtn"
            onClick={handleFeedbackSubmit}
            disabled={!feedback.trim()}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPopup;
