import { useState } from 'react';
import Dashboard from './components/Dashboard';

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login attempt:', { username, password });
    setIsLoggedIn(true);
  };

  if (isLoggedIn) {
    return <Dashboard />;
  }

  return (
    <div className="size-full relative overflow-hidden bg-gradient-to-br from-black via-purple-950 to-black">
      {/* Floating Triangles Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div
          className="absolute w-64 h-64 border border-white/10 bg-gradient-to-br from-purple-500/5 to-transparent backdrop-blur-sm"
          style={{
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            top: '10%',
            left: '15%',
            animation: 'float-1 20s ease-in-out infinite, pulse-glow-1 6s ease-in-out infinite'
          }}
        />
        <div
          className="absolute w-48 h-48 border border-purple-400/10 bg-gradient-to-br from-purple-600/5 to-transparent backdrop-blur-sm"
          style={{
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            top: '60%',
            right: '20%',
            animation: 'float-2 25s ease-in-out infinite, pulse-glow-2 7s ease-in-out infinite'
          }}
        />
        <div
          className="absolute w-56 h-56 border border-purple-300/10 bg-gradient-to-br from-purple-400/5 to-transparent backdrop-blur-sm"
          style={{
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            bottom: '15%',
            left: '25%',
            animation: 'float-3 22s ease-in-out infinite, pulse-glow-3 8s ease-in-out infinite'
          }}
        />
        <div
          className="absolute w-40 h-40 border border-white/10 bg-gradient-to-br from-purple-500/5 to-transparent backdrop-blur-sm"
          style={{
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            top: '35%',
            right: '10%',
            animation: 'float-4 18s ease-in-out infinite, pulse-glow-1 6.5s ease-in-out infinite'
          }}
        />
        <div
          className="absolute w-52 h-52 border border-purple-400/10 bg-gradient-to-br from-purple-600/5 to-transparent backdrop-blur-sm"
          style={{
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            top: '5%',
            right: '35%',
            animation: 'float-5 28s ease-in-out infinite, pulse-glow-2 7.5s ease-in-out infinite'
          }}
        />
      </div>

      {/* Login Container */}
      <div className="size-full flex items-center justify-center relative z-10">
        <div className="w-full max-w-md px-6">
          {/* Logo/Brand */}
          <div className="mb-8 text-center">
            <h1 className="text-5xl mb-2 tracking-wider bg-gradient-to-r from-purple-400 via-pink-300 to-purple-400 bg-clip-text text-transparent" style={{
              fontFamily: 'Orbitron, monospace',
              filter: 'drop-shadow(0 0 20px rgba(168, 85, 247, 0.8)) drop-shadow(0 0 40px rgba(168, 85, 247, 0.5)) drop-shadow(0 0 60px rgba(168, 85, 247, 0.3))'
            }}>
              SocialtrackX
            </h1>
            <p className="text-purple-300 text-sm" style={{ textShadow: '0 0 10px rgba(216, 180, 254, 0.5)' }}>Social Media Intelligence Platform</p>
          </div>

          {/* Glass Login Form */}
          <div className="backdrop-blur-xl bg-white/[0.02] border border-purple-400/30 rounded-2xl p-8 shadow-2xl shadow-purple-500/20" style={{ boxShadow: '0 0 40px rgba(168, 85, 247, 0.2), inset 0 0 40px rgba(168, 85, 247, 0.05)' }}>
            <h2 className="text-2xl mb-6 text-center text-purple-200" style={{
              fontFamily: 'Orbitron, monospace'
            }}>Welcome back investigator</h2>

            <form onSubmit={handleLogin} className="space-y-5">
              {/* Username Input */}
              <div>
                <label htmlFor="username" className="block text-sm mb-2 text-purple-200/90">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-white/5 border border-purple-400/20 text-white placeholder-purple-300/30 focus:outline-none focus:border-purple-400/70 focus:bg-white/10 backdrop-blur-sm transition-all"
                  style={{ boxShadow: '0 0 10px rgba(168, 85, 247, 0.1)' }}
                  placeholder="Enter your username"
                  required
                />
              </div>

              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm mb-2 text-purple-200/90">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-white/5 border border-purple-400/20 text-white placeholder-purple-300/30 focus:outline-none focus:border-purple-400/70 focus:bg-white/10 backdrop-blur-sm transition-all"
                  style={{ boxShadow: '0 0 10px rgba(168, 85, 247, 0.1)' }}
                  placeholder="Enter your password"
                  required
                />
              </div>

              {/* Info Note */}
              <div className="text-center">
                <p className="text-xs text-purple-300/50">
                  Access credentials are provided by administration
                </p>
              </div>

              {/* Login Button */}
              <button
                type="submit"
                className="w-full py-3 rounded-lg bg-gradient-to-r from-purple-500/30 to-pink-500/30 border border-purple-400/50 text-white backdrop-blur-md hover:from-purple-500/40 hover:to-pink-500/40 hover:border-purple-400/70 hover:scale-105 transition-all duration-300 active:scale-[0.98]"
                style={{
                  boxShadow: '0 0 20px rgba(168, 85, 247, 0.4), 0 0 40px rgba(168, 85, 247, 0.2), inset 0 0 20px rgba(168, 85, 247, 0.1)',
                  textShadow: '0 0 10px rgba(255, 255, 255, 0.5)'
                }}
              >
                Sign In
              </button>

              {/* Request Access Button */}
              <button
                type="button"
                className="w-full py-3 rounded-lg bg-white/5 border border-purple-400/30 text-purple-300 backdrop-blur-md hover:bg-white/10 hover:border-purple-400/50 hover:scale-105 transition-all duration-300"
                style={{
                  boxShadow: '0 0 15px rgba(168, 85, 247, 0.2)',
                  textShadow: '0 0 10px rgba(216, 180, 254, 0.5)'
                }}
              >
                Request Access
              </button>
            </form>

            {/* Support Link */}
            <p className="mt-6 text-center text-sm text-purple-300/70">
              Need help?{' '}
              <a href="#" className="text-purple-300 hover:text-purple-200 hover:scale-105 inline-block transition-all duration-300">
                Contact Support
              </a>
            </p>
          </div>

          {/* Footer Note */}
          <p className="mt-6 text-center text-xs text-purple-400/40">
            Secure access to criminal intelligence data
          </p>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes float-1 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(20px, -30px) rotate(5deg); }
          50% { transform: translate(-15px, -50px) rotate(-3deg); }
          75% { transform: translate(30px, -25px) rotate(4deg); }
        }
        @keyframes float-2 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(-25px, 35px) rotate(-4deg); }
          50% { transform: translate(20px, 60px) rotate(3deg); }
          75% { transform: translate(-30px, 40px) rotate(-5deg); }
        }
        @keyframes float-3 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(30px, -20px) rotate(6deg); }
          50% { transform: translate(-20px, -45px) rotate(-4deg); }
          75% { transform: translate(25px, -30px) rotate(3deg); }
        }
        @keyframes float-4 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(-20px, 25px) rotate(-3deg); }
          50% { transform: translate(25px, 45px) rotate(5deg); }
          75% { transform: translate(-15px, 30px) rotate(-4deg); }
        }
        @keyframes float-5 {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(25px, -35px) rotate(4deg); }
          50% { transform: translate(-30px, -55px) rotate(-6deg); }
          75% { transform: translate(20px, -40px) rotate(5deg); }
        }
        @keyframes pulse-glow-1 {
          0%, 100% {
            opacity: 1;
            filter: drop-shadow(0 0 2px rgba(168, 85, 247, 0.1));
          }
          50% {
            opacity: 1;
            filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.6)) drop-shadow(0 0 40px rgba(168, 85, 247, 0.3));
          }
        }
        @keyframes pulse-glow-2 {
          0%, 100% {
            opacity: 1;
            filter: drop-shadow(0 0 2px rgba(147, 51, 234, 0.1));
          }
          50% {
            opacity: 1;
            filter: drop-shadow(0 0 25px rgba(147, 51, 234, 0.6)) drop-shadow(0 0 45px rgba(147, 51, 234, 0.3));
          }
        }
        @keyframes pulse-glow-3 {
          0%, 100% {
            opacity: 1;
            filter: drop-shadow(0 0 2px rgba(192, 132, 252, 0.1));
          }
          50% {
            opacity: 1;
            filter: drop-shadow(0 0 22px rgba(192, 132, 252, 0.6)) drop-shadow(0 0 42px rgba(192, 132, 252, 0.3));
          }
        }
      `}</style>
    </div>
  );
}