const EmptyState = ({ message, icon, className = '' }) => {
  return (
    <div className={`text-center py-12 ${className}`}>
      {icon && <div className="text-4xl mb-4">{icon}</div>}
      <p className="text-gray-500">{message}</p>
    </div>
  );
};

export default EmptyState;
