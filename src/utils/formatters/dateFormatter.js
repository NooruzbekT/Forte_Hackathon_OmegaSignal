export function formatDate(date, format = 'full') {
  const d = new Date(date)
  
  const formats = {
    full: {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    },
    short: {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    },
    time: {
      hour: '2-digit',
      minute: '2-digit'
    }
  }

  return d.toLocaleString('ru-RU', formats[format] || formats.full)
}

export function formatRelativeTime(date) {
  const now = new Date()
  const d = new Date(date)
  const diff = now - d

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  if (diff < minute) {
    return 'только что'
  } else if (diff < hour) {
    const minutes = Math.floor(diff / minute)
    return `${minutes} мин. назад`
  } else if (diff < day) {
    const hours = Math.floor(diff / hour)
    return `${hours} ч. назад`
  } else {
    const days = Math.floor(diff / day)
    return `${days} дн. назад`
  }
}