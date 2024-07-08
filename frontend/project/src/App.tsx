import { Component } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Header from './parts/Header';
import Home from './pages/Backup';
import Backup from './pages/Backup';
import NotFound from './pages/NotFound';
import './App.css';

export default class App extends Component {
  render() {
    return (
      <BrowserRouter>
        <main cds-layout="vertical gap:lg" cds-text="body">
          <div className="main-container">
            <Header />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/backup" element={<Backup />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </main>
      </BrowserRouter >
    );
  }
}
