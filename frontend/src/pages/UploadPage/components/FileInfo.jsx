import { FiFile, FiX } from 'react-icons/fi';

const FileInfo = ({ file, onReset }) => {
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg flex items-center justify-between">
      <div className="flex items-center gap-3">
        <FiFile className="text-2xl text-blue-600" />
        <div>
          <p className="font-medium text-gray-900">{file.name}</p>
          <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
        </div>
      </div>
      <button
        onClick={onReset}
        className="p-2 hover:bg-gray-200 rounded-full transition-colors"
        title="파일 선택 취소"
      >
        <FiX className="text-xl text-gray-600" />
      </button>
    </div>
  );
};

export default FileInfo;
