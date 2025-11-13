import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { departmentAPI, collegeAPI } from '../api/crudAPI';

const DepartmentPage = () => {
  const [departments, setDepartments] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState(null);
  const [formData, setFormData] = useState({ name: '', college: '' });

  // 데이터 로드
  const fetchData = async () => {
    try {
      setLoading(true);
      const [departmentsData, collegesData] = await Promise.all([
        departmentAPI.getAll(),
        collegeAPI.getAll(),
      ]);
      setDepartments(departmentsData);
      setColleges(collegesData);
      setError(null);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // 모달 열기 (생성)
  const handleCreate = () => {
    setEditingDepartment(null);
    setFormData({ name: '', college: '' });
    setIsModalOpen(true);
  };

  // 모달 열기 (수정)
  const handleEdit = (department) => {
    setEditingDepartment(department);
    setFormData({
      name: department.name,
      college: department.college,
    });
    setIsModalOpen(true);
  };

  // 모달 닫기
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingDepartment(null);
    setFormData({ name: '', college: '' });
  };

  // 저장
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.college) {
      alert('모든 필드를 입력하세요.');
      return;
    }

    try {
      if (editingDepartment) {
        await departmentAPI.update(editingDepartment.id, formData);
      } else {
        await departmentAPI.create(formData);
      }
      fetchData();
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
      await departmentAPI.delete(id);
      fetchData();
    } catch (err) {
      alert('삭제에 실패했습니다. 하위 데이터가 있는지 확인하세요.');
      console.error(err);
    }
  };

  if (loading) return <MainLayout><LoadingSpinner /></MainLayout>;
  if (error) return <MainLayout><ErrorMessage message={error} /></MainLayout>;

  return (
    <MainLayout>
      <div className="page-container">
        <div className="page-header">
          <h1>학과 관리</h1>
          <Button onClick={handleCreate}>+ 새 학과</Button>
        </div>

        {departments.length === 0 ? (
          <EmptyState message="등록된 학과가 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>단과대학</th>
                  <th>학과명</th>
                  <th>등록일</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((dept) => (
                  <tr key={dept.id}>
                    <td>{dept.id}</td>
                    <td>{dept.college_name}</td>
                    <td>{dept.name}</td>
                    <td>{new Date(dept.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn-edit"
                          onClick={() => handleEdit(dept)}
                        >
                          수정
                        </button>
                        <button
                          className="btn-delete"
                          onClick={() => handleDelete(dept.id)}
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
          title={editingDepartment ? '학과 수정' : '새 학과'}
        >
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="college">단과대학</label>
              <select
                id="college"
                value={formData.college}
                onChange={(e) =>
                  setFormData({ ...formData, college: e.target.value })
                }
                required
              >
                <option value="">선택하세요</option>
                {colleges.map((college) => (
                  <option key={college.id} value={college.id}>
                    {college.name}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="학과명"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="예: 컴퓨터공학과"
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

          .form-group {
            margin-bottom: 1rem;
          }

          .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
          }

          .form-group select {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-size: 1rem;
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

export default DepartmentPage;
