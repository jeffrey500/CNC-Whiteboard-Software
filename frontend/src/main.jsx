import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {BrowserRouter} from 'react-router-dom' // Import the router

createRoot(document.getElementById('root')).render(
    <StrictMode>
        {/* Wrap App with the router */}
        <BrowserRouter>
            <App/>
        </BrowserRouter>
    </StrictMode>,
)