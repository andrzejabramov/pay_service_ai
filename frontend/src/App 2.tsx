import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LoginForm } from "./features/auth/LoginForm";
import { RegisterForm } from "./features/auth/RegisterForm";
import { ProtectedRoute } from "./routes/ProtectedRoute";

// Заглушка для главной страницы
function Dashboard() {
  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold">Добро пожаловать в PayServices!</h1>
      <p>Здесь будет дашборд с таблицей пользователей и контрактами.</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
