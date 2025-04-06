"use client"

import { useState } from "react"

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-gradient-to-r from-purple-700 to-indigo-800 text-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z"
                clipRule="evenodd"
              />
            </svg>
            <h1 className="text-xl font-bold">OS Lab Helper</h1>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md hover:bg-purple-600 focus:outline-none"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Desktop navigation */}
          <nav className="hidden md:flex space-x-6">
            <a href="#" className="hover:text-purple-200 font-medium">
              Home
            </a>
            <a href="#" className="hover:text-purple-200 font-medium">
              About
            </a>
            <a href="#" className="hover:text-purple-200 font-medium">
              Resources
            </a>
            <a href="#" className="hover:text-purple-200 font-medium">
              Contact
            </a>
          </nav>
        </div>

        {/* Mobile navigation */}
        {isMenuOpen && (
          <nav className="mt-4 md:hidden">
            <div className="flex flex-col space-y-3">
              <a href="#" className="hover:bg-purple-600 px-3 py-2 rounded-md">
                Home
              </a>
              <a href="#" className="hover:bg-purple-600 px-3 py-2 rounded-md">
                About
              </a>
              <a href="#" className="hover:bg-purple-600 px-3 py-2 rounded-md">
                Resources
              </a>
              <a href="#" className="hover:bg-purple-600 px-3 py-2 rounded-md">
                Contact
              </a>
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}

export default Header

