import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ currentStep, totalSteps, currentDescription }) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="progress-container">
      <div className="progress-bar" style={{ width: `${progress}%` }}></div>
      <div className="progress-info">
        <span>Step {currentStep} of {totalSteps}</span>
        <span className="progress-description">{currentDescription}</span>
      </div>
    </div>
  );
};

export default ProgressBar;
