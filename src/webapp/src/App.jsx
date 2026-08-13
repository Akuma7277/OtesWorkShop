import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AppProvider, useApp } from './context/AppContext'
import Header from './components/Header'
import BottomNav from './components/BottomNav'
import Spinner from './components/Spinner'
import HomePage from './pages/HomePage'
import ShopPage from './pages/ShopPage'
import ProductDetailPage from './pages/ProductDetailPage'
import CartPage from './pages/CartPage'
import OrderDetailPage from './pages/OrderDetailPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'
import RegisterPage from './pages/RegisterPage'
import AwaitingApprovalPage from './pages/AwaitingApprovalPage'
import NewsPage from './pages/NewsPage'

function AppShell() {
  const { loading, registrationStatus, toast } = useApp()

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100dvh', flexDirection: 'column', gap: 20 }}>
        <div style={{ fontSize: 48 }}>🍀</div>
        <Spinner text="NexШоп yuklanmoqda..." />
      </div>
    )
  }

  // 1. Force registration if not registered
  if (!registrationStatus.registered) {
    return (
      <div className="app-container">
        <RegisterPage />
        {toast && <div className="toast">{toast}</div>}
      </div>
    )
  }

  // 2. Force awaiting approval screen if status is PENDING
  if (registrationStatus.status === 'PENDING') {
    return (
      <div className="app-container">
        <AwaitingApprovalPage />
        {toast && <div className="toast">{toast}</div>}
      </div>
    )
  }

  return (
    <div className="app-container">
      <Header />
      <main style={{ flex: 1, overflow: 'hidden' }}>
        <Routes>
          <Route path="/"           element={<HomePage />} />
          <Route path="/shop"       element={<ShopPage />} />
          <Route path="/shop/:id"   element={<ProductDetailPage />} />
          <Route path="/cart"       element={<CartPage />} />
          <Route path="/news"       element={<NewsPage />} />
          <Route path="/orders"     element={<ProfilePage initialTab="orders" />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/profile"    element={<ProfilePage initialTab="info" />} />
          <Route path="/reviews"    element={<ProfilePage initialTab="review" />} />
          <Route path="/admin"      element={<AdminPage />} />
        </Routes>
      </main>
      <BottomNav />

      {/* Toast */}
      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AppProvider>
  )
}
