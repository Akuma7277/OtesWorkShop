import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { placeOrder } from '../api'
import { haptic } from '../tg'
import Spinner from '../components/Spinner'
import { t, getLanguage } from '../i18n'

export default function CartPage() {
  const { cart, removeFromCart, updateCartGrams, clearCart, cartTotal, loadBalance, showToast, lang, getProductPriceForGrams } = useApp()
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
    haptic.medium()
    setPlacing(true)
    try {
      const items = cart.map(i => ({
        product_id: i.product.id,
        grams: i.grams
      }))
      await placeOrder({
        items
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
          const subtotal = getProductPriceForGrams(product, grams)
          return (
            <div key={product.id} className="cart-item" style={{ padding: '12px 16px' }}>
              <div className="cart-item-image">
                {product.image_url ? <img src={product.image_url} alt={product.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : '🍃'}
              </div>
              <div className="cart-item-info">
                <div className="cart-item-name">{product.name}</div>
                <div className="cart-item-price">{grams} g</div>
                <div style={{ fontSize: 13, fontWeight: 700, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginTop: 2 }}>
                  {subtotal.toFixed(1)} $
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => { haptic.light(); removeFromCart(product.id) }}
                  style={{ padding: '8px 12px', fontSize: 13 }}
                >
                  {lang === 'ru' ? 'Удалить' : 'O\'chirish'}
                </button>
              </div>
            </div>
          )
        })}
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
