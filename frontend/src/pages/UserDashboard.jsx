import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ArrowLeftRight, CreditCard, DollarSign, Activity, AlertTriangle, IndianRupee } from 'lucide-react';

export default function UserDashboard() {
  const { user, token, login } = useContext(AuthContext);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]); // other users to send to
  
  // Form state
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('TRANSFER');
  const [receiverId, setReceiverId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTransactions();
    fetchUsers();
  }, []);

  const fetchTransactions = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/transactions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTransactions(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
        if (data.length > 0) setReceiverId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setLastResult(null);
    setError(null);

    if (!receiverId) {
      setError('Please select a recipient');
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch('http://localhost:5000/api/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ amount: parseFloat(amount), type, receiver_id: receiverId })
      });
      
      const data = await res.json();
      if (res.ok) {
        setLastResult(data);
        setAmount('');
        // update user context with new balance
        if (data.sender_balance !== undefined) {
          login({ ...user, balance: data.sender_balance }, token);
        }
        fetchTransactions(); // Refresh history
      } else {
        setError(data.message || 'Transaction failed');
      }
    } catch (err) {
      console.error(err);
      setError('An error occurred while processing your transaction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* Transaction Form Section */}
      <div className="lg:col-span-1 space-y-6">
        <div className="glass-panel p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5 text-primary-500" />
            New Transaction
          </h2>
          <p className="mb-4">Current balance: <strong>₹{user?.balance?.toFixed(2) || '0.00'}</strong></p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Recipient</label>
              <select
                className="glass-input"
                value={receiverId}
                onChange={(e) => setReceiverId(e.target.value)}
                required
              >
                <option value="" disabled>Select user</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>
                    {u.username}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
              <select 
                className="glass-input"
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <option value="TRANSFER">Transfer</option>
                <option value="PAYMENT">Payment</option>
                <option value="CASH_OUT">Cash Out</option>
                <option value="DEBIT">Debit</option>
                <option value="CASH_IN">Cash In</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Amount (₹)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <IndianRupee className="h-5 w-5 text-gray-400" />
                </div>
                <input 
                  type="number" 
                  step="0.01"
                  min="0.01"
                  max={user?.balance || 0}
                  className={`glass-input pl-10 ${parseFloat(amount) > (user?.balance || 0) ? 'border-red-500 dark:border-red-500' : ''}`}
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                />
              </div>
              {parseFloat(amount) > (user?.balance || 0) && amount && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                  ⚠️ Amount exceeds your available balance of ₹{user?.balance?.toFixed(2)}
                </p>
              )}
            </div>
            
            <button 
              type="submit" 
              className="btn-primary w-full mt-2"
              disabled={submitting || parseFloat(amount) > (user?.balance || 0)}
            >
              {submitting ? 'Processing AI Verification...' : 'Submit Transaction'}
            </button>
          </form>

          {/* Error Message Display */}
          {error && (
            <div className="mt-4 p-4 rounded-2xl bg-red-50/90 dark:bg-red-900/40 border border-red-500/50 flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold text-red-700 dark:text-red-300">Transaction Warning</p>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Real-time AI Result Card */}
        {lastResult && (
          <div className={`p-6 rounded-2xl border backdrop-blur-md shadow-lg transition-all duration-500 transform translate-y-0 opacity-100 ${
            lastResult.is_fraud 
              ? 'bg-red-50/90 dark:bg-red-900/40 border-red-500/50 shadow-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.3)]' 
              : 'bg-green-50/90 dark:bg-green-900/40 border-green-500/50'
          }`}>
            <h3 className="font-bold flex items-center gap-2 mb-2">
              <Activity className="h-5 w-5" />
              AI Risk Analysis
            </h3>
            
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium">Risk Score:</span>
              <span className={`text-2xl font-black ${lastResult.is_fraud ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                {lastResult.risk_score}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-4 overflow-hidden">
              <div 
                className={`h-2.5 rounded-full ${lastResult.is_fraud ? 'bg-red-500' : 'bg-green-500'}`} 
                style={{ width: `${lastResult.risk_score}%`, transition: 'width 1s ease-out' }}
              ></div>
            </div>

            {lastResult.is_fraud && (
              <div className="neon-alert mb-4 flex items-start gap-2 text-sm">
                <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                <div>
                  <strong>⚠️ High Risk Transaction Detected</strong>
                  <p className="mt-1 opacity-90">This transaction has been flagged by our machine learning model.</p>
                </div>
              </div>
            )}
            
            {lastResult.explanations && lastResult.explanations.length > 0 && (
               <div className="mt-3 text-sm">
                  <p className="font-semibold text-gray-700 dark:text-gray-300 mb-1">AI Explanation:</p>
                  <ul className="list-disc pl-5 space-y-1 text-gray-600 dark:text-gray-400">
                     {lastResult.explanations.map((exp, i) => <li key={i}>{exp}</li>)}
                  </ul>
               </div>
            )}
          </div>
        )}
      </div>

      {/* History Section */}
      <div className="lg:col-span-2 space-y-4">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <CreditCard className="h-5 w-5 text-primary-500" />
          Recent Transactions
        </h2>
        
        {loading ? (
          <div className="text-center py-12 text-gray-400 animate-pulse">Loading secure data...</div>
        ) : transactions.length === 0 ? (
          <div className="glass-panel p-12 text-center text-gray-500">
            No transactions found. Make your first transfer!
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map(txn => (
              <div key={txn.id} className="glass-panel p-4 flex items-center justify-between hover:bg-white/90 dark:hover:bg-slate-800/90 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-full ${
                    txn.is_fraud ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' : 
                    'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
                  }`}>
                    {txn.is_fraud ? <AlertTriangle className="h-5 w-5" /> : <ArrowLeftRight className="h-5 w-5" />}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100">{txn.type}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(txn.created_at).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {txn.sender_username === user.username ? 
                        `To: ${txn.receiver_username}` : 
                        `From: ${txn.sender_username}`}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="font-bold text-lg dark:text-white">₹{txn.amount.toLocaleString()}</p>
                  <p className={`text-xs font-medium px-2 py-0.5 rounded-full inline-block mt-1 ${
                    txn.risk_score > 80 ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300' :
                    txn.risk_score > 40 ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300' :
                    'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300'
                  }`}>
                    Risk: {txn.risk_score}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
