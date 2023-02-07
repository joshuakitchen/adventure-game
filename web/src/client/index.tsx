import React, { FC } from 'react'
import { createRoot } from 'react-dom/client'
import { Route, Routes } from 'react-router'
import { BrowserRouter } from 'react-router-dom'
import { library } from '@fortawesome/fontawesome-svg-core'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { GamePage, LoginPage, RegisterPage } from './pages'
import { UserProvider } from './user'

library.add(far, fas)

const root = createRoot(document.getElementById('react-root'))

const Application: FC<{}> = function Application() {
  return (
    <Routes>
      <Route path='/' element={<GamePage />} />
      <Route path='/login' element={<LoginPage />} />
      <Route path='/register' element={<RegisterPage />} />
    </Routes>
  )
}

root.render(
  <UserProvider>
    <BrowserRouter>
      <Application />
    </BrowserRouter>
  </UserProvider>
)
