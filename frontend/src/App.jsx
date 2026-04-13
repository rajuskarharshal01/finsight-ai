import React, { useState } from 'react';
import Header from './components/Header';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <div className="app">
      <Header
        onNavigate={setCurrentPage}
        currentPage={currentPage}
      />
      <main>
        {currentPage === 'home' && <Home />}
        {currentPage === 'analysis' && <Analysis />}
      </main>
    </div>
  );
}

export default App;