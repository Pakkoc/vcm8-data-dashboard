import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { publicationAPI, departmentAPI } from '../api/crudAPI';

const PublicationPage = () => {
  const [publications, setPublications] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPublication, setEditingPublication] = useState(null);
  const [formData, setFormData] = useState({
    publication_date: '',
    department: '',
    title: '',
    primary_author: '',
    journal_name: '',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [publicationsData, departmentsData] = await Promise.all([
        publicationAPI.getAll(),
        departmentAPI.getAll(),
      ]);
      setPublications(publicationsData);
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
    setEditingPublication(null);
    setFormData({ publication_date: '', department: '', title: '', primary_author: '', journal_name: '' });
    setIsModalOpen(true);
  };

  const handleEdit = (publication) => {
    setEditingPublication(publication);
    setFormData({
      publication_date: publication.publication_date,
      department: publication.department,
      title: publication.title,
      primary_author: publication.primary_author || '',
      journal_name: publication.journal_name || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingPublication) {
        await publicationAPI.update(editingPublication.id, formData);
      } else {
        await publicationAPI.create(formData);
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
      await publicationAPI.delete(id);
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
          <h1>논문 관리</h1>
          <Button onClick={handleCreate}>+ 새 논문</Button>
        </div>

        {publications.length === 0 ? (
          <EmptyState message="등록된 논문이 없습니다." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>게재일</th>
                  <th>학과</th>
                  <th>논문제목</th>
                  <th>제1저자</th>
                  <th>저널명</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {publications.map((pub) => (
                  <tr key={pub.id}>
                    <td>{new Date(pub.publication_date).toLocaleDateString()}</td>
                    <td>{pub.department_name}</td>
                    <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{pub.title}</td>
                    <td>{pub.primary_author || '-'}</td>
                    <td>{pub.journal_name || '-'}</td>
                    <td>
                      <div className="action-buttons">
                        <button className="btn-edit" onClick={() => handleEdit(pub)}>수정</button>
                        <button className="btn-delete" onClick={() => handleDelete(pub.id)}>삭제</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingPublication ? '논문 수정' : '새 논문'}>
          <form onSubmit={handleSubmit}>
            <Input label="게재일" type="date" value={formData.publication_date} onChange={(e) => setFormData({ ...formData, publication_date: e.target.value })} required />
            <div className="form-group">
              <label>학과</label>
              <select value={formData.department} onChange={(e) => setFormData({ ...formData, department: e.target.value })} required>
                <option value="">선택하세요</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.college_name} - {dept.name}</option>
                ))}
              </select>
            </div>
            <Input label="논문제목" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} required />
            <Input label="제1저자" value={formData.primary_author} onChange={(e) => setFormData({ ...formData, primary_author: e.target.value })} />
            <Input label="저널명" value={formData.journal_name} onChange={(e) => setFormData({ ...formData, journal_name: e.target.value })} />
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

export default PublicationPage;
