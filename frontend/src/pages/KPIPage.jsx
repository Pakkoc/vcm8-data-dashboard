import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { kpiAPI, departmentAPI } from '../api/crudAPI';

const KPIPage = () => {
  const [kpis, setKpis] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingKPI, setEditingKPI] = useState(null);
  const [formData, setFormData] = useState({
    department: '',
    evaluation_year: new Date().getFullYear(),
    employment_rate: '',
    full_time_faculty_count: '',
    visiting_faculty_count: '',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [kpisData, departmentsData] = await Promise.all([
        kpiAPI.getAll(),
        departmentAPI.getAll(),
      ]);
      setKpis(kpisData);
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
    setEditingKPI(null);
    setFormData({
      department: '',
      evaluation_year: new Date().getFullYear(),
      employment_rate: '',
      full_time_faculty_count: '',
      visiting_faculty_count: '',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (kpi) => {
    setEditingKPI(kpi);
    setFormData({
      department: kpi.department,
      evaluation_year: kpi.evaluation_year,
      employment_rate: kpi.employment_rate || '',
      full_time_faculty_count: kpi.full_time_faculty_count || '',
      visiting_faculty_count: kpi.visiting_faculty_count || '',
    });
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingKPI(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const submitData = {
        ...formData,
        employment_rate: formData.employment_rate || null,
        full_time_faculty_count: formData.full_time_faculty_count || null,
        visiting_faculty_count: formData.visiting_faculty_count || null,
      };

      if (editingKPI) {
        await kpiAPI.update(editingKPI.id, submitData);
      } else {
        await kpiAPI.create(submitData);
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
      await kpiAPI.delete(id);
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
          <h1>학과 KPI 관리</h1>
          <Button onClick={handleCreate}>+ 새 KPI</Button>
        </div>

        {kpis.length === 0 ? (
          <EmptyState message="등록된 KPI가 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>학과</th>
                  <th>평가년도</th>
                  <th>취업률(%)</th>
                  <th>전임교원</th>
                  <th>겸임교원</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {kpis.map((kpi) => (
                  <tr key={kpi.id}>
                    <td>{kpi.department_name}</td>
                    <td>{kpi.evaluation_year}</td>
                    <td>{kpi.employment_rate || '-'}</td>
                    <td>{kpi.full_time_faculty_count || '-'}</td>
                    <td>{kpi.visiting_faculty_count || '-'}</td>
                    <td>
                      <div className="action-buttons">
                        <button className="btn-edit" onClick={() => handleEdit(kpi)}>수정</button>
                        <button className="btn-delete" onClick={() => handleDelete(kpi.id)}>삭제</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Modal isOpen={isModalOpen} onClose={handleCloseModal} title={editingKPI ? 'KPI 수정' : '새 KPI'}>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>학과</label>
              <select value={formData.department} onChange={(e) => setFormData({ ...formData, department: e.target.value })} required>
                <option value="">선택하세요</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.college_name} - {dept.name}</option>
                ))}
              </select>
            </div>
            <Input label="평가년도" type="number" value={formData.evaluation_year} onChange={(e) => setFormData({ ...formData, evaluation_year: e.target.value })} required />
            <Input label="취업률(%)" type="number" step="0.01" value={formData.employment_rate} onChange={(e) => setFormData({ ...formData, employment_rate: e.target.value })} />
            <Input label="전임교원 수" type="number" value={formData.full_time_faculty_count} onChange={(e) => setFormData({ ...formData, full_time_faculty_count: e.target.value })} />
            <Input label="겸임교원 수" type="number" value={formData.visiting_faculty_count} onChange={(e) => setFormData({ ...formData, visiting_faculty_count: e.target.value })} />
            <div className="modal-actions">
              <Button type="button" onClick={handleCloseModal} variant="secondary">취소</Button>
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

export default KPIPage;
