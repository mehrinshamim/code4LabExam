"use client"

import { useState } from "react"
import Header from "./components/Header"
import Footer from "./components/Footer"
import DocumentationForm from "./components/DocumentationForm"
import DocumentationViewer from "./components/DocumentationViewer"

function App() {
  const [question, setQuestion] = useState("")
  const [code, setCode] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [documentation, setDocumentation] = useState([])

  const [sections, setSections] = useState({
    overview: true,
    shortAlgorithm: true,
    detailedAlgorithm: true,
    code: true,
    requiredModules: true,
    variablesAndConstants: true,
    functions: true,
    explanation: true,
  })

  const handleSectionChange = (section) => {
    setSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('https://code4labexam.onrender.com/generate-documentation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          code: code || null,
          options: sections
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate documentation');
      }

      const result = await response.json();
      
      // Transform the API response to match our documentation viewer format
      const formattedDocs = [
        { title: 'Question Overview & Concepts', content: result.overview || '' },
        { title: 'Short Algorithm', content: result.shortAlgorithm || '' },
        { title: 'Detailed Algorithm', content: result.detailedAlgorithm || '' },
        { title: 'Code', content: result.code || '' },
        { title: 'Required Modules', content: result.requiredModules || '' },
        { title: 'Variables & Constants', content: result.variablesAndConstants || '' },
        { title: 'Functions', content: result.functions || '' },
        { title: 'Code Explanation', content: result.explanation || '' }
      ].filter(doc => doc.content); // Remove empty sections

      setDocumentation(formattedDocs);
    } catch (error) {
      console.error("Error generating documentation:", error);
      // You might want to show an error message to the user
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-grow container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">OS Lab Practice Code Generator</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <DocumentationForm
            question={question}
            setQuestion={setQuestion}
            code={code}
            setCode={setCode}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
          />

          <DocumentationViewer 
            documentation={documentation} 
            isLoading={isLoading}
            question={question}
            sections={sections}
            handleSectionChange={handleSectionChange}
          />
        </div>
      </main>

      <Footer />
    </div>
  )
}

export default App

