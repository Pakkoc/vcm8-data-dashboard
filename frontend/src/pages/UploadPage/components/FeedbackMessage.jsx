import { FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import Button from '../../../components/common/Button';

const FeedbackMessage = ({ type, message, onNavigateToDashboard }) => {
  const isSuccess = type === 'success';

  return (
    <div
      className={`
        mt-6 p-4 rounded-lg border
        ${isSuccess
          ? 'bg-green-50 border-green-200'
          : 'bg-red-50 border-red-200'
        }
      `}
    >
      <div className="flex items-start gap-3">
        {isSuccess ? (
          <FiCheckCircle className="text-2xl text-green-600 flex-shrink-0" />
        ) : (
          <FiAlertCircle className="text-2xl text-red-600 flex-shrink-0" />
        )}

        <div className="flex-1">
          <p className={`font-medium ${isSuccess ? 'text-green-900' : 'text-red-900'}`}>
            {isSuccess ? '업로드 성공' : '업로드 실패'}
          </p>
          <p className={`text-sm mt-1 whitespace-pre-line ${isSuccess ? 'text-green-800' : 'text-red-800'}`}>
            {message}
          </p>

          {isSuccess && (
            <Button
              onClick={onNavigateToDashboard}
              variant="primary"
              className="mt-3"
            >
              대시보드에서 확인하기
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackMessage;
