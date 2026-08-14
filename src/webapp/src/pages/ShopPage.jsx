import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getProducts, getCategories } from '../api'
import { useApp } from '../context/AppContext'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { t } from '../i18n'

export default function ShopPage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCat, setSelectedCat] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { lang } = useApp()

  useEffect(() => {
    getCategories()
      .then(data => setCategories(data || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = { is_active: true }
    if (selectedCat) params.category_id = selectedCat
    if (search) params.search = search

    const timer = setTimeout(() => {
      getProducts(params)
        .then(data => setProducts(data?.items || data || []))
        .catch(() => {})
        .finally(() => setLoading(false))
    }, 300)
    return () => clearTimeout(timer)
  }, [selectedCat, search])

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', minHeight: '100%' }}>
      {/* Search bar */}
      <div style={{ padding: '16px 16px 0' }}>
        <input
          className="input"
          placeholder={t('search_placeholder')}
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Category pills */}
      {categories.length > 0 && (
        <div className="scroll-x" style={{ padding: '12px 16px 4px' }}>
          <button
            className="btn btn-sm"
            style={{ flexShrink: 0, ...(selectedCat === null ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
            onClick={() => { haptic.light(); setSelectedCat(null) }}
          >
            {t('all')}
          </button>
          {categories.map(cat => (
            <button
              key={cat.id}
              className="btn btn-sm"
              style={{ flexShrink: 0, ...(selectedCat === cat.id ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
              onClick={() => { haptic.light(); setSelectedCat(cat.id) }}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      <div className="page-content" style={{ paddingTop: 8 }}>
        {loading ? (
          <Spinner text="..." />
        ) : products.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <div className="empty-state-title">{t('empty_products')}</div>
            <div className="empty-state-desc">{t('no_products_desc')}</div>
          </div>
        ) : (
          <div className="grid-2 stagger">
            {products.map(p => (
              <ProductCard key={p.id} product={p} onPress={() => navigate(`/shop/${p.id}`)} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

const TASHKENT_DISTRICTS = [
  { key: 'Chilonzor', uz: 'Chilonzor', ru: 'Чиланзар' },
  { key: 'Yunusobod', uz: 'Yunusobod', ru: 'Юнусабад' },
  { key: 'MirzoUlugbek', uz: 'M. Ulug\'bek', ru: 'М. Улугбек' },
  { key: 'Mirobod', uz: 'Mirobod', ru: 'Мирабад' },
  { key: 'Yashnobod', uz: 'Yashnobod', ru: 'Яшнабад' },
  { key: 'Yakkasaroy', uz: 'Yakkasaroy', ru: 'Яккасарай' },
  { key: 'Uchtepa', uz: 'Uchtepa', ru: 'Учтепа' },
  { key: 'Shayxontohur', uz: 'Shayxontohur', ru: 'Шайхантахур' },
  { key: 'Olmazor', uz: 'Olmazor', ru: 'Алмазар' },
  { key: 'Sergeli', uz: 'Sergeli', ru: 'Сергели' },
  { key: 'Yangihayot', uz: 'Yangihayot', ru: 'Янгихаёт' },
  { key: 'Bektemir', uz: 'Bektemir', ru: 'Бектемир' },
]

function ProductCard({ product, onPress }) {
  const { lang } = useApp()
  const hasImage = !!product.image_url
  const stock = Number(product.stock_grams)
  const isOut = stock <= 0
  const isLow = !isOut && stock < 100

  return (
    <div className="product-card" onClick={() => { haptic.light(); onPress() }}>
      <div className="product-image-placeholder">
        {hasImage ? <img src={product.image_url} alt={product.name} /> : <span>🍃</span>}
      </div>
      {isLow && <div className="product-badge" style={{ background: 'var(--gradient-gold)' }}>{t('stock_low')}</div>}
      {isOut && <div className="product-badge" style={{ background: 'linear-gradient(135deg,#f87171,#ef4444)' }}>{t('stock_none')}</div>}
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        {product.description && (
          <div className="text-xs text-muted mb-2 truncate">{product.description}</div>
        )}
        {product.pickup_address && (
          <div style={{ fontSize: 10, color: 'var(--accent-primary)', marginBottom: 4, fontWeight: 700 }}>
            📍 {TASHKENT_DISTRICTS.find(d => d.key === product.pickup_address)?.[lang] || product.pickup_address}
          </div>
        )}
        <div className="product-price">{Number(product.sale_price_per_gram).toFixed(1)} $/g</div>
        <div className={`product-stock ${isOut ? 'out' : isLow ? 'low' : 'ok'}`}>
          {isOut ? `❌ ${t('stock_none')}` : isLow ? `⚠️ ${t('stock_low')} (${stock.toFixed(0)} g)` : `✅ ${stock.toFixed(0)} g`}
        </div>
      </div>
    </div>
  )
}
