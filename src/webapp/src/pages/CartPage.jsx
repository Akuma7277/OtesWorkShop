import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { placeOrder } from '../api'
import { haptic } from '../tg'
import Spinner from '../components/Spinner'
import { t, getLanguage } from '../i18n'

export default function CartPage() {
  const { cart, removeFromCart, updateCartGrams, clearCart, cartTotal, loadBalance, showToast, lang } = useApp()
  const [address, setAddress] = useState('')
  const [placing, setPlacing] = useState(false)
  const navigate = useNavigate()

  if (cart.length === 0) {
    return (
      <div className="page-content fade-in">
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <div className="empty-state-title">{t('cart_empty')}</div>
          <div className="empty-state-desc">{t('cart_empty_desc')}</div>
          <button className="btn btn-primary mt-4" onClick={() => { haptic.light(); navigate('/shop') }}>
            {t('go_to_shop')}
          </button>
        </div>
      </div>
    )
  }

  const handlePlaceOrder = async () => {
    if (!address.trim()) {
      showToast(lang === 'ru' ? '❌ Введите адрес доставки' : '❌ Yetkazib berish manzilingizni kiriting')
      return
    }

    haptic.medium()
    setPlacing(true)
    try {
      const items = cart.map(i => ({
        product_id: i.product.id,
        grams: i.grams
      }))
      await placeOrder({
        items,
        delivery_address: address.trim()
      })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Заказ успешно оформлен!' : '✅ Buyurtma muvaffaqiyatli qabul qilindi!')
      clearCart()
      await loadBalance()
      navigate('/orders')
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setPlacing(false)
    }
  }

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4">
        <h1 className="section-title">🛒 {t('cart')}</h1>
        <button className="section-link" style={{ color: 'var(--accent-red)' }} onClick={() => { haptic.light(); clearCart() }}>
          {t('clear')}
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
                <div className="cart-item-price">{Number(product.sale_price_per_gram).toFixed(1)} $/g</div>
                <div style={{ fontSize: 13, fontWeight: 700, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginTop: 2 }}>
                  {subtotal.toFixed(1)} $
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
        <label className="input-label">📍 {t('delivery_address')}</label>
        <textarea
          className="input"
          rows={3}
          placeholder={t('address_placeholder')}
          value={address}
          onChange={e => setAddress(e.target.value)}
          style={{ resize: 'none' }}
        />
      </div>

      {/* Order summary */}
      <div className="card mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-secondary">{lang === 'ru' ? 'Товары:' : 'Mahsulotlar:'}</span>
          <span className="font-bold">{cart.length} {lang === 'ru' ? 'вид(а)' : 'xil'}</span>
        </div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-secondary">{lang === 'ru' ? 'Общий вес:' : 'Jami gramm:'}</span>
          <span className="font-bold">{cart.reduce((s, i) => s + i.grams, 0)} g</span>
        </div>
        <div className="divider" />
        <div className="flex justify-between items-center">
          <span style={{ fontWeight: 700, fontSize: 16 }}>{t('total_amount')}:</span>
          <span style={{ fontSize: 22, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            {cartTotal.toFixed(1)} $
          </span>
        </div>
      </div>

      <button
        className="btn btn-primary btn-full btn-lg"
        onClick={handlePlaceOrder}
        disabled={placing}
      >
        {placing ? `⏳ ${t('placing_order')}` : `🛒 ${t('place_order')} — ${cartTotal.toFixed(1)} $`}
      </button>
    </div>
  )
}
