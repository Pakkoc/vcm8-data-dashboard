import { useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Button from '../components/common/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import useApi from '../hooks/useApi';
import { dataUploadAPI } from '../api/dataUploadAPI';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');
  const { loading, error, execute, reset } = useApi(dataUploadAPI.uploadMultipleFiles);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setSuccessMessage('');
    reset();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (files.length === 0) {
      return;
    }

    try {
      const result = await execute(files);
      setSuccessMessage(
        `${files.length}개 파일 업로드 성공!\n` +
        `학생: ${result.details.students}명, ` +
        `학과 KPI: ${result.details.department_kpis}개, ` +
        `논문: ${result.details.publications}개, ` +
        `연구 프로젝트: ${result.details.research_projects}개, ` +
        `프로젝트 지출: ${result.details.project_expenses}개`
      );
      setFiles([]);
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
                파일 선택 (Excel 또는 CSV) - 여러 파일 선택 가능
              </label>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                multiple
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>

            {files.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  선택된 파일 ({files.length}개):
                </p>
                <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                  {files.map((file, index) => (
                    <li key={index}>{file.name}</li>
                  ))}
                </ul>
              </div>
            )}

            {error && <ErrorMessage message={error} className="mb-4" />}

            {successMessage && (
              <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
                <p className="text-green-700 whitespace-pre-line">{successMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              loading={loading}
              disabled={files.length === 0 || loading}
              className="w-full"
            >
              {files.length > 1 ? `${files.length}개 파일 업로드` : '업로드'}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">업로드 가이드</h3>
            <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
              <li>Excel (.xlsx, .xls) 또는 CSV (.csv) 파일을 선택할 수 있습니다.</li>
              <li>여러 파일을 한 번에 선택하여 동시에 업로드할 수 있습니다.</li>
              <li>파일 크기는 각각 10MB를 초과할 수 없습니다.</li>
              <li>순서 상관없이 업로드 가능합니다.</li>
              <li>업로드 시 기존 데이터는 모두 삭제되고 새로운 데이터로 대체됩니다.</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default UploadPage;
