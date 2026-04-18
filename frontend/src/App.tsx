import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Admin from './pages/Admin'
import SubmitEvent from './pages/SubmitEvent'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/sugerir" element={<SubmitEvent />} />
    </Routes>
  )
}
