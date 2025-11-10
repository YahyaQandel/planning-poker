import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { ThemeProvider } from './components/ThemeProvider';
import HomeModern from './pages/HomeModern';
import RoomModern from './pages/RoomModern';

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="planning-poker-theme">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomeModern />} />
          <Route path="/room/:code" element={<RoomModern />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </ThemeProvider>
  );
}

export default App;
