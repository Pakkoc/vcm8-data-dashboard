import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { collegeAPI } from '../api/crudAPI';

const CollegePage = () => {
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCollege, setEditingCollege] = useState(null);
  const [formData, setFormData] = useState({ name: '' });

  // 데이터 로드
  const fetchColleges = async () => {
    try {
      setLoading(true);
      const data = await collegeAPI.getAll();
      setColleges(data);
      setError(null);
    } catch (err) {
      setError('단과대학 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchColleges();
  }, []);

  // 모달 열기 (생성)
  const handleCreate = () => {
    setEditingCollege(null);
    setFormData({ name: '' });
    setIsModalOpen(true);
  };

  // 모달 열기 (수정)
  const handleEdit = (college) => {
    setEditingCollege(college);
    setFormData({ name: college.name });
    setIsModalOpen(true);
  };

  // 모달 닫기
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCollege(null);
    setFormData({ name: '' });
  };

  // 저장
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('단과대학 이름을 입력하세요.');
      return;
    }

    try {
      if (editingCollege) {
        await collegeAPI.update(editingCollege.id, formData);
      } else {
        await collegeAPI.create(formData);
      }
      fetchColleges();
      handleCloseModal();
    } catch (err) {
      alert('저장에 실패했습니다.');
      console.error(err);
    }
  };

  // 삭제
  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await collegeAPI.delete(id);
      fetchColleges();
    } catch (err) {
      alert('삭제에 실패했습니다. 하위 학과가 있는지 확인하세요.');
      console.error(err);
    }
  };

  if (loading) return <MainLayout><LoadingSpinner /></MainLayout>;
  if (error) return <MainLayout><ErrorMessage message={error} /></MainLayout>;

  return (
    <MainLayout>
      <div className="page-container">
        <div className="page-header">
          <h1>단과대학 관리</h1>
          <Button onClick={handleCreate}>+ 새 단과대학</Button>
        </div>

        {colleges.length === 0 ? (
          <EmptyState message="등록된 단과대학이 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>이름</th>
                  <th>등록일</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {colleges.map((college) => (
                  <tr key={college.id}>
                    <td>{college.id}</td>
                    <td>{college.name}</td>
                    <td>{new Date(college.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn-edit"
                          onClick={() => handleEdit(college)}
                        >
                          수정
                        </button>
                        <button
                          className="btn-delete"
                          onClick={() => handleDelete(college.id)}
                        >
                          삭제
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title={editingCollege ? '단과대학 수정' : '새 단과대학'}
        >
          <form onSubmit={handleSubmit}>
            <Input
              label="단과대학 이름"
              value={formData.name}
              onChange={(e) => setFormData({ name: e.target.value })}
              placeholder="예: 공과대학"
              required
            />
            <div className="modal-actions">
              <Button type="button" onClick={handleCloseModal} variant="secondary">
                취소
              </Button>
              <Button type="submit">저장</Button>
            </div>
          </form>
        </Modal>

        <style jsx>{`
          .page-container {
            padding: 2rem;
          }

          .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
          }

          .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
          }

          .table-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
          }

          .data-table {
            width: 100%;
            border-collapse: collapse;
          }

          .data-table thead {
            background-color: #f9fafb;
          }

          .data-table th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
          }

          .data-table td {
            padding: 1rem;
            border-bottom: 1px solid #e5e7eb;
          }

          .data-table tbody tr:hover {
            background-color: #f9fafb;
          }

          .action-buttons {
            display: flex;
            gap: 0.5rem;
          }

          .btn-edit,
          .btn-delete {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
          }

          .btn-edit {
            background-color: #3b82f6;
            color: white;
          }

          .btn-edit:hover {
            background-color: #2563eb;
          }

          .btn-delete {
            background-color: #ef4444;
            color: white;
          }

          .btn-delete:hover {
            background-color: #dc2626;
          }

          .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            margin-top: 1.5rem;
          }
        `}</style>
      </div>
    </MainLayout>
  );
};

export default CollegePage;
