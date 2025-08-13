# Anzen - AI Code Vulnerability Checker

A modern, AI-powered web application that scans GitHub repositories for security vulnerabilities and provides detailed remediation guidance.

## 🚀 Features

- **User Authentication**: Secure sign-up and login system
- **Repository Management**: Add, scan, and manage GitHub repositories
- **AI-Powered Scanning**: Automated vulnerability detection using AI models
- **Detailed Reports**: Comprehensive vulnerability reports with severity levels
- **Dark Mode**: Full dark mode support with system preference detection
- **Responsive Design**: Optimized for all devices from mobile to desktop
- **Real-time Updates**: Live scanning status and progress tracking

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **React Router** - Client-side routing and navigation
- **Tailwind CSS** - Utility-first CSS framework with dark mode support
- **Lucide React** - Beautiful, customizable icons
- **Vite** - Fast build tool and development server

### Backend (Integration Ready)
- **Flask** - Lightweight Python web framework
- **Google Cloud Firestore** - NoSQL document database
- **Python AI Models** - Custom vulnerability detection models
- **GitHub API** - Repository cloning and management

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/anzen.git
   cd anzen
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:5173`

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎨 Design Features

- **Apple-level Design Aesthetics** - Clean, sophisticated visual presentation
- **Micro-interactions** - Smooth animations and hover effects
- **Consistent Color System** - Professional blue (#3B82F6) primary with semantic colors
- **Typography Hierarchy** - Clear visual hierarchy with proper spacing
- **Responsive Grid System** - Adapts seamlessly across all viewport sizes
- **Dark Mode Support** - Automatic system preference detection with manual toggle

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🔐 Security Features

- **Input Validation** - GitHub URL validation and sanitization
- **Error Handling** - Comprehensive error states and user feedback
- **Loading States** - Clear progress indicators for all async operations
- **Secure Authentication** - Mock authentication ready for backend integration

## 🚀 Deployment

The frontend is ready for deployment to any static hosting service:

- **Netlify** - Recommended for automatic deployments
- **Vercel** - Great for React applications
- **GitHub Pages** - Free hosting for public repositories
- **AWS S3** - Scalable cloud hosting

## 📚 Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Navbar.jsx      # Navigation component
├── contexts/           # React contexts
│   └── ThemeContext.jsx # Dark mode theme provider
├── pages/              # Page components
│   ├── Login.jsx       # Authentication pages
│   ├── Signup.jsx
│   ├── Dashboard.jsx   # Main dashboard
│   ├── AddRepository.jsx
│   └── RepositoryDetail.jsx
├── App.jsx             # Main application component
├── main.jsx           # Application entry point
└── index.css          # Global styles and Tailwind imports
```

## 🔗 Backend Integration

See [Backend Integration Guide](./docs/BACKEND_INTEGRATION.md) for detailed instructions on connecting the Flask backend.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tailwind CSS** for the excellent utility-first CSS framework
- **Lucide** for the beautiful icon set
- **React Team** for the amazing framework
- **Vite** for the lightning-fast build tool