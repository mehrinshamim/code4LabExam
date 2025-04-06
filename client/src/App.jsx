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
      // Simulate API call to generate documentation
      setTimeout(() => {
        const result = generateMockDocumentation(question, code, sections)
        setDocumentation(result)
        setIsLoading(false)
      }, 2000)
    } catch (error) {
      console.error("Error generating documentation:", error)
      setIsLoading(false)
    }
  }

  // Mock function to simulate documentation generation
  const generateMockDocumentation = (question, code, sections) => {
    const hasCode = code.trim().length > 0
    const docs = []

    if (sections.overview) {
      docs.push({
        title: "Question Overview & Concepts",
        content: `This question is about ${question.includes("memory allocation") ? "memory allocation algorithms" : "operating system concepts"}.`,
      })
    }

    if (sections.shortAlgorithm) {
      docs.push({
        title: "Short Algorithm",
        content:
          "1. Initialize memory blocks\n2. For each process, find the best fit block\n3. Allocate memory and update available blocks",
      })
    }

    if (sections.detailedAlgorithm) {
      docs.push({
        title: "Detailed Algorithm",
        content:
          "1. Initialize an array to represent memory blocks with their sizes\n2. Sort the memory blocks if needed\n3. For each process requiring allocation:\n   a. Find the smallest block that is large enough\n   b. Allocate the process to this block\n   c. Reduce the block size by the process size\n   d. If block size becomes zero, remove it from available blocks\n4. Return the allocation map",
      })
    }

    if (sections.code) {
      docs.push({
        title: "Code",
        content: hasCode
          ? code
          : `// Sample code for memory allocation\nfunction bestFit(blocks, processes) {\n  let allocation = Array(processes.length).fill(-1);\n  \n  for (let i = 0; i < processes.length; i++) {\n    let bestIdx = -1;\n    for (let j = 0; j < blocks.length; j++) {\n      if (blocks[j] >= processes[i]) {\n        if (bestIdx === -1 || blocks[j] < blocks[bestIdx]) {\n          bestIdx = j;\n        }\n      }\n    }\n    \n    if (bestIdx !== -1) {\n      allocation[i] = bestIdx;\n      blocks[bestIdx] -= processes[i];\n    }\n  }\n  \n  return allocation;\n}`,
      })
    }

    if (sections.requiredModules) {
      docs.push({
        title: "Required Modules",
        content:
          "- Standard I/O library\n- Memory management utilities\n- Data structure libraries for arrays and lists",
      })
    }

    if (sections.variablesAndConstants) {
      docs.push({
        title: "Variables & Constants",
        content:
          "- blocks[]: Array storing sizes of available memory blocks\n- processes[]: Array storing sizes of processes to be allocated\n- allocation[]: Array storing the block index where each process is allocated",
      })
    }

    if (sections.functions) {
      docs.push({
        title: "Functions",
        content:
          "- bestFit(): Main function implementing the Best Fit algorithm\n- printAllocation(): Helper function to display the allocation results",
      })
    }

    if (sections.explanation) {
      docs.push({
        title: "Code Explanation",
        content:
          "The code implements the Best Fit memory allocation algorithm:\n\n1. It initializes an allocation array with -1 values (indicating no allocation)\n2. For each process, it finds the smallest block that can accommodate it\n3. When a suitable block is found, it updates the allocation array and reduces the block size\n4. If no suitable block is found, the process remains unallocated (-1)\n5. Finally, it returns the allocation mapping",
      })
    }

    return docs
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-grow container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">OS Lab Exam Documentation Generator</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <DocumentationForm
            question={question}
            setQuestion={setQuestion}
            code={code}
            setCode={setCode}
            sections={sections}
            handleSectionChange={handleSectionChange}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
          />

          <DocumentationViewer documentation={documentation} isLoading={isLoading} />
        </div>
      </main>

      <Footer />
    </div>
  )
}

export default App

