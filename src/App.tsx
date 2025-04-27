import './App.css'
import { Routes, Route } from 'react-router-dom';
import DashboardLayout from './pages/dashboard';
import QuickStart from './pages/quick-start';
import PlaceholderDashboardContent from './components/placeholder-dashboard';

function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardLayout />}>
        <Route index element={<PlaceholderDashboardContent />} />
        <Route path="team" element={<QuickStart />} />
      </Route>
    </Routes>
  );
}

export default App;
