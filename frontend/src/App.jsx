import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Scanner from './pages/Scanner'
import Evaluator from './pages/Evaluator'
import CVTailor from './pages/CVTailor'
import Tracker from './pages/Tracker'
import InterviewPrep from './pages/InterviewPrep'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/evaluator" element={<Evaluator />} />
        <Route path="/cv-tailor" element={<CVTailor />} />
        <Route path="/tracker" element={<Tracker />} />
        <Route path="/interview" element={<InterviewPrep />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}
