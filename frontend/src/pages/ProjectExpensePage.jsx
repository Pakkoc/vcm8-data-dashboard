import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { projectExpenseAPI, researchProjectAPI } from '../api/crudAPI';

const ProjectExpensePage = () => {
  const [expenses, setExpenses] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [formData, setFormData] = useState({
    execution_id: '',
    project: '',
    execution_date: '',
    item: '',
    amount: '',
    status: '처리중',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [expensesData, projectsData] = await Promise.all([
        projectExpenseAPI.getAll(),
        researchProjectAPI.getAll(),
      ]);
      setExpenses(expensesData);
      setProjects(projectsData);
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
    setEditingExpense(null);
    setFormData({ execution_id: '', project: '', execution_date: '', item: '', amount: '', status: '처리중' });
    setIsModalOpen(true);
  };

  const handleEdit = (expense) => {
    setEditingExpense(expense);
    setFormData({
      execution_id: expense.execution_id,
      project: expense.project,
      execution_date: expense.execution_date,
      item: expense.item,
      amount: expense.amount,
      status: expense.status,
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingExpense) {
        await projectExpenseAPI.update(editingExpense.id, formData);
      } else {
        await projectExpenseAPI.create(formData);
      }
      fetchData();
      setIsModalOpen(false);
    } catch (err) {
      alert('저장에 실패했습니다.');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await projectExpenseAPI.delete(id);
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
          <h1>과제집행내역 관리</h1>
          <Button onClick={handleCreate}>+ 새 집행내역</Button>
        </div>

        {expenses.length === 0 ? (
          <EmptyState message="등록된 집행내역이 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>집행ID</th>
                  <th>과제번호</th>
                  <th>집행일</th>
                  <th>항목</th>
                  <th>금액</th>
                  <th>상태</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((exp) => (
                  <tr key={exp.id}>
                    <td>{exp.execution_id}</td>
                    <td>{exp.project_number}</td>
                    <td>{new Date(exp.execution_date).toLocaleDateString()}</td>
                    <td>{exp.item}</td>
                    <td>{exp.amount.toLocaleString()}</td>
                    <td><span className={`status-badge status-${exp.status}`}>{exp.status}</span></td>
                    <td>
                      <div className="action-buttons">
                        <button className="btn-edit" onClick={() => handleEdit(exp)}>수정</button>
                        <button className="btn-delete" onClick={() => handleDelete(exp.id)}>삭제</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingExpense ? '집행내역 수정' : '새 집행내역'}>
          <form onSubmit={handleSubmit}>
            <Input label="집행ID" value={formData.execution_id} onChange={(e) => setFormData({ ...formData, execution_id: e.target.value })} required />
            <div className="form-group">
              <label>연구과제</label>
              <select value={formData.project} onChange={(e) => setFormData({ ...formData, project: e.target.value })} required>
                <option value="">선택하세요</option>
                {projects.map((proj) => (
                  <option key={proj.id} value={proj.id}>{proj.project_number} - {proj.name}</option>
                ))}
              </select>
            </div>
            <Input label="집행일" type="date" value={formData.execution_date} onChange={(e) => setFormData({ ...formData, execution_date: e.target.value })} required />
            <Input label="항목" value={formData.item} onChange={(e) => setFormData({ ...formData, item: e.target.value })} required />
            <Input label="금액" type="number" value={formData.amount} onChange={(e) => setFormData({ ...formData, amount: e.target.value })} required />
            <div className="form-group">
              <label>상태</label>
              <select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })}>
                <option value="처리중">처리중</option>
                <option value="집행완료">집행완료</option>
                <option value="반려">반려</option>
              </select>
            </div>
            <div className="modal-actions">
              <Button type="button" onClick={() => setIsModalOpen(false)} variant="secondary">취소</Button>
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
          .status-badge { padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.875rem; font-weight: 500; }
          .status-처리중 { background-color: #fef3c7; color: #92400e; }
          .status-집행완료 { background-color: #d1fae5; color: #065f46; }
          .status-반려 { background-color: #fee2e2; color: #991b1b; }
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

export default ProjectExpensePage;
