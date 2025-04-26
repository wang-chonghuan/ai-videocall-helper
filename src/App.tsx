import './App.css'

function App() {
  return (
    <div 
      className="flex flex-col bg-blue-100 text-gray-800 font-sans overflow-hidden h-full w-full"
    >
      {/* Custom Title Bar */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-3 py-1 flex justify-between items-center flex-shrink-0">
        <h1 className="text-sm font-semibold text-gray-700">AI Videocall Helper</h1>
        <div className="flex space-x-1">
          <button className="px-2 py-0.5 text-xs rounded text-gray-600 hover:bg-gray-200 transition-colors">
            Login
          </button>
          <button className="px-2 py-0.5 text-xs rounded bg-blue-500 text-white hover:bg-blue-600 transition-colors">
            Register
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-4 overflow-y-auto">
        <div className="max-w-3xl mx-auto">
          {/* Welcome Section */}
          <div className="bg-white rounded-md border border-gray-200 p-4 mb-4">
            <h2 className="text-base font-semibold text-gray-800 mb-1">AI-Powered Video Call Assistant</h2>
            <p className="text-sm text-gray-600">
              Enhance your online meetings with AI-generated responses based on speech and visual context.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[ // Array for easier mapping/modification if needed
              { title: "Voice Analysis", description: "Generate AI responses based on meeting conversations" },
              { title: "Screen Analysis", description: "Create responses from shared screen content" },
              { title: "Personal Context", description: "Create personalized responses based on your background" },
              { title: "Settings", description: "Customize AI response style and preferences" }
            ].map((feature) => (
              <div key={feature.title} className="bg-white rounded-md border border-gray-200 p-3 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer">
                <h3 className="text-sm font-semibold text-blue-600 mb-0.5">{feature.title}</h3>
                <p className="text-xs text-gray-500">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
