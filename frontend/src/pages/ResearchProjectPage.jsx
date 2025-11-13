import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { researchProjectAPI, departmentAPI } from '../api/crudAPI';

const ResearchProjectPage = () => {
  const [projects, setProjects] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({
    project_number: '',
    name: '',
    principal_investigator: '',
    department: '',
    funding_agency: '',
    total_funding_amount: '',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projectsData, departmentsData] = await Promise.all([
        researchProjectAPI.getAll(),
        departmentAPI.getAll(),
      ]);
      setProjects(projectsData);
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
    setEditingProject(null);
    setFormData({ project_number: '', name: '', principal_investigator: '', department: '', funding_agency: '', total_funding_amount: '' });
    setIsModalOpen(true);
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      project_number: project.project_number,
      name: project.name,
      principal_investigator: project.principal_investigator || '',
      department: project.department,
      funding_agency: project.funding_agency || '',
      total_funding_amount: project.total_funding_amount || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        total_funding_amount: formData.total_funding_amount || null,
      };
      if (editingProject) {
        await researchProjectAPI.update(editingProject.id, submitData);
      } else {
        await researchProjectAPI.create(submitData);
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
      await researchProjectAPI.delete(id);
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
          <h1>연구과제 관리</h1>
          <Button onClick={handleCreate}>+ 새 연구과제</Button>
        </div>

        {projects.length === 0 ? (
          <EmptyState message="등록된 연구과제가 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>과제번호</th>
                  <th>과제명</th>
                  <th>책임연구원</th>
                  <th>학과</th>
                  <th>지원기관</th>
                  <th>총연구비</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((proj) => (
                  <tr key={proj.id}>
                    <td>{proj.project_number}</td>
                    <td style={{ maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{proj.name}</td>
                    <td>{proj.principal_investigator || '-'}</td>
                    <td>{proj.department_name}</td>
                    <td>{proj.funding_agency || '-'}</td>
                    <td>{proj.total_funding_amount ? proj.total_funding_amount.toLocaleString() : '-'}</td>
                    <td>
                      <div className="action-buttons">
                        <button className="btn-edit" onClick={() => handleEdit(proj)}>수정</button>
                        <button className="btn-delete" onClick={() => handleDelete(proj.id)}>삭제</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingProject ? '연구과제 수정' : '새 연구과제'}>
          <form onSubmit={handleSubmit}>
            <Input label="과제번호" value={formData.project_number} onChange={(e) => setFormData({ ...formData, project_number: e.target.value })} required />
            <Input label="과제명" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
            <Input label="책임연구원" value={formData.principal_investigator} onChange={(e) => setFormData({ ...formData, principal_investigator: e.target.value })} />
            <div className="form-group">
              <label>학과</label>
              <select value={formData.department} onChange={(e) => setFormData({ ...formData, department: e.target.value })} required>
                <option value="">선택하세요</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.college_name} - {dept.name}</option>
                ))}
              </select>
            </div>
            <Input label="지원기관" value={formData.funding_agency} onChange={(e) => setFormData({ ...formData, funding_agency: e.target.value })} />
            <Input label="총연구비" type="number" value={formData.total_funding_amount} onChange={(e) => setFormData({ ...formData, total_funding_amount: e.target.value })} />
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
          .data-table th { padding: 1rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; white-space: nowrap; }
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

export default ResearchProjectPage;
