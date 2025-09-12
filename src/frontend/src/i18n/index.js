import { createI18n } from 'vue-i18n'
import zh from '../locales/zh.js'
import en from '../locales/en.js'

const messages = {
  zh,
  en
}

// 获取浏览器语言设置，默认为中文
function getDefaultLocale() {
  const savedLocale = localStorage.getItem('movieclip-locale')
  if (savedLocale && ['zh', 'en'].includes(savedLocale)) {
    return savedLocale
  }
  
  const browserLocale = navigator.language.toLowerCase()
  if (browserLocale.startsWith('zh')) {
    return 'zh'
  } else if (browserLocale.startsWith('en')) {
    return 'en'
  }
  
  return 'zh' // 默认中文
}

const i18n = createI18n({
  locale: getDefaultLocale(),
  fallbackLocale: 'zh',
  messages,
  legacy: false, // 使用 Composition API
  globalInjection: true
})

export default i18n
