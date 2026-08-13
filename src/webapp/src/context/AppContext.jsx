import { createContext, useContext, useState, useEffect } from 'react'
import { getMe, getBalance } from '../api'
import api from '../api'
import { tgUser } from '../tg'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [user, setUser] = useState(null)
  const [balance, setBalance] = useState(0)
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [registrationStatus, setRegistrationStatus] = useState({ registered: false, status: null, is_admin: false })

  const [lang, setLangState] = useState(localStorage.getItem('shopim_lang') || 'uz')

  useEffect(() => {
    loadUser()
    const handleStorage = () => {
      setLangState(localStorage.getItem('shopim_lang') || 'uz')
    }
    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [])

  const loadUser = async () => {
    try {
      const statusRes = await api.get('/users/status')
      setRegistrationStatus(statusRes)
      setIsAdmin(statusRes?.is_admin || false)

      if (statusRes?.registered && statusRes?.status === 'APPROVED') {
        const me = await getMe()
        setUser(me)
        setIsAdmin(me?.is_admin || false)
        if (me?.language_code && !localStorage.getItem('shopim_lang')) {
          localStorage.setItem('shopim_lang', me.language_code)
          setLangState(me.language_code)
        }
        await loadBalance()
      } else {
        setUser(null)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadBalance = async () => {
    try {
      const data = await getBalance()
      setBalance(data?.balance ?? 0)
    } catch {}
  }

  const showToast = (message, duration = 2500) => {
    setToast(message)
    setTimeout(() => setToast(null), duration)
  }

  // Cart management
  const addToCart = (product, grams) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.product.id === product.id)
      if (existing) {
        return prev.map((i) =>
          i.product.id === product.id ? { ...i, grams: i.grams + grams } : i
        )
      }
      return [...prev, { product, grams }]
    })
    showToast(`✅ ${product.name} savatga qo'shildi`)
  }

  const removeFromCart = (productId) => {
    setCart((prev) => prev.filter((i) => i.product.id !== productId))
  }

  const updateCartGrams = (productId, grams) => {
    if (grams <= 0) {
      removeFromCart(productId)
      return
    }
    setCart((prev) =>
      prev.map((i) => (i.product.id === productId ? { ...i, grams } : i))
    )
  }

  const clearCart = () => setCart([])

  const getProductPriceForGrams = (product, grams) => {
    const basePrice = Number(product.sale_price_per_gram)
    if (grams === 1) return basePrice
    if (grams === 3) return basePrice * 2.0
    if (grams === 5) return basePrice * 3.0
    if (grams === 10) return basePrice * 5.6
    return basePrice * grams
  }

  const cartTotal = cart.reduce(
    (sum, i) => sum + getProductPriceForGrams(i.product, i.grams),
    0
  )
  const cartCount = cart.reduce((sum, i) => sum + i.grams, 0)

  return (
    <AppContext.Provider
      value={{
        user, setUser, balance, setBalance, loadBalance,
        cart, addToCart, removeFromCart, updateCartGrams, clearCart,
        cartTotal, cartCount, getProductPriceForGrams,
        loading, error,
        toast, showToast,
        isAdmin,
        tgUser,
        lang,
        registrationStatus,
        loadUser,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
