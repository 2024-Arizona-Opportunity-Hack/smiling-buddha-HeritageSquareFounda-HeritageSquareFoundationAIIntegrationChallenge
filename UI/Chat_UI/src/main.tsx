import React, { ReactNode, useState } from 'react'
import ReactDOM from 'react-dom/client'
import Container from './Container.tsx'
import './index.scss';


import {
  BrowserRouter as Router,
  Route,
  Navigate,
  Routes,
  BrowserRouter,
} from "react-router-dom";
import { Provider } from 'react-redux';
import { store } from './store/store.ts';
import { FOVUS_AUTHENTICATED, FOVUS_IDTOKEN } from './session.const.ts';
import { Login } from './Login.tsx';
import { SignUp } from './SignUp.tsx';


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
    {/* <Container />
     */}

<BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        <Route
          path="/signup"
          element={
            <PublicRoute>
              <SignUp />
            </PublicRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <Container />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)


interface RouteProps {
  children: ReactNode;
}



function PrivateRoute({ children }: RouteProps) {
  const isUserAuthenticated: boolean =
    !!sessionStorage.getItem(FOVUS_IDTOKEN) &&
    sessionStorage.getItem(FOVUS_AUTHENTICATED) == "true";
  // console.log("PrivateRoute");

  const [isAuthenticated, setIsAuthenticated] = useState(isUserAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/" />;
}

function PublicRoute({ children }: RouteProps) {
  const isUserAuthenticated: boolean =
    !!sessionStorage.getItem(FOVUS_IDTOKEN) &&
    sessionStorage.getItem(FOVUS_AUTHENTICATED) == "true";
  const [isAuthenticated, setIsAuthenticated] = useState(isUserAuthenticated);
  return isAuthenticated ? <Navigate to="/chat" /> : <>{children}</>;
}
