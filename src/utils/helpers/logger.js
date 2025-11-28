const isDev = import.meta.env.DEV

export const logger = {
  log(...args) {
    if (isDev) {
      console.log('[LOG]', ...args)
    }
  },

  error(...args) {
    console.error('[ERROR]', ...args)
  },

  warn(...args) {
    if (isDev) {
      console.warn('[WARN]', ...args)
    }
  },

  info(...args) {
    if (isDev) {
      console.info('[INFO]', ...args)
    }
  },

  group(label) {
    if (isDev) {
      console.group(label)
    }
  },

  groupEnd() {
    if (isDev) {
      console.groupEnd()
    }
  }
}