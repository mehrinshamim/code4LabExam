"use client"

import { useState, useRef } from "react"
import { jsPDF } from "jspdf"

function DocumentationViewer({ documentation, isLoading }) {
  const [activeTab, setActiveTab] = useState(documentation.length > 0 ? documentation[0].title : "")
  const documentationRef = useRef(null)

  const generatePDF = async () => {
    if (!documentationRef.current || documentation.length === 0) return

    const pdf = new jsPDF("p", "mm", "a4")
    let yOffset = 10

    // Add title
    pdf.setFontSize(18)
    pdf.text("OS Lab Documentation", 105, yOffset, { align: "center" })
    yOffset += 15

    // Process each section
    for (const section of documentation) {
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
        )}
      </div>

      <p className="text-gray-600 mb-4">Generated documentation for your lab exam preparation</p>

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

