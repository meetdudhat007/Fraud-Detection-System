import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';
import FraudResult from './pages/FraudResult';
import { AuthContext } from './context/AuthContext';
import { ThemeContext } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

function App() {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('theme') === 'dark');

  // Sync dark mode class
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const login = (userData, jwtToken) => {
    setUser(userData);
    setToken(jwtToken);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', jwtToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  const toggleTheme = () => setDarkMode(!darkMode);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      <ThemeContext.Provider value={{ darkMode, toggleTheme }}>
        <div className="min-h-screen flex flex-col animated-bg font-sans">
          <Router>
            <Navbar />
            <main className="flex-grow pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
              <Routes>
                <Route path="/" element={<Navigate to={user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/login'} />} />
                <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
                <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
                <Route path="/dashboard" element={user && user.role !== 'admin' ? <UserDashboard /> : <Navigate to="/login" />} />
                <Route path="/admin" element={user && user.role === 'admin' ? <AdminDashboard /> : <Navigate to="/login" />} />
                <Route path="/admin/users" element={user && user.role === 'admin' ? <AdminUsers /> : <Navigate to="/login" />} />
                <Route path="/admin/fraud-result/:id" element={user && user.role === 'admin' ? <FraudResult /> : <Navigate to="/login" />} />
              </Routes>
            </main>
            <Footer />
          </Router>
        </div>
      </ThemeContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;
