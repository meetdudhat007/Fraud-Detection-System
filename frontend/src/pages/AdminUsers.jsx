import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Users, Trash2, AlertCircle } from 'lucide-react';

export default function AdminUsers() {
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:5000/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      } else {
        setError('Failed to load users');
      }
    } catch (err) {
      setError('Network error');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (id, username) => {
    if (username === 'admin') {
      alert("Cannot delete the default admin user.");
      return;
    }
    
    if (!window.confirm(`Are you sure you want to delete user ${username}? All their transactions will also be deleted.`)) {
      return;
    }

    try {
      const res = await fetch(`http://localhost:5000/api/admin/users/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        // Remove user from local state
        setUsers(prev => prev.filter(u => u.id !== id));
      } else {
        const data = await res.json();
        alert(data.message || 'Failed to delete user');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to server');
    }
  };

  if (loading) return <div className="text-center py-20 text-indigo-500 animate-pulse font-medium text-lg">Loading User Directory...</div>;
  if (error) return <div className="text-center py-20 text-red-500"><AlertCircle className="mx-auto mb-2 h-8 w-8"/>{error}</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold dark:text-white flex items-center gap-2">
            <Users className="h-6 w-6 text-indigo-500" />
            User Management
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Manage system accounts and view generated balances.</p>
        </div>
        <div className="bg-indigo-100 text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-200 px-4 py-2 rounded-lg font-bold">
          Total: {users.length} Users
        </div>
      </div>

      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 dark:bg-slate-800/50 border-b border-gray-100 dark:border-slate-700">
                <th className="p-4 font-semibold text-gray-600 dark:text-gray-300">ID</th>
                <th className="p-4 font-semibold text-gray-600 dark:text-gray-300">Username</th>
                <th className="p-4 font-semibold text-gray-600 dark:text-gray-300">Role</th>
                <th className="p-4 font-semibold text-gray-600 dark:text-gray-300">Balance</th>
                <th className="p-4 font-semibold text-gray-600 dark:text-gray-300 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-gray-50 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="p-4 text-gray-500 dark:text-gray-400">#{u.id}</td>
                  <td className="p-4 font-medium dark:text-gray-200">{u.username}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded-full font-bold uppercase ${u.role === 'admin' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-400' : 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="p-4 font-mono dark:text-gray-300">₹{u.balance != null ? u.balance.toLocaleString() : '0.00'}</td>
                  <td className="p-4 text-right">
                    <button 
                      onClick={() => deleteUser(u.id, u.username)}
                      disabled={u.username === 'admin'}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Delete User"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-gray-500 dark:text-gray-400">
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
