import React from 'react';

const Logo = ({ className = '', size = 'md' }) => {
  // Size variants
  const sizes = {
    xs: 'h-4 w-4',      // 16x16 pixels (favicon size)
    sm: 'h-6 w-6',      // 24x24 pixels
    md: 'h-8 w-8',      // 32x32 pixels (standard favicon)
    lg: 'h-12 w-12',    // 48x48 pixels
    xl: 'h-16 w-16',    // 64x64 pixels
    '2xl': 'h-20 w-20', // 80x80 pixels
    icon: 'h-32 w-32'   // 128x128 pixels (app icon)
  };

  return (
    <svg 
      className={`${sizes[size]} ${className}`}
      viewBox="0 0 512 512" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background hexagon with gradient */}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#3B82F6' }} />
          <stop offset="100%" style={{ stopColor: '#2563EB' }} />
        </linearGradient>
      </defs>
      
      {/* Main hexagon */}
      <path 
        d="M256 42 L432 149 L432 363 L256 470 L80 363 L80 149 Z" 
        fill="url(#gradient)"
        stroke="#60A5FA"
        strokeWidth="8"
      />
      
      {/* Inner hexagon for depth */}
      <path 
        d="M256 82 L396 169 L396 343 L256 430 L116 343 L116 169 Z"
        fill="#4F46E5"
        fillOpacity="0.3"
      />
      
      {/* Stylized 安 character */}
      <g transform="translate(256 256) scale(1.2)">
        {/* Top part of 安 */}
        <path 
          d="M-60 -60 L60 -60 L40 -40 L-40 -40 Z"
          fill="white"
        />
        
        {/* Bottom part of 安 */}
        <path 
          d="M-50 -30 L50 -30 L70 60 L0 40 L-70 60 Z"
          fill="white"
        />
      </g>
    </svg>
  );
};

export default Logo;
