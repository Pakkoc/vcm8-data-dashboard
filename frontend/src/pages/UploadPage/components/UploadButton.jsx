import Button from '../../../components/common/Button';

const UploadButton = ({ disabled, loading, onClick }) => {
  return (
    <div className="mt-6">
      <Button
        onClick={onClick}
        disabled={disabled}
        loading={loading}
        variant="primary"
        className="w-full py-3"
      >
        {loading ? '업로드 중...' : '업로드'}
      </Button>
    </div>
  );
};

export default UploadButton;
