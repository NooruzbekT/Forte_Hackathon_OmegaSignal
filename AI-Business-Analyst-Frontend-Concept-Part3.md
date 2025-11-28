# AI-Business Analyst Frontend - Часть 3: Практические примеры и референсы

## 📚 СОДЕРЖАНИЕ

1. [Полные примеры use-cases](#use-cases)
2. [Референсы и вдохновение](#референсы)
3. [FAQ и частые вопросы](#faq)
4. [Чек-лист для хакатона](#чек-лист)
5. [Полезные ресурсы](#ресурсы)

---

## 💼 1. ПОЛНЫЕ ПРИМЕРЫ USE-CASES <a name="use-cases"></a>

### Use Case 1: Пользователь начинает новый проект

**Сценарий**: Пользователь заходит в приложение и хочет создать BRD для новой фичи

**Flow**:
```
1. Пользователь видит WelcomeScreen
2. Выбирает пример или вводит свой запрос: "Нужно добавить QR-оплату в мобильное приложение"
3. Layer 1 (Intent): AI определяет intent=NEW_FEATURE
4. Layer 2 (Gathering): AI задает уточняющие вопросы
5. Layer 3 (RAG): AI ищет похожие проекты
6. Layer 4 (Generation): AI создает BRD документ
7. Layer 5 (Validation): AI проверяет качество
8. Пользователь скачивает DOCX/PDF
```

**Код для тестирования**:

```javascript
// Mock данные для теста
const mockConversation = [
  {
    role: 'user',
    content: 'Нужно добавить QR-оплату в мобильное приложение'
  },
  {
    role: 'assistant',
    content: 'Понял, это новая функциональность. Давайте уточним детали.\n\n1. Для какой платформы: iOS, Android или обе?\n2. Какую проблему решаем?\n3. Какие KPI?',
    layer: 2
  },
  {
    role: 'user',
    content: 'Обе платформы. Хотим ускорить процесс оплаты без ввода карты. KPI: увеличить конверсию на 20%'
  },
  {
    role: 'assistant',
    content: 'Отлично! Создаю BRD документ...',
    layer: 4,
    document: {
      type: 'BRD',
      title: 'QR Payment Integration',
      executiveSummary: 'Добавление функциональности оплаты по QR-коду...',
      requirements: [
        'Сканирование QR-кода через камеру',
        'Интеграция с платежным шлюзом',
        'Поддержка iOS и Android',
        'Отображение истории транзакций'
      ],
      quality: {
        completeness: 0.95,
        consistency: 0.92,
        overall: 0.93
      }
    }
  }
]
```

---

### Use Case 2: Генерация с Mermaid диаграммой

**Сценарий**: AI создает процессную диаграмму

```javascript
const mockMessageWithDiagram = {
  role: 'assistant',
  content: `Вот схема процесса оплаты:

\`\`\`mermaid
graph TD
    A[Пользователь открывает QR Scanner] --> B{QR код валиден?}
    B -->|Да| C[Подтверждение оплаты]
    B -->|Нет| D[Ошибка: Невалидный QR]
    C --> E[Обработка платежа]
    E --> F{Успешно?}
    F -->|Да| G[Показать успех]
    F -->|Нет| H[Показать ошибку]
    G --> I[Добавить в историю]
\`\`\`

Эта схема показывает основной flow оплаты.`,
  layer: 4
}
```

**Компонент для отображения**:

```vue
<script setup>
import { computed } from 'vue'
import VueMermaidString from 'vue-mermaid-string'

const props = defineProps({
  content: String
})

const hasMermaid = computed(() => {
  return props.content.includes('```mermaid')
})

const textParts = computed(() => {
  if (!hasMermaid.value) return [{ type: 'text', content: props.content }]
  
  const parts = []
  const regex = /```mermaid\n([\s\S]*?)\n```/g
  let lastIndex = 0
  let match
  
  while ((match = regex.exec(props.content)) !== null) {
    // Text before diagram
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: props.content.slice(lastIndex, match.index)
      })
    }
    
    // Diagram
    parts.push({
      type: 'mermaid',
      content: match[1]
    })
    
    lastIndex = match.index + match[0].length
  }
  
  // Text after last diagram
  if (lastIndex < props.content.length) {
    parts.push({
      type: 'text',
      content: props.content.slice(lastIndex)
    })
  }
  
  return parts
})
</script>

<template>
  <div class="message-content-parts">
    <div
      v-for="(part, index) in textParts"
      :key="index"
      :class="['content-part', `content-part-${part.type}`]"
    >
      <div v-if="part.type === 'text'" v-html="part.content" />
      
      <div v-else-if="part.type === 'mermaid'" class="mermaid-wrapper">
        <VueMermaidString 
          :value="part.content"
          :options="{ theme: 'default', fontSize: 14 }"
        />
        
        <el-button
          type="primary"
          size="small"
          :icon="Download"
          @click="exportDiagram(part.content)"
          class="export-btn"
        >
          Экспорт PNG
        </el-button>
      </div>
    </div>
  </div>
</template>
```

---

### Use Case 3: Экспорт документа

**Полный рабочий пример**:

```vue
<script setup>
import { ref } from 'vue'
import { useDocument } from '@/composables/useDocument'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  document: Object
})

const { exportDocument } = useDocument()
const isExporting = ref(false)

async function handleExport(format) {
  try {
    await ElMessageBox.confirm(
      `Вы действительно хотите экспортировать документ в формате ${format.toUpperCase()}?`,
      'Экспорт документа',
      {
        confirmButtonText: 'Экспортировать',
        cancelButtonText: 'Отмена',
        type: 'info'
      }
    )
    
    isExporting.value = true
    
    const filename = await exportDocument(props.document, format)
    
    ElMessage.success({
      message: `Документ ${filename} успешно создан!`,
      duration: 5000
    })
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Ошибка экспорта документа')
      console.error(error)
    }
  } finally {
    isExporting.value = false
  }
}
</script>

<template>
  <div class="document-export">
    <el-button-group>
      <el-button
        type="primary"
        :icon="Document"
        :loading="isExporting"
        @click="handleExport('docx')"
      >
        Экспорт DOCX
      </el-button>
      
      <el-button
        type="primary"
        :icon="Document"
        :loading="isExporting"
        @click="handleExport('pdf')"
      >
        Экспорт PDF
      </el-button>
    </el-button-group>
  </div>
</template>
```

---

### Use Case 4: Обработка ошибок API

```vue
<script setup>
import { ref } from 'vue'
import { useChat } from '@/composables/useChat'
import { ElMessage } from 'element-plus'

const { sendMessage } = useChat()
const retryCount = ref(0)
const MAX_RETRIES = 3

async function sendWithRetry(message) {
  try {
    await sendMessage(message)
    retryCount.value = 0 // Reset on success
    
  } catch (error) {
    if (retryCount.value < MAX_RETRIES) {
      retryCount.value++
      
      ElMessage.warning({
        message: `Ошибка отправки. Попытка ${retryCount.value}/${MAX_RETRIES}...`,
        duration: 2000
      })
      
      // Exponential backoff
      const delay = Math.min(1000 * Math.pow(2, retryCount.value), 10000)
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return sendWithRetry(message)
      
    } else {
      ElMessage.error({
        message: 'Не удалось отправить сообщение после нескольких попыток',
        duration: 5000
      })
      
      retryCount.value = 0
      throw error
    }
  }
}
</script>
```

---

### Use Case 5: Сохранение состояния в localStorage

```javascript
// src/composables/usePersistence.js
import { watch } from 'vue'
import { useChatStore } from '@/stores/chatStore'

export function usePersistence() {
  const chatStore = useChatStore()

  // Auto-save on changes
  watch(
    () => chatStore.messages,
    (messages) => {
      try {
        localStorage.setItem('forte_chat', JSON.stringify({
          messages,
          timestamp: Date.now()
        }))
      } catch (error) {
        console.warn('Failed to save to localStorage:', error)
      }
    },
    { deep: true }
  )

  // Load on mount
  function loadSavedChat() {
    try {
      const saved = localStorage.getItem('forte_chat')
      if (saved) {
        const data = JSON.parse(saved)
        
        // Check if data is fresh (< 24 hours)
        const hoursSinceLastSave = (Date.now() - data.timestamp) / 1000 / 60 / 60
        if (hoursSinceLastSave < 24) {
          chatStore.messages = data.messages
          return true
        }
      }
    } catch (error) {
      console.warn('Failed to load from localStorage:', error)
    }
    return false
  }

  function clearSavedChat() {
    try {
      localStorage.removeItem('forte_chat')
    } catch (error) {
      console.warn('Failed to clear localStorage:', error)
    }
  }

  return {
    loadSavedChat,
    clearSavedChat
  }
}
```

**Использование в App.vue**:

```vue
<script setup>
import { onMounted } from 'vue'
import { usePersistence } from '@/composables/usePersistence'
import { ElMessageBox } from 'element-plus'

const { loadSavedChat, clearSavedChat } = usePersistence()

onMounted(async () => {
  const hasData = loadSavedChat()
  
  if (hasData) {
    try {
      await ElMessageBox.confirm(
        'Найден сохраненный чат. Продолжить?',
        'Восстановление сеанса',
        {
          confirmButtonText: 'Продолжить',
          cancelButtonText: 'Начать заново'
        }
      )
    } catch {
      clearSavedChat()
    }
  }
})
</script>
```

---

## 🎨 2. РЕФЕРЕНСЫ И ВДОХНОВЕНИЕ <a name="референсы"></a>

### 2.1 AI Chat Interfaces

**ChatGPT (OpenAI)**
- ✅ Минимализм
- ✅ Четкое разделение пользователь/AI
- ✅ Markdown поддержка
- ✅ Копирование кода

**Claude.ai (Anthropic)**
- ✅ Чистый, профессиональный UI
- ✅ Artifacts (preview документов)
- ✅ Анимации и transitions
- ✅ Thinking indicators

**Google Gemini**
- ✅ Material Design
- ✅ Rich formatting
- ✅ Multi-modal (текст + изображения)

**Что взять для Fortebank**:
- Минимализм ChatGPT
- Чистота Claude
- Профессионализм Gemini
- + Банковская стилистика

### 2.2 Document Editors

**Notion**
- ✅ Блочная структура
- ✅ Плавное редактирование
- ✅ Экспорт в разные форматы

**Google Docs**
- ✅ Real-time preview
- ✅ Commenting system
- ✅ Sharing & collaboration

**Что взять**:
- Preview как в Notion
- Качественный экспорт

### 2.3 Banking UIs

**Revolut**
- ✅ Современный дизайн
- ✅ Четкая типографика
- ✅ Яркие акценты

**Kaspi.kz (Казахстан)**
- ✅ Красный брендинг
- ✅ Понятная навигация
- ✅ Mobile-first

**Halyk Bank (Казахстан)**
- ✅ Зеленые акценты (похоже на Forte!)
- ✅ Консервативный, но современный
- ✅ Доверительный вид

**Что взять**:
- Доверительность Halyk
- Современность Revolut
- Локальную адаптацию Kaspi

---

## ❓ 3. FAQ И ЧАСТЫЕ ВОПРОСЫ <a name="faq"></a>

### Q1: Нужен ли мне TypeScript для этого проекта?

**A**: Нет! Вы указали, что опыта с TypeScript нет, и для хакатона это абсолютно нормально. JavaScript + JSDoc комментарии дадут вам 80% преимуществ TypeScript без кривой обучения.

```javascript
/**
 * @param {string} message - User message
 * @param {Object} options - Options
 * @param {number} options.retry - Retry count
 * @returns {Promise<Object>} API response
 */
async function sendMessage(message, options = {}) {
  // ...
}
```

---

### Q2: Как тестировать без бэкенда?

**A**: Используйте mock данные и `setTimeout` для имитации задержек:

```javascript
// src/utils/mockAPI.js
export const mockAPI = {
  async sendMessage(message) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    return {
      response: `Это mock ответ на: "${message}"`,
      current_layer: Math.floor(Math.random() * 5) + 1,
      document: null
    }
  }
}

// В useChat.js
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

async function sendMessage(content) {
  if (USE_MOCK) {
    return await mockAPI.sendMessage(content)
  }
  return await apiClient.post('/api/chat', { message: content })
}
```

---

### Q3: Как сделать адаптивный дизайн быстро?

**A**: Element Plus компоненты уже адаптивные! Добавьте только медиа-запросы для custom стилей:

```css
/* Mobile-first approach */
.chat-container {
  padding: 12px;
}

@media (min-width: 768px) {
  .chat-container {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .chat-container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

---

### Q4: Mermaid диаграммы не отображаются. Что делать?

**A**: Проверьте:

1. Правильность синтаксиса:
```javascript
// ❌ Bad
const diagram = "graph TD A-->B"

// ✅ Good
const diagram = `graph TD
  A --> B`
```

2. Импорт компонента:
```javascript
import VueMermaidString from 'vue-mermaid-string'
```

3. Опции рендеринга:
```vue
<VueMermaidString 
  :value="diagram"
  :options="{ theme: 'default' }"
/>
```

---

### Q5: Как быстро добавить анимации?

**A**: Используйте CSS transitions и Vue transitions:

```vue
<TransitionGroup name="list">
  <div v-for="item in items" :key="item.id">
    {{ item }}
  </div>
</TransitionGroup>

<style>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
```

---

### Q6: Что делать если docx файлы не открываются?

**A**: Убедитесь что:

1. Используете правильную версию docx:
```json
"docx": "^8.5.0"  // Минимум 8.x
```

2. Создаете Blob правильно:
```javascript
const blob = await Packer.toBlob(doc)
// НЕ Buffer! НЕ ArrayBuffer!
saveAs(blob, 'document.docx')
```

3. MIME type правильный (file-saver делает это автоматически)

---

### Q7: Как оптимизировать для медленного интернета?

**A**:

```javascript
// 1. Lazy loading для тяжелых компонентов
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)

// 2. Debounce для input
import { useDebounceFn } from '@vueuse/core'
const debouncedSearch = useDebounceFn(search, 500)

// 3. Оптимистичный UI
function addMessage(message) {
  // Сразу показываем сообщение
  chatStore.addMessage({ ...message, pending: true })
  
  // Отправляем на сервер
  sendToBackend(message).then(() => {
    updateMessage(message.id, { pending: false })
  })
}
```

---

### Q8: Нужен ли роутер (Vue Router)?

**A**: Для хакатона - **НЕТ!** Одна страница проще и быстрее. Если очень нужно несколько экранов, используйте условный рендеринг:

```vue
<script setup>
import { ref } from 'vue'

const currentView = ref('chat') // 'chat' | 'documents' | 'history'
</script>

<template>
  <ChatView v-if="currentView === 'chat'" />
  <DocumentsView v-else-if="currentView === 'documents'" />
  <HistoryView v-else-if="currentView === 'history'" />
</template>
```

---

## ✅ 4. ЧЕК-ЛИСТ ДЛЯ ХАКАТОНА <a name="чек-лист"></a>

### Pre-Development (до начала кодинга)

- [ ] Прочитать весь концепт-документ
- [ ] Изучить брендбук Fortebank
- [ ] Установить все зависимости
- [ ] Настроить IDE (VSCode + Volar)
- [ ] Создать репозиторий на GitHub
- [ ] Подготовить mock данные

### Day 1: Foundation

**Утро**
- [ ] Создать Vite проект
- [ ] Установить Element Plus + Pinia
- [ ] Создать структуру папок
- [ ] Настроить variables.css с цветами Forte
- [ ] Создать chatStore.js

**После обеда**
- [ ] ChatContainer.vue (базовая версия)
- [ ] ChatMessage.vue
- [ ] ChatInput.vue
- [ ] Протестировать с mock данными

**Вечер (опционально)**
- [ ] Empty state
- [ ] Basic styling
- [ ] Commit & push

### Day 2: Core Features

**Утро**
- [ ] API client setup
- [ ] useChat composable
- [ ] Интеграция с бэкендом (или mock)
- [ ] LayerProgress.vue

**После обеда**
- [ ] MermaidChart.vue
- [ ] useDocument composable
- [ ] DOCX generation
- [ ] PDF generation

**Вечер**
- [ ] DocumentPreview.vue
- [ ] Тестирование генерации
- [ ] Commit & push

### Day 3: Polish

**Утро**
- [ ] Loading states
- [ ] Error handling
- [ ] Mobile responsive
- [ ] Transitions & animations

**После обеда**
- [ ] Финальное тестирование
- [ ] README.md
- [ ] Подготовка презентации
- [ ] Deploy (Vercel/Netlify)

### Pre-Presentation

- [ ] Записать демо видео (backup!)
- [ ] Подготовить live demo
- [ ] Проверить на разных браузерах
- [ ] Приготовить объяснение архитектуры

---

## 🔥 КРИТИЧЕСКИЕ МОМЕНТЫ (не забыть!)

### ⚠️ Top 5 ошибок на хакатонах:

1. **Переусложнение**
   - ❌ Пытаться сделать все фичи
   - ✅ Сфокусироваться на core flow

2. **Игнорирование мобильной версии**
   - ❌ "Сделаем потом"
   - ✅ Mobile-first CSS

3. **Плохая обработка ошибок**
   - ❌ Приложение крашится
   - ✅ Try-catch + user-friendly messages

4. **Отсутствие демо данных**
   - ❌ Ничего не работает без бэкенда
   - ✅ Mock API всегда готов

5. **Плохая презентация**
   - ❌ Показываем код
   - ✅ Показываем value для пользователя

---

## 🚨 EMERGENCY FIXES (если что-то сломалось)

### "npm install не работает"
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### "Element Plus не работает"
```javascript
// main.js
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import ru from 'element-plus/es/locale/lang/ru'

app.use(ElementPlus, { locale: ru })
```

### "Build fails"
```bash
# Проверьте версии
node --version  # Должно быть 18+
npm --version   # Должно быть 9+

# Попробуйте
npm run build -- --debug
```

### "Приложение тормозит"
```javascript
// Быстрый фикс: отключите devtools
app.config.performance = false

// Или используйте production build
npm run build
npm run preview
```

---

## 📚 5. ПОЛЕЗНЫЕ РЕСУРСЫ <a name="ресурсы"></a>

### Официальная документация

- **Vue 3**: https://vuejs.org/guide/introduction.html
- **Vite**: https://vitejs.dev/guide/
- **Pinia**: https://pinia.vuejs.org/introduction.html
- **Element Plus**: https://element-plus.org/en-US/
- **Mermaid**: https://mermaid.js.org/intro/

### Библиотеки документов

- **docx**: https://docx.js.org/
- **jsPDF**: http://raw.githack.com/MrRio/jsPDF/master/docs/
- **vue-mermaid-string**: https://www.npmjs.com/package/vue-mermaid-string

### Инструменты

- **VSCode**: https://code.visualstudio.com/
- **Volar**: https://marketplace.visualstudio.com/items?itemName=Vue.volar
- **Vue DevTools**: https://devtools.vuejs.org/

### CSS & Design

- **Fortebank**: https://forte.kz/
- **Coolors** (палитры): https://coolors.co/
- **CSS Gradient**: https://cssgradient.io/

### Testing & Mock

- **JSONPlaceholder**: https://jsonplaceholder.typicode.com/ (fake API)
- **Mockaroo**: https://www.mockaroo.com/ (generate mock data)

### Deploy

- **Vercel**: https://vercel.com/ (Easiest!)
- **Netlify**: https://www.netlify.com/
- **GitHub Pages**: https://pages.github.com/

---

## 🎯 ФИНАЛЬНЫЕ СОВЕТЫ

### Для успешного хакатона:

1. **Начните простым MVP**
   - Сначала работающий чат
   - Потом добавляйте фичи

2. **Коммитьте часто**
   ```bash
   git commit -m "feat: add basic chat"
   git push
   ```

3. **Тестируйте на реальных данных**
   - Не только "Hello World"
   - Реальные сценарии из банка

4. **Готовьте презентацию с первого дня**
   - Что решает проблему?
   - Как это работает?
   - Почему это круто?

5. **Спите!**
   - Уставший код = плохой код
   - Лучше меньше фич, но качественно

---

## 🏆 SUCCESS CRITERIA

Ваш проект успешен, если:

✅ **Работает core flow**:
- Можно отправить сообщение
- AI отвечает
- Генерируется документ
- Можно скачать DOCX/PDF

✅ **Выглядит профессионально**:
- Чистый UI
- Брендинг Fortebank
- Нет ошибок в консоли

✅ **Демонстрируемо**:
- Работает live demo
- Или записано видео
- Четкая презентация

✅ **Технически грамотно**:
- Понятная архитектура
- Читаемый код
- README с инструкциями

---

## 🎊 ЗАКЛЮЧЕНИЕ

У вас есть ВСЕ для успеха:

📋 **Полная концепция** - архитектура, компоненты, стратегия  
💻 **Готовые примеры** - копируй и адаптируй  
🗺️ **Четкий план** - 3 дня с приоритетами  
🔧 **Решения проблем** - FAQ и emergency fixes  
✅ **Чек-лист** - ничего не забудешь

**Следующие шаги**:
1. ☕ Сделай кофе
2. 📂 Создай проект
3. 💪 Начни с Day 1
4. 🚀 Ship it!

**Удачи на хакатоне Fortebank! Вы сделаете это! 🎉**

---

_Создано для команды AI-Business Analyst • Хакатон Fortebank 2024 • Vue 3 + Element Plus + Pinia_