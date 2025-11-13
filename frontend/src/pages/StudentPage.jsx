import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { studentAPI, departmentAPI } from '../api/crudAPI';

const StudentPage = () => {
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [formData, setFormData] = useState({
    student_id_number: '',
    name: '',
    department: '',
    program_level: '학사',
    status: '재학',
    email: '',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [studentsData, departmentsData] = await Promise.all([
        studentAPI.getAll(),
        departmentAPI.getAll(),
      ]);
      setStudents(studentsData);
      setDepartments(departmentsData);
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

  const handleCreate = () => {
    setEditingStudent(null);
    setFormData({
      student_id_number: '',
      name: '',
      department: '',
      program_level: '학사',
      status: '재학',
      email: '',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (student) => {
    setEditingStudent(student);
    setFormData({
      student_id_number: student.student_id_number,
      name: student.name,
      department: student.department,
      program_level: student.program_level,
      status: student.status,
      email: student.email || '',
    });
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingStudent(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.student_id_number.trim() || !formData.name.trim() || !formData.department) {
      alert('필수 필드를 모두 입력하세요.');
      return;
    }

    try {
      if (editingStudent) {
        await studentAPI.update(editingStudent.id, formData);
      } else {
        await studentAPI.create(formData);
      }
      fetchData();
      handleCloseModal();
    } catch (err) {
      alert('저장에 실패했습니다.');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await studentAPI.delete(id);
      fetchData();
    } catch (err) {
      alert('삭제에 실패했습니다.');
      console.error(err);
    }
  };

  if (loading) return <MainLayout><LoadingSpinner /></MainLayout>;
  if (error) return <MainLayout><ErrorMessage message={error} /></MainLayout>;

  return (
    <MainLayout>
      <div className="page-container">
        <div className="page-header">
          <h1>학생 관리</h1>
          <Button onClick={handleCreate}>+ 새 학생</Button>
        </div>

        {students.length === 0 ? (
          <EmptyState message="등록된 학생이 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>학번</th>
                  <th>이름</th>
                  <th>학과</th>
                  <th>과정</th>
                  <th>상태</th>
                  <th>이메일</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id}>
                    <td>{student.student_id_number}</td>
                    <td>{student.name}</td>
                    <td>{student.department_name}</td>
                    <td>{student.program_level}</td>
                    <td>{student.status}</td>
                    <td>{student.email || '-'}</td>
                    <td>
                      <div className="action-buttons">
                        <button className="btn-edit" onClick={() => handleEdit(student)}>
                          수정
                        </button>
                        <button className="btn-delete" onClick={() => handleDelete(student.id)}>
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
          title={editingStudent ? '학생 수정' : '새 학생'}
        >
          <form onSubmit={handleSubmit}>
            <Input
              label="학번"
              value={formData.student_id_number}
              onChange={(e) => setFormData({ ...formData, student_id_number: e.target.value })}
              required
            />
            <Input
              label="이름"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <div className="form-group">
              <label>학과</label>
              <select
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                required
              >
                <option value="">선택하세요</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.college_name} - {dept.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>과정</label>
              <select
                value={formData.program_level}
                onChange={(e) => setFormData({ ...formData, program_level: e.target.value })}
              >
                <option value="학사">학사</option>
                <option value="석사">석사</option>
                <option value="박사">박사</option>
              </select>
            </div>
            <div className="form-group">
              <label>상태</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="재학">재학</option>
                <option value="휴학">휴학</option>
                <option value="졸업">졸업</option>
              </select>
            </div>
            <Input
              label="이메일"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
          .page-container { padding: 2rem; }
          .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
          .page-header h1 { font-size: 2rem; font-weight: 700; margin: 0; }
          .table-container { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); overflow-x: auto; }
          .data-table { width: 100%; border-collapse: collapse; }
          .data-table thead { background-color: #f9fafb; }
          .data-table th { padding: 1rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; }
          .data-table td { padding: 1rem; border-bottom: 1px solid #e5e7eb; }
          .data-table tbody tr:hover { background-color: #f9fafb; }
          .action-buttons { display: flex; gap: 0.5rem; }
          .btn-edit, .btn-delete { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 0.875rem; font-weight: 500; transition: all 0.2s; }
          .btn-edit { background-color: #3b82f6; color: white; }
          .btn-edit:hover { background-color: #2563eb; }
          .btn-delete { background-color: #ef4444; color: white; }
          .btn-delete:hover { background-color: #dc2626; }
          .form-group { margin-bottom: 1rem; }
          .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; }
          .form-group select { width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 4px; font-size: 1rem; }
          .modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1.5rem; }
        `}</style>
      </div>
    </MainLayout>
  );
};

export default StudentPage;
