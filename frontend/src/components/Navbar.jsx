import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, LogOut, Menu, X } from 'lucide-react';
import Logo from './Logo';
import VSCodeLogo from './VSCodeLogo';

const Navbar = ({ user, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
    setIsMenuOpen(false);
  };

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
          <div className="hidden md:flex items-center">
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/your-username/anzen-lite-extension"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-white bg-[#0066b8] hover:bg-[#005ba4] active:bg-[#004793] rounded-md transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <VSCodeLogo size={16} className="flex-shrink-0 text-white" />
                <span>VS Code</span>
              </a>
              <div 
                className="group relative p-2 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors duration-200"
              >
                <User className="h-4 w-4 text-gray-300" />
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 translate-y-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                  <div className="bg-gray-900 text-white text-sm px-3 py-1.5 rounded-lg shadow-lg border border-gray-700 whitespace-nowrap">
                    <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 -translate-y-1/2 border-4 border-transparent border-b-gray-900"></div>
                    {user?.email}
                  </div>
                </div>
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
          <div className="px-4 py-3 space-y-3">
            <a
              href="https://github.com/your-username/anzen-lite-extension"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center px-3 py-2 text-base font-medium text-white bg-[#0066b8] hover:bg-[#005ba4] active:bg-[#004793] rounded-md transition-all duration-200 shadow-sm hover:shadow-md"
            >
              <VSCodeLogo size={20} className="flex-shrink-0 mr-3 text-white" />
              VS Code
            </a>
            <div className="flex items-center px-3 py-2 bg-gray-700 rounded-md" title={user?.email}>
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
      )}
    </nav>
  );
};

export default Navbar;
