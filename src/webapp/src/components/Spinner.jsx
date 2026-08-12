export default function Spinner({ text = 'Yuklanmoqda...' }) {
  return (
    <div className="loading-center">
      <div className="spinner" />
      <span>{text}</span>
    </div>
  )
}
