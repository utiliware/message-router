import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import LandingPage from './templates/landing-page'
import { IdxProvider } from './context'

function App() {
  return (
    <IdxProvider>
      <LandingPage />
    </IdxProvider>
  );
}


export default App
