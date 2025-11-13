const ErrorMessage = ({ message, onRetry, className = '' }) => {
  return (
    <div className={`bg-red-50 border border-red-200 rounded p-4 text-center ${className}`}>
      <p className="text-red-700 mb-2">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-red-600 underline hover:text-red-800"
        >
          다시 시도
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
