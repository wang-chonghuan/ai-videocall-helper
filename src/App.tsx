import './App.css'

function App() {
  return (
    <div className="flex flex-col h-screen bg-gray-100 p-6 overflow-hidden">
      {/* Header */}
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-blue-600">Online Meeting Helper</h1>
        <div className="flex space-x-2">
          <button className="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded hover:bg-blue-600 transition">
            Login
          </button>
          <button className="px-4 py-2 text-sm font-medium text-blue-600 bg-white border border-blue-500 rounded hover:bg-blue-50 transition">
            Register
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">AI-Powered Meeting Assistant</h2>
          <p className="text-gray-600 mb-4">
            Enhance your online meetings with AI-generated responses based on speech and visual context.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer transition">
              <h3 className="font-medium mb-2">Voice Analysis</h3>
              <p className="text-sm text-gray-500">Generate AI responses based on meeting conversations</p>
            </div>
            <div className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer transition">
              <h3 className="font-medium mb-2">Screen Analysis</h3>
              <p className="text-sm text-gray-500">Create responses from shared screen content</p>
            </div>
            <div className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer transition">
              <h3 className="font-medium mb-2">Personal Context</h3>
              <p className="text-sm text-gray-500">Create personalized responses based on your background</p>
            </div>
            <div className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer transition">
              <h3 className="font-medium mb-2">Settings</h3>
              <p className="text-sm text-gray-500">Customize AI response style and preferences</p>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="mt-6 text-center text-sm text-gray-500">
        <p>Online Meeting Helper &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App
