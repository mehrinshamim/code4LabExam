"use client"

import { useState, useRef, useEffect } from "react"
import { jsPDF } from "jspdf"

function DocumentationViewer({ documentation, isLoading, question, sections, handleSectionChange }) {
  const [activeTab, setActiveTab] = useState('Question Overview & Concepts')
  const [showExportOptions, setShowExportOptions] = useState(false)
  const documentationRef = useRef(null)

  useEffect(() => {
    if (documentation.length > 0) {
      const overviewSection = documentation.find(
        section => section.title === 'Question Overview & Concepts'
      )
      setActiveTab(overviewSection ? overviewSection.title : documentation[0].title)
    }
  }, [documentation])

  const generatePDF = async () => {
    if (!documentationRef.current || documentation.length === 0) return

    const pdf = new jsPDF("p", "mm", "a4")
    let yOffset = 10

    // Add title
    pdf.setFontSize(18)
    pdf.text("OS Lab Documentation", 105, yOffset, { align: "center" })
    yOffset += 15

    // Add the question
    if (question) {
      pdf.setFontSize(12)
      pdf.text("Question:", 10, yOffset)
      yOffset += 7
      
      pdf.setFontSize(10)
      const questionLines = pdf.splitTextToSize(question, 190)
      pdf.text(questionLines, 10, yOffset)
      yOffset += questionLines.length * 5 + 10
    }

    // Process each section based on user's selection
    for (const section of documentation) {
      // Map section titles to option keys
      const optionKey = {
        'Question Overview & Concepts': 'overview',
        'Short Algorithm': 'shortAlgorithm',
        'Detailed Algorithm': 'detailedAlgorithm',
        'Code': 'code',
        'Required Modules': 'requiredModules',
        'Variables & Constants': 'variablesAndConstants',
        'Functions': 'functions',
        'Code Explanation': 'explanation'
      }[section.title]

      // Skip if this section wasn't selected
      if (!sections[optionKey]) continue

      // Check if we need a new page
      if (yOffset > 280) {
        pdf.addPage()
        yOffset = 10
      }

      // Add section title
      pdf.setFontSize(14)
      pdf.text(section.title, 10, yOffset)
      yOffset += 10

      // Add section content
      pdf.setFontSize(10)
      const splitContent = pdf.splitTextToSize(section.content, 190)

      // Check if we need a new page
      if (yOffset + splitContent.length * 5 > 280) {
        pdf.addPage()
        yOffset = 10
      }

      pdf.text(splitContent, 10, yOffset)
      yOffset += splitContent.length * 5 + 10

      // Add some space between sections
      if (yOffset > 280) {
        pdf.addPage()
        yOffset = 10
      }
    }

    pdf.save("os-lab-documentation.pdf")
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Documentation</h2>

        {documentation.length > 0 && (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowExportOptions(!showExportOptions)}
              className="flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
              </svg>
              Export Options
            </button>
            
            <button
              onClick={generatePDF}
              className="flex items-center px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z"
                  clipRule="evenodd"
                />
              </svg>
              Generate PDF
            </button>
          </div>
        )}
      </div>

      <p className="text-gray-600 mb-4">Generated documentation for your lab exam preparation</p>

      {/* Export Options Panel */}
      {showExportOptions && documentation.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg mb-4 border border-gray-200">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Select Sections for PDF Export</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="overview"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.overview}
                onChange={() => handleSectionChange("overview")}
              />
              <label htmlFor="overview" className="ml-2 text-sm text-gray-700">
                Overview
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="shortAlgorithm"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.shortAlgorithm}
                onChange={() => handleSectionChange("shortAlgorithm")}
              />
              <label htmlFor="shortAlgorithm" className="ml-2 text-sm text-gray-700">
                Short Algorithm
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="detailedAlgorithm"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.detailedAlgorithm}
                onChange={() => handleSectionChange("detailedAlgorithm")}
              />
              <label htmlFor="detailedAlgorithm" className="ml-2 text-sm text-gray-700">
                Detailed Algorithm
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="code"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.code}
                onChange={() => handleSectionChange("code")}
              />
              <label htmlFor="code" className="ml-2 text-sm text-gray-700">
                Code
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="requiredModules"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.requiredModules}
                onChange={() => handleSectionChange("requiredModules")}
              />
              <label htmlFor="requiredModules" className="ml-2 text-sm text-gray-700">
                Required Modules
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="variablesAndConstants"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.variablesAndConstants}
                onChange={() => handleSectionChange("variablesAndConstants")}
              />
              <label htmlFor="variablesAndConstants" className="ml-2 text-sm text-gray-700">
                Variables & Constants
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="functions"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.functions}
                onChange={() => handleSectionChange("functions")}
              />
              <label htmlFor="functions" className="ml-2 text-sm text-gray-700">
                Functions
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="explanation"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                checked={sections.explanation}
                onChange={() => handleSectionChange("explanation")}
              />
              <label htmlFor="explanation" className="ml-2 text-sm text-gray-700">
                Code Explanation
              </label>
            </div>
          </div>
        </div>
      )}

      <div ref={documentationRef} className="min-h-[400px]">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            <p className="mt-4 text-gray-500">Analyzing and generating documentation...</p>
          </div>
        ) : documentation.length > 0 ? (
          <div>
            <div className="flex flex-wrap border-b">
              {documentation.map((section) => (
                <button
                  key={section.title}
                  className={`px-4 py-2 text-sm font-medium ${
                    activeTab === section.title
                      ? "border-b-2 border-purple-600 text-purple-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                  onClick={() => setActiveTab(section.title)}
                >
                  {section.title}
                </button>
              ))}
            </div>

            <div className="mt-4">
              {documentation.map((section) => (
                <div key={section.title} className={`${activeTab === section.title ? "block" : "hidden"}`}>
                  <h3 className="text-lg font-medium mb-3">{section.title}</h3>
                  <div className="whitespace-pre-wrap text-gray-700">{section.content}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mx-auto text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p>Enter a question and click "Generate Documentation" to get started.</p>
            <p className="mt-2 text-sm">
              The AI will analyze your question and code to create comprehensive documentation.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentationViewer