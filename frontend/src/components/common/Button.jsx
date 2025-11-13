const Button = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  loading = false,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseStyles = 'px-4 py-2 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {loading ? '처리 중...' : children}
    </button>
  );
};

export default Button;
