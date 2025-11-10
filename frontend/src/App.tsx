import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/room/:code" element={<div className="p-8">Room page coming soon...</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
