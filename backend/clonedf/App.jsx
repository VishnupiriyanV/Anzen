import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import RepositoryDetail from './pages/RepositoryDetail';
import AddRepository from './pages/AddRepository';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real application, you might verify the session with the backend here
    // or use a more persistent token. For this setup, we rely on Flask's session.
    // Simulate checking for stored auth token (though Flask session is server-side)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    setUser(userData);
    // While Flask manages the session, we keep user data in localStorage for client-side state
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = async () => {
    setUser(null);
    localStorage.removeItem('user');
    // Call backend logout endpoint to clear Flask session
    try {
      await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include' // Important: Send session cookie to clear it
      });
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 transition-colors duration-300">
        {/* Navbar is shown only if user is logged in */}
        {user && <Navbar user={user} onLogout={logout} />}
        
        <Routes>
          <Route 
            path="/" 
            element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/login" 
            element={user ? <Navigate to="/dashboard" /> : <Login onLogin={login} />} 
          />
          <Route 
            path="/signup" 
            element={user ? <Navigate to="/dashboard" /> : <Signup onLogin={login} />} 
          />
          {/* Protected Routes: Only accessible if user is logged in */}
          <Route 
            path="/dashboard" 
            element={user ? <Dashboard /> : <Navigate to="/login" />} 
          />
          <Route
            path="/repository/:repoUrlEncoded" /* Changed to use repoUrlEncoded */
            element={user ? <RepositoryDetail /> : <Navigate to="/login" />}
          />
          <Route 
            path="/add-repository" 
            element={user ? <AddRepository /> : <Navigate to="/login" />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;