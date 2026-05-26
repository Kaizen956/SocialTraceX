export default function Dashboard() {
  const stats = [
    { label: 'TOTAL CASES', value: '1', color: 'white' },
    { label: 'ACTIVE', value: '1', color: 'green' },
    { label: 'ENTRIES CAPTURED', value: '0', color: 'blue' },
    { label: 'CLOSED', value: '0', color: 'orange' }
  ];

  const cases = [
    {
      id: 1,
      title: 'fjdsopajfo',
      platform: 'Instagram',
      target: '@jays_kaizen',
      status: 'ACTIVE',
      entries: 0,
      lastCapture: '2026-04-30 06:14'
    }
  ];

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

      {/* Main Content */}
      <div className="size-full relative z-10 overflow-y-auto">
        {/* Top Navigation */}
        <nav className="backdrop-blur-xl bg-white/[0.02] border-b border-white/10 px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full border-2 border-purple-400"></div>
                <span className="text-white" style={{ fontFamily: 'Orbitron, monospace' }}>
                  SocialtrackX <span className="text-purple-400/60 text-sm">v1.0</span>
                </span>
              </div>
              <a href="#" className="text-purple-300 hover:text-purple-200 transition-colors">
                Dashboard
              </a>
              <a href="#" className="text-purple-400/60 hover:text-purple-300 transition-colors">
                New Case
              </a>
            </div>
            <div className="flex items-center gap-6">
              <span className="text-purple-300/70 text-sm">Lead Examiner</span>
              <button className="text-purple-400/60 hover:text-purple-300 transition-colors text-sm">
                Logout
              </button>
            </div>
          </div>
        </nav>

        {/* Dashboard Content */}
        <div className="px-8 py-8 max-w-[1400px] mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl text-white mb-1" style={{ fontFamily: 'Orbitron, monospace' }}>
                Investigation Dashboard
              </h1>
              <p className="text-purple-300/60">Welcome, Lead Examiner</p>
            </div>
            <button
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500/30 to-blue-600/30 border border-blue-400/50 text-white backdrop-blur-md hover:from-blue-500/40 hover:to-blue-600/40 hover:border-blue-400/70 hover:scale-105 transition-all duration-300"
              style={{
                boxShadow: '0 0 20px rgba(59, 130, 246, 0.3)',
              }}
            >
              + New Case
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="backdrop-blur-xl bg-white/[0.02] border rounded-xl p-6 hover:bg-white/[0.04] transition-all duration-300"
                style={{
                  borderColor:
                    stat.color === 'green' ? 'rgba(34, 197, 94, 0.2)' :
                    stat.color === 'blue' ? 'rgba(59, 130, 246, 0.2)' :
                    stat.color === 'orange' ? 'rgba(249, 115, 22, 0.2)' :
                    'rgba(255, 255, 255, 0.1)'
                }}
              >
                <div
                  className="text-4xl mb-2"
                  style={{
                    fontFamily: 'Orbitron, monospace',
                    color:
                      stat.color === 'green' ? '#22c55e' :
                      stat.color === 'blue' ? '#3b82f6' :
                      stat.color === 'orange' ? '#f97316' :
                      '#ffffff'
                  }}
                >
                  {stat.value}
                </div>
                <div className="text-xs text-purple-300/50 tracking-wider">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          {/* Cases Table */}
          <div className="backdrop-blur-xl bg-white/[0.02] border border-white/10 rounded-xl overflow-hidden">
            {/* Table Header */}
            <div className="grid grid-cols-[60px_1fr_150px_150px_120px_100px_180px_150px] gap-4 px-6 py-4 border-b border-white/10 text-xs text-purple-300/50 uppercase tracking-wider">
              <div>#</div>
              <div>Case Title</div>
              <div>Platform</div>
              <div>Target</div>
              <div>Status</div>
              <div>Entries</div>
              <div>Last Capture</div>
              <div>Actions</div>
            </div>

            {/* Table Rows */}
            {cases.map((caseItem) => (
              <div
                key={caseItem.id}
                className="grid grid-cols-[60px_1fr_150px_150px_120px_100px_180px_150px] gap-4 px-6 py-4 border-b border-white/5 hover:bg-white/[0.02] transition-all text-purple-200/90"
              >
                <div className="text-purple-400/60">{caseItem.id}</div>
                <div className="text-white">{caseItem.title}</div>
                <div>
                  <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-400/30 text-purple-300 text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2c2.717 0 3.056.01 4.122.06 1.065.05 1.79.217 2.428.465.66.254 1.216.598 1.772 1.153a4.908 4.908 0 0 1 1.153 1.772c.247.637.415 1.363.465 2.428.047 1.066.06 1.405.06 4.122 0 2.717-.01 3.056-.06 4.122-.05 1.065-.218 1.79-.465 2.428a4.883 4.883 0 0 1-1.153 1.772 4.915 4.915 0 0 1-1.772 1.153c-.637.247-1.363.415-2.428.465-1.066.047-1.405.06-4.122.06-2.717 0-3.056-.01-4.122-.06-1.065-.05-1.79-.218-2.428-.465a4.89 4.89 0 0 1-1.772-1.153 4.904 4.904 0 0 1-1.153-1.772c-.248-.637-.415-1.363-.465-2.428C2.013 15.056 2 14.717 2 12c0-2.717.01-3.056.06-4.122.05-1.066.217-1.79.465-2.428a4.88 4.88 0 0 1 1.153-1.772A4.897 4.897 0 0 1 5.45 2.525c.638-.248 1.362-.415 2.428-.465C8.944 2.013 9.283 2 12 2zm0 5a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm6.5-.25a1.25 1.25 0 0 0-2.5 0 1.25 1.25 0 0 0 2.5 0zM12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"/>
                    </svg>
                    Instagram
                  </span>
                </div>
                <div className="text-purple-300/80">{caseItem.target}</div>
                <div>
                  <span className="inline-block px-3 py-1 rounded-full bg-green-500/20 border border-green-400/40 text-green-400 text-xs uppercase tracking-wider">
                    {caseItem.status}
                  </span>
                </div>
                <div className="text-purple-300/70">{caseItem.entries}</div>
                <div className="text-purple-300/70 text-sm">{caseItem.lastCapture}</div>
                <div className="flex gap-2">
                  <button className="px-4 py-1.5 rounded-lg bg-white/5 border border-blue-400/30 text-blue-300 backdrop-blur-md hover:bg-white/10 hover:border-blue-400/50 hover:scale-105 transition-all duration-300 text-sm">
                    View
                  </button>
                  <button className="px-4 py-1.5 rounded-lg bg-white/5 border border-white/10 text-purple-300 backdrop-blur-md hover:bg-white/10 hover:border-white/20 hover:scale-105 transition-all duration-300 text-sm">
                    Report
                  </button>
                </div>
              </div>
            ))}
          </div>
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
