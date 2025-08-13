import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { User, LogOut, Menu, X } from 'lucide-react';
import Logo from './Logo';

const Navbar = ({ user, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
    setIsMenuOpen(false);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-gray-800 shadow-lg border-b border-gray-700 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-3 group">
              <Logo size="lg" className="group-hover:opacity-90 transition-opacity duration-200" />
              <span className="text-xl font-bold text-white">Anzen</span>
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                isActive('/dashboard')
                  ? 'text-blue-400 bg-blue-900/20'
                  : 'text-gray-300 hover:text-blue-400 hover:bg-gray-700'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/add-repository"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                isActive('/add-repository')
                  ? 'text-blue-400 bg-blue-900/20'
                  : 'text-gray-300 hover:text-blue-400 hover:bg-gray-700'
              }`}
            >
              Add Repository
            </Link>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-700 rounded-lg">
                <User className="h-4 w-4 text-gray-300" />
                <span className="text-sm font-medium text-gray-200">{user?.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-md transition-colors duration-200"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md text-gray-300 hover:text-gray-200 hover:bg-gray-700 transition-colors duration-200"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-gray-800 border-t border-gray-700">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link
              to="/dashboard"
              onClick={() => setIsMenuOpen(false)}
              className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${
                isActive('/dashboard')
                  ? 'text-blue-400 bg-blue-900/20'
                  : 'text-gray-300 hover:text-blue-400 hover:bg-gray-700'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/add-repository"
              onClick={() => setIsMenuOpen(false)}
              className={`block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${
                isActive('/add-repository')
                  ? 'text-blue-400 bg-blue-900/20'
                  : 'text-gray-300 hover:text-blue-400 hover:bg-gray-700'
              }`}
            >
              Add Repository
            </Link>

            <div className="border-t border-gray-700 pt-3 mt-3">
              <div className="flex items-center px-3 py-2">
                <User className="h-5 w-5 text-gray-300 mr-3" />
                <span className="text-base font-medium text-gray-200">{user?.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left flex items-center px-3 py-2 text-base font-medium text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-md transition-colors duration-200"
              >
                <LogOut className="h-5 w-5 mr-3" />
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;