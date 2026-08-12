import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AppProvider, useApp } from './context/AppContext'
import Header from './components/Header'
import BottomNav from './components/BottomNav'
import Spinner from './components/Spinner'
import HomePage from './pages/HomePage'
import ShopPage from './pages/ShopPage'
import ProductDetailPage from './pages/ProductDetailPage'
import CartPage from './pages/CartPage'
import OrdersPage from './pages/OrdersPage'
import OrderDetailPage from './pages/OrderDetailPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'

function AppShell() {
  const { loading, error, toast } = useApp()

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100dvh', flexDirection: 'column', gap: 20 }}>
        <div style={{ fontSize: 48 }}>🛍️</div>
        <Spinner text="Shopim yuklanmoqda..." />
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
          <Route path="/orders"     element={<OrdersPage />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/profile"    element={<ProfilePage />} />
          <Route path="/reviews"    element={<ProfilePage />} />
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
