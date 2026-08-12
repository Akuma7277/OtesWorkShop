import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { placeOrder } from '../api'
import { haptic } from '../tg'

export default function CartPage() {
  const { cart, updateCartGrams, removeFromCart, clearCart, cartTotal, user, showToast, loadBalance } = useApp()
  const [address, setAddress] = useState(user?.address || '')
  const [placing, setPlacing] = useState(false)
  const navigate = useNavigate()

  const handlePlaceOrder = async () => {
    if (cart.length === 0) return
    if (!address.trim()) { showToast('❌ Yetkazib berish manzilini kiriting'); return }
    haptic.medium()
    setPlacing(true)
    try {
      const items = cart.map(i => ({ product_id: i.product.id, grams: i.grams }))
      const order = await placeOrder({ items, delivery_address: address })
      clearCart()
      await loadBalance()
      haptic.success()
      showToast('✅ Buyurtma muvaffaqiyatli qabul qilindi!')
      navigate(`/orders/${order.id}`)
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setPlacing(false)
    }
  }

  if (cart.length === 0) {
    return (
      <div className="page-content fade-in">
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <div className="empty-state-title">Savat bo'sh</div>
          <div className="empty-state-desc">Mahsulotlar qo'shish uchun do'konga o'ting</div>
          <button className="btn btn-primary mt-4" onClick={() => navigate('/shop')}>
            🛍️ Do'konga o'tish
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4">
        <h1 className="section-title">🛒 Savat</h1>
        <button className="section-link" style={{ color: 'var(--accent-red)' }} onClick={() => { haptic.light(); clearCart() }}>
          Tozalash
        </button>
      </div>

      {/* Cart Items */}
      <div className="stagger mb-4">
        {cart.map(({ product, grams }) => {
          const subtotal = grams * Number(product.sale_price_per_gram)
          return (
            <div key={product.id} className="cart-item">
              <div className="cart-item-image">
                {product.image_url ? <img src={product.image_url} alt={product.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : '🍃'}
              </div>
              <div className="cart-item-info">
                <div className="cart-item-name">{product.name}</div>
                <div className="cart-item-price">{Number(product.sale_price_per_gram).toFixed(0)} so'm/g</div>
                <div style={{ fontSize: 13, fontWeight: 700, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginTop: 2 }}>
                  {subtotal.toFixed(0)} so'm
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                <div className="qty-control">
                  <button className="qty-btn" onClick={() => { haptic.light(); updateCartGrams(product.id, grams - 10) }}>−</button>
                  <span className="qty-value">{grams}g</span>
                  <button className="qty-btn" onClick={() => { haptic.light(); updateCartGrams(product.id, grams + 10) }}>+</button>
                </div>
                <button
                  onClick={() => { haptic.light(); removeFromCart(product.id) }}
                  style={{ background: 'none', border: 'none', color: 'var(--accent-red)', cursor: 'pointer', fontSize: 18 }}
                >
                  🗑
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Delivery address */}
      <div className="input-group">
        <label className="input-label">📍 Yetkazib berish manzili</label>
        <textarea
          className="input"
          rows={3}
          placeholder="Aniq manzilni kiriting..."
          value={address}
          onChange={e => setAddress(e.target.value)}
          style={{ resize: 'none' }}
        />
      </div>

      {/* Order summary */}
      <div className="card mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-secondary">Mahsulotlar:</span>
          <span className="font-bold">{cart.length} xil</span>
        </div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-secondary">Jami gramm:</span>
          <span className="font-bold">{cart.reduce((s, i) => s + i.grams, 0)} g</span>
        </div>
        <div className="divider" />
        <div className="flex justify-between items-center">
          <span style={{ fontWeight: 700, fontSize: 16 }}>Jami summa:</span>
          <span style={{ fontSize: 22, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            {cartTotal.toFixed(0)} so'm
          </span>
        </div>
      </div>

      <button
        className="btn btn-primary btn-full btn-lg"
        onClick={handlePlaceOrder}
        disabled={placing}
      >
        {placing ? '⏳ Joylashtirilmoqda...' : `✅ Buyurtma berish — ${cartTotal.toFixed(0)} so'm`}
      </button>
    </div>
  )
}
