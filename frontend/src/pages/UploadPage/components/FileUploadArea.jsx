import { useState } from 'react';
import { FiUpload } from 'react-icons/fi';

const FileUploadArea = ({ onFileSelect, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-lg p-12 text-center
        transition-colors cursor-pointer
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <FiUpload className="mx-auto text-4xl text-gray-400 mb-4" />

      <label className="cursor-pointer">
        <span className="text-blue-600 hover:underline">파일 선택</span>
        <span className="text-gray-600"> 또는 파일을 여기로 드래그하세요</span>
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />
      </label>
    </div>
  );
};

export default FileUploadArea;
