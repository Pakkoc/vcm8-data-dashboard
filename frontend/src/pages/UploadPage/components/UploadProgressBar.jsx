const UploadProgressBar = ({ progress }) => {
  return (
    <div className="mt-4">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>데이터 처리 중...</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default UploadProgressBar;
