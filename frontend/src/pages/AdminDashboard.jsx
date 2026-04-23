import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { io } from 'socket.io-client';
import { ShieldAlert, TrendingUp, Users, AlertTriangle, AlertCircle } from 'lucide-react';
import { 
  BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, 
  Legend, LineChart, Line, ScatterChart, Scatter, ZAxis
} from 'recharts';

export default function AdminDashboard() {
  const { token } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [liveFeed, setLiveFeed] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initialize Socket.io
  useEffect(() => {
    fetchStats();

    const socket = io('http://localhost:5000');
    
    socket.on('new_transaction', (txn) => {
       // Prepend to live feed
       setLiveFeed(prev => [txn, ...prev].slice(0, 50));
       
       // Update stats intelligently without full refetch
       setStats(prev => {
          if(!prev) return prev;
          const isFraud = txn.is_fraud;
          const newTotal = prev.total_transactions + 1;
          const newFraudCount = prev.fraud_transactions + (isFraud ? 1 : 0);
          
          return {
             ...prev,
             total_transactions: newTotal,
             fraud_transactions: newFraudCount,
             fraud_percentage: ((newFraudCount / newTotal) * 100).toFixed(2),
             recent_timeline: [txn, ...prev.recent_timeline].slice(0, 50)
          };
       });
    });

    return () => socket.disconnect();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/admin/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
        setLiveFeed(data.recent_timeline || []);
      }
    } catch (err) {
      console.error("Failed to fetch admin stats", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) return <div className="text-center py-20 text-indigo-500 animate-pulse font-medium text-lg">Initializing Security Telemetry...</div>;

  // Prepare chart data
  const pieData = Object.keys(stats.by_type).map(key => ({
    name: key, 
    value: stats.by_type[key],
    fraud: stats.fraud_by_type[key] || 0
  }));

  const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  
  // Transform timeline data for heatmap-like scatter plot (amount vs time)
  const scatterData = liveFeed.map((t, index) => ({
      x: index, // Recent index mapping to time
      y: parseFloat(t.amount),
      z: t.risk_score,
      fraud: t.is_fraud
  })).reverse();

  return (
    <div className="space-y-6">
      
      {/* Top Value Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Transactions</p>
            <h3 className="text-3xl font-black mt-1 dark:text-white">{stats.total_transactions}</h3>
          </div>
          <div className="h-12 w-12 bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400 rounded-2xl flex items-center justify-center">
            <TrendingUp size={24} />
          </div>
        </div>
        
        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Flagged Frauds</p>
            <h3 className="text-3xl font-black mt-1 text-red-600 dark:text-red-400">{stats.fraud_transactions}</h3>
          </div>
          <div className="h-12 w-12 bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 rounded-2xl flex items-center justify-center">
            <ShieldAlert size={24} />
          </div>
        </div>

        <div className="glass-panel p-6 flex items-center justify-between relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent"></div>
          <div className="relative z-10">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Fraud Rate</p>
            <h3 className="text-3xl font-black mt-1 dark:text-white">{stats.fraud_percentage}%</h3>
          </div>
          <div className="relative z-10 h-12 w-12 bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400 rounded-2xl flex items-center justify-center">
            <AlertTriangle size={24} />
          </div>
        </div>
      </div>

      {/* Main Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Col: 2 Charts */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 h-96">
            <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-6">Transaction Volume & Fraud by Type</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pieData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <XAxis dataKey="name" stroke="#8884d8" />
                <YAxis />
                <Tooltip cursor={{fill: 'transparent'}} contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff'}} />
                <Legend />
                <Bar dataKey="value" name="Total Count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fraud" name="Fraud Count" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="glass-panel p-6 h-[400px]">
             <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-6 flex justify-between">
               <span>Fraud Risk Scatter Heatmap</span>
               <span className="text-xs font-normal text-gray-500 mt-1">Amount vs Recent Timeline (Bubble Size = Risk)</span>
             </h3>
             <ResponsiveContainer width="100%" height="85%">
               <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <XAxis dataKey="x" name="Sequence" type="number" hide />
                  <YAxis dataKey="y" name="Amount (₹)" type="number" scale="log" domain={['auto', 'auto']} stroke="#8884d8" />
                  <ZAxis dataKey="z" range={[50, 400]} name="Risk Score" />
                  <Tooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{backgroundColor: '#1e293b', borderRadius: '8px'}}/>
                  <Scatter name="Normal" data={scatterData.filter(d => !d.fraud)} fill="#10b981" fillOpacity={0.6} />
                  <Scatter name="Fraud" data={scatterData.filter(d => d.fraud)} fill="#ef4444" fillOpacity={0.8} />
               </ScatterChart>
             </ResponsiveContainer>
          </div>
        </div>

        {/* Right Col: Live Feed */}
        <div className="lg:col-span-1 glass-panel p-0 flex flex-col h-[800px] overflow-hidden">
          <div className="p-6 border-b border-gray-100 dark:border-slate-800 flex justify-between items-center">
            <h3 className="font-bold flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              Live Telemetry
            </h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 dashboard-scrollbar">
             {liveFeed.map((txn, i) => (
                <Link to={`/admin/fraud-result/${txn.id}`} key={i} className={`block p-4 rounded-xl border animate-in fade-in slide-in-from-top-4 duration-300 hover:shadow-md transition-all ${
                   txn.is_fraud ? 'bg-red-50 hover:bg-red-100 dark:bg-red-900/10 dark:hover:bg-red-900/20 border-red-200 dark:border-red-900/50' : 'bg-white hover:bg-gray-50 dark:bg-slate-800 dark:hover:bg-slate-700 border-gray-100 dark:border-slate-700'
                }`}>
                   <div className="flex justify-between items-start">
                      <div>
                         <span className="font-semibold block text-sm focus:outline-none">{txn.type}</span>
                         <span className="text-xs text-gray-500">
                           {txn.sender_username && txn.receiver_username ?
                             `From ${txn.sender_username} to ${txn.receiver_username}` :
                             txn.sender_username || txn.receiver_username || 'Unknown'}
                         </span>
                      </div>
                      <span className="font-bold font-mono text-sm">₹{txn.amount.toLocaleString()}</span>
                   </div>
                   <div className="mt-3 flex justify-between items-end">
                      <span className="text-xs text-gray-400">{new Date(txn.created_at).toLocaleTimeString()}</span>
                      <span className={`text-xs px-2 py-1 rounded-md font-bold ${
                         txn.is_fraud ? 'bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400' : 'bg-green-100 text-green-600 dark:bg-green-900/50 dark:text-green-400'
                      }`}>
                         Risk: {txn.risk_score}%
                      </span>
                   </div>
                </Link>
             ))}
             {liveFeed.length === 0 && <p className="text-center text-sm text-gray-500 mt-10">Waiting for transactions...</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
