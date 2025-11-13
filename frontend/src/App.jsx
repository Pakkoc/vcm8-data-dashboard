import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import CollegePage from './pages/CollegePage';
import DepartmentPage from './pages/DepartmentPage';
import StudentPage from './pages/StudentPage';
import KPIPage from './pages/KPIPage';
import PublicationPage from './pages/PublicationPage';
import ResearchProjectPage from './pages/ResearchProjectPage';
import ProjectExpensePage from './pages/ProjectExpensePage';
import ProtectedRoute from './components/auth/ProtectedRoute';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/upload"
          element={
            <ProtectedRoute adminOnly>
              <UploadPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/colleges"
          element={
            <ProtectedRoute>
              <CollegePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/departments"
          element={
            <ProtectedRoute>
              <DepartmentPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/students"
          element={
            <ProtectedRoute>
              <StudentPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/kpis"
          element={
            <ProtectedRoute>
              <KPIPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/publications"
          element={
            <ProtectedRoute>
              <PublicationPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <ResearchProjectPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/expenses"
          element={
            <ProtectedRoute>
              <ProjectExpensePage />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
