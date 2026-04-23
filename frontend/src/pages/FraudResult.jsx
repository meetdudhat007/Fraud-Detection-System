import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ChevronLeft, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function FraudResult() {
  const { id } = useParams();
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [txn, setTxn] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    fetchTxn();
  }, [id]);

  const fetchTxn = async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/transactions/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        console.log('loaded txn', data);
        setTxn(data);
      } else {
        console.warn('failed to load txn', await res.text());
      }
    } catch (err) {
      console.error('fetchTxn error', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-20 text-[#a0aabf] animate-pulse">Loading analysis...</div>;
  if (!txn) return <div className="text-center py-20 text-red-500">Transaction not found</div>;

  // The metrics from our backend simulation
  const metrics = txn.advanced_metrics || {
    status: txn.is_fraud ? 'Fraud' : 'Safe',
    fraud_score: txn.risk_score,
    graph_based_status: txn.risk_score > 60 ? 'Suspicious' : 'Normal',
    time_series_status: txn.risk_score > 50 ? 'Suspicious' : 'Normal',
    model_predictions: {
      supervised_rf: txn.is_fraud ? 'Fraud' : 'Safe',
      unsupervised_if: 'Safe',
      neural_network_mlp: 'Safe'
    }
  };

  const isFraud = metrics.status === 'Fraud';
  // Use exact colors from the screenshot
  const deepBg = '#0f1115';
  const cardBg = '#181b21';
  const borderColor = '#2a2e39';
  const textMuted = '#7e879c';
  const textAlert = '#ef4444';
  const textSafe = '#10b981';

  return (
    <div className="min-h-screen text-gray-200" style={{ backgroundColor: deepBg, margin: '-3rem -2rem -3rem -2rem', padding: '3rem 2rem' }}>
      
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
            <Link to="/admin" className="text-[#64748b] hover:text-white transition-colors">
                <ChevronLeft size={20} />
            </Link>
            <h1 className="text-2xl font-semibold text-white">Fraud Result</h1>
        </div>
        <p className="text-sm pl-8" style={{ color: textMuted }}>
          Transaction #{txn.id} • {new Date(txn.created_at).toLocaleString()}
        </p>
      </div>

      <div className="space-y-6">
        
        {/* Top 4 Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          {/* Status Box */}
          <div className="rounded-xl p-5 border flex flex-col justify-center" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: textMuted }}>Status</p>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 text-xs font-medium rounded-full border ${isFraud ? 'bg-red-900/20 text-red-500 border-red-900/50' : 'bg-green-900/20 text-green-500 border-green-900/50'}`}>
                {metrics.status}
              </span>
              <div className={`h-2 w-2 rounded-full ${isFraud ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 'bg-green-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]'}`}></div>
            </div>
          </div>

          {/* Fraud Score Box */}
          <div className="rounded-xl p-5 border md:col-span-1" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: textMuted }}>Fraud Score</p>
            <div className="mb-2">
                <span className="text-xl font-bold" style={{ color: '#f59e0b'}}>{metrics.fraud_score}%</span>
                <span className="text-sm ml-1" style={{ color: textMuted }}>/ 100%</span>
            </div>
            {/* Progress bar */}
            <div className="h-1.5 w-full bg-[#222632] rounded-full overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-orange-500 to-yellow-400" style={{ width: `${metrics.fraud_score}%` }}></div>
            </div>
          </div>

          {/* Graph Based Box */}
          <div className="rounded-xl p-5 border flex flex-col justify-center" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: textMuted }}>Graph-Based</p>
            <div>
                 <span className={`px-3 py-1 text-xs font-medium rounded-full border ${metrics.graph_based_status === 'Normal' ? 'bg-green-900/20 text-green-500 border-green-900/50' : 'bg-orange-900/20 text-orange-400 border-orange-900/50'}`}>
                    {metrics.graph_based_status}
                 </span>
            </div>
          </div>

          {/* Time Series Box */}
          <div className="rounded-xl p-5 border flex flex-col justify-center" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: textMuted }}>Time-Series</p>
            <div>
                 <span className={`px-3 py-1 text-xs font-medium rounded-full border ${metrics.time_series_status === 'Normal' ? 'bg-green-900/20 text-green-500 border-green-900/50' : 'bg-orange-900/20 text-orange-400 border-orange-900/50'}`}>
                    {metrics.time_series_status}
                 </span>
            </div>
          </div>
        </div>

        {/* Model Predictions Section */}
        <div className="rounded-xl p-6 border" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-6" style={{ color: textMuted }}>Model Predictions</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Supervised */}
                <div className="p-4 rounded-lg bg-[#14161b] border border-transparent">
                     <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-3">Supervised (RF)</p>
                     <span className={`px-3 py-1 text-xs font-medium rounded-full border ${metrics.model_predictions.supervised_rf === 'Fraud' ? 'bg-red-900/20 text-red-500 border-red-900/50' : 'bg-green-900/20 text-green-500 border-green-900/50'}`}>
                        {metrics.model_predictions.supervised_rf}
                     </span>
                </div>

                {/* Unsupervised */}
                <div className="p-4 rounded-lg bg-[#14161b] border border-transparent">
                     <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-3">Unsupervised (IF)</p>
                     <span className={`px-3 py-1 text-xs font-medium rounded-full border ${metrics.model_predictions.unsupervised_if === 'Fraud' ? 'bg-red-900/20 text-red-500 border-red-900/50' : 'bg-green-900/20 text-green-500 border-green-900/50'}`}>
                        {metrics.model_predictions.unsupervised_if}
                     </span>
                </div>

                {/* Neural Network */}
                <div className="p-4 rounded-lg bg-[#14161b] border border-transparent">
                     <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-3">Neural Network (MLP)</p>
                     <span className={`px-3 py-1 text-xs font-medium rounded-full border ${metrics.model_predictions.neural_network_mlp === 'Fraud' ? 'bg-red-900/20 text-red-500 border-red-900/50' : 'bg-green-900/20 text-green-500 border-green-900/50'}`}>
                        {metrics.model_predictions.neural_network_mlp}
                     </span>
                </div>

            </div>
        </div>

        {/* Transaction Input Section */}
        <div className="rounded-xl p-6 border" style={{ backgroundColor: cardBg, borderColor: borderColor }}>
            <p className="text-xs font-bold uppercase tracking-wider mb-6" style={{ color: textMuted }}>Transaction Input</p>
            <div className="grid grid-cols-2 gap-y-6">
                <div>
                     <p className="text-xs mb-1" style={{ color: textMuted }}>Type</p>
                     <p className="font-semibold text-white tracking-wide uppercase">{txn.type}</p>
                </div>
                <div>
                     <p className="text-xs mb-1" style={{ color: textMuted }}>Sender</p>
                     <p className="font-semibold text-white tracking-wide">
                        {txn.sender_username ? txn.sender_username : `#${txn.sender_id}`}
                     </p>
                </div>
                <div>
                     <p className="text-xs mb-1" style={{ color: textMuted }}>Destination ID</p>
                     <p className="font-semibold text-white tracking-wide">{txn.oldbalanceDest > 0 ? `D${parseInt(txn.oldbalanceDest).toString().padStart(9, '0')}` : 'N/A'}</p>
                </div>
                <div>
                     <p className="text-xs mb-1" style={{ color: textMuted }}>Amount</p>
                     <p className="font-semibold text-white tracking-wide">{txn.amount.toLocaleString(undefined, { minimumFractionDigits: 3 })}</p>
                </div>
            </div>
        </div>
        
        {/* Footer Actions */}
        <div className="flex items-center gap-4 mt-6">
            <button
               onClick={() => setShowExplanation(prev => !prev)}
               className="bg-[#3b82f6] hover:bg-[#2563eb] text-white font-semibold py-2.5 px-5 rounded-lg text-sm transition-colors">
                {showExplanation ? 'Hide explanation' : 'View risk explanation'}
            </button>
            <button
               onClick={() => navigate('/admin')}
               className="bg-transparent border border-[#3b4355] text-[#a0aabf] hover:text-white hover:border-[#64748b] font-semibold py-2.5 px-5 rounded-lg text-sm transition-colors">
                New check
            </button>
        </div>
        {showExplanation && (
          <div className="mt-6 p-4 rounded-lg bg-[#14161b] border border-[#2a2e39]">
             <p className="text-sm font-semibold mb-2" style={{ color: textMuted }}>Explanation</p>
             {txn.explanations && txn.explanations.length > 0 ? (
                <ul className="list-disc list-inside text-xs" style={{ color: textMuted }}>
                   {txn.explanations.map((exp, idx) => <li key={idx}>{exp}</li>)}
                </ul>
             ) : (
                <p className="text-xs" style={{ color: textMuted }}>No specific reasons provided.</p>
             )}
          </div>
        )}

      </div>
    </div>
  );
}
