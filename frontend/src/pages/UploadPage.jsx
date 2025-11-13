import { useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Button from '../components/common/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import useApi from '../hooks/useApi';
import { dataUploadAPI } from '../api/dataUploadAPI';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const { loading, error, execute, reset } = useApi(dataUploadAPI.uploadExcel);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setSuccessMessage('');
    reset();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      return;
    }

    try {
      const result = await execute(file);
      setSuccessMessage(`데이터 업로드 성공: ${JSON.stringify(result.details)}`);
      setFile(null);
      // 파일 입력 리셋
      e.target.reset();
    } catch (err) {
      // 에러는 useApi에서 처리됨
    }
  };

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">데이터 관리</h1>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">엑셀 파일 업로드</h2>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                파일 선택 (Excel 또는 CSV)
              </label>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>

            {file && (
              <p className="text-sm text-gray-600 mb-4">
                선택된 파일: {file.name}
              </p>
            )}

            {error && <ErrorMessage message={error} className="mb-4" />}

            {successMessage && (
              <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
                <p className="text-green-700">{successMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              loading={loading}
              disabled={!file || loading}
              className="w-full"
            >
              업로드
            </Button>
          </form>

          <div className="mt-6 p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">업로드 가이드</h3>
            <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
              <li>Excel (.xlsx, .xls) 또는 CSV (.csv) 파일만 업로드 가능합니다.</li>
              <li>파일 크기는 10MB를 초과할 수 없습니다.</li>
              <li>업로드 시 기존 데이터는 모두 삭제되고 새로운 데이터로 대체됩니다.</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default UploadPage;
