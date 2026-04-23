import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ThemeContext } from '../context/ThemeContext';
import { ShieldAlert, Moon, Sun, LogOut, User, ShieldCheck } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const { darkMode, toggleTheme } = useContext(ThemeContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="fixed top-0 w-full z-50 glass-panel !rounded-none !border-x-0 !border-t-0 bg-white/60 dark:bg-slate-900/60 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <ShieldCheck className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-indigo-600 dark:from-primary-400 dark:to-indigo-400">
                FraudGuard 
              </span>
            </Link>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="h-5 w-5 text-gray-200" /> : <Moon className="h-5 w-5 text-gray-600" />}
            </button>
            
            {user ? (
              <div className="flex items-center gap-4">
                {user.role === 'admin' && (
                  <Link to="/admin/users" className="text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                    Manage Users
                  </Link>
                )}
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100 dark:bg-slate-800">
                  <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{user.username}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200 uppercase tracking-wide">
                    {user.role}
                  </span>
                </div>
                <button 
                  onClick={handleLogout}
                  className="p-2 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Link to="/login" className="btn-secondary !py-2 !px-4 text-sm">Login</Link>
                <Link to="/register" className="btn-primary !py-2 !px-4 text-sm hidden sm:block">Register</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
