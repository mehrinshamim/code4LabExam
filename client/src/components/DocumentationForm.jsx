"use client"

function DocumentationForm({
  question,
  setQuestion,
  code,
  setCode,
  handleSubmit,
  isLoading,
}) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Input</h2>
      <p className="text-gray-600 mb-4">Enter your lab question and code (if available)</p>

      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1">
              Lab Question
            </label>
            <textarea
              id="question"
              placeholder="Paste your OS lab question here..."
              className="w-full min-h-[120px] px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
              Your Code (Optional)
            </label>
            <textarea
              id="code"
              placeholder="If you have working code, paste it here..."
              className="w-full min-h-[200px] px-3 py-2 text-gray-700 border rounded-lg font-mono focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </div>
        </div>

        <button
          type="submit"
          className={`w-full mt-6 py-2 px-4 rounded-md text-white font-medium ${
            isLoading
              ? "bg-purple-400 cursor-not-allowed"
              : "bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
          }`}
          disabled={isLoading || !question}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generating Documentation...
            </div>
          ) : (
            "Generate Documentation"
          )}
        </button>
      </form>
    </div>
  )
}

export default DocumentationForm

