# 🏦 AI-Business Analyst Frontend - Полная концепция для хакатона Fortebank

## 📋 Содержание
1. [Анализ требований и контекст](#анализ-требований)
2. [Архитектурное решение](#архитектура)
3. [Технологический стек с обоснованием](#стек)
4. [Дизайн-система Fortebank](#дизайн)
5. [Структура проекта](#структура)
6. [Детальные компоненты с кодом](#компоненты)
7. [State Management стратегия](#state)
8. [API интеграция](#api)
9. [UI/UX паттерны для банковского AI](#ux)
10. [План разработки для хакатона](#план)
11. [Оптимизация и производительность](#оптимизация)
12. [Потенциальные проблемы и решения](#проблемы)

---

## 🎯 1. АНАЛИЗ ТРЕБОВАНИЙ И КОНТЕКСТ <a name="анализ-требований"></a>

### 1.1 Контекст проекта
**Хакатон**: AI от Fortebank  
**Цель**: Создать AI-Business Analyst, который автоматизирует создание бизнес-документации  
**Целевая аудитория**: Product managers, Business Analysts, Tech Leads в банке

### 1.2 Функциональные требования

#### Ключевые возможности:
1. **Conversational Interface**
   - Чат с AI-аналитиком
   - Поддержка multi-turn диалогов
   - История взаимодействий
   - Контекстное понимание

2. **5-Layer Processing Visualization**
   - Layer 1: Intent Understanding
   - Layer 2: Requirement Gathering
   - Layer 3: RAG Search
   - Layer 4: Document Generation
   - Layer 5: Quality Validation

3. **Document Generation**
   - BRD (Business Requirements Document)
   - PRD (Product Requirements Document)
   - TSD (Technical Specification Document)
   - Экспорт в DOCX, PDF

4. **Flow Visualization**
   - Mermaid диаграммы
   - Процессные схемы
   - Экспорт в PNG/SVG

### 1.3 Технические ограничения
- **Команда**: 1 фронтендер
- **Время**: 2-3 дня (типичный хакатон)
- **Навыки**: Vue 3 Composition API, без TypeScript
- **Приоритет**: Скорость разработки > идеальная архитектура

### 1.4 Бизнес-требования
- Стилистика Fortebank (брендбук)
- Enterprise-level UI
- Профессиональный, доверительный вид
- Адаптивность (desktop-first, но mobile-friendly)

---

## 🏗️ 2. АРХИТЕКТУРНОЕ РЕШЕНИЕ <a name="архитектура"></a>

### 2.1 Архитектурная философия

**Выбор**: Component-Based Architecture с Composition API

**Обоснование**:
1. **Модульность** - легко разбить на независимые компоненты
2. **Переиспользование** - composables для логики
3. **Тестируемость** - каждый компонент изолирован
4. **Масштабируемость** - легко добавлять новые features

### 2.2 Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────┐
│                      APP LAYER                          │
│                      (App.vue)                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼─────────┐      ┌───────▼──────────┐
│  VIEW LAYER     │      │  STATE LAYER     │
│  (MainView)     │◄─────┤  (Pinia Stores)  │
└───────┬─────────┘      └──────────────────┘
        │                         ▲
        │                         │
        │                    ┌────┴─────┐
        │                    │          │
┌───────▼──────────┐   ┌────▼────┐ ┌──▼───────┐
│ FEATURE MODULES  │   │ Chat    │ │Document  │
│                  │   │ Store   │ │ Store    │
│ ┌──────────────┐ │   └─────────┘ └──────────┘
│ │ Chat Module  │ │         ▲
│ │              │ │         │
│ │ - Container  │ │   ┌─────┴──────┐
│ │ - Messages   │◄────┤ COMPOSABLES│
│ │ - Input      │ │   │            │
│ └──────────────┘ │   │ useChat()  │
│                  │   │ useDoc()   │
│ ┌──────────────┐ │   │ useAPI()   │
│ │ Doc Module   │ │   └────────────┘
│ │              │ │         ▲
│ │ - Preview    │ │         │
│ │ - Generator  │ │   ┌─────┴──────┐
│ │ - Export     │ │   │   UTILS    │
│ └──────────────┘ │   │            │
│                  │   │ API Client │
│ ┌──────────────┐ │   │ Generators │
│ │ Chart Module │ │   │ Formatters │
│ │              │ │   └────────────┘
│ │ - Mermaid    │ │
│ │ - Export     │ │
│ └──────────────┘ │
└──────────────────┘
```

### 2.3 Data Flow Architecture

```
User Input
    ↓
ChatInput Component
    ↓
Chat Store (addMessage)
    ↓
API Layer (useAPI composable)
    ↓
Backend (WebSocket/HTTP)
    ↓
Response Handler
    ↓
Store Update (addMessage, setLayer)
    ↓
UI Update (reactive)
    ↓
Document/Chart Generation (if needed)
```

### 2.4 Архитектурные принципы

1. **Single Responsibility**: Каждый компонент = одна задача
2. **Composition over Inheritance**: Composables вместо mixins
3. **Reactive by Default**: Все данные reactive/ref
4. **Prop Drilling Prevention**: Pinia для глобального state
5. **API Abstraction**: Единый API layer для всех запросов

---

## 💻 3. ТЕХНОЛОГИЧЕСКИЙ СТЕК <a name="стек"></a>

### 3.1 Core Framework

#### Vue 3.4+ (Composition API)
```json
"vue": "^3.4.0"
```

**Почему Vue 3**:
- ✅ Composition API = лучшая организация кода
- ✅ `<script setup>` = меньше boilerplate
- ✅ Быстрый reactivity system
- ✅ Отличная TypeScript поддержка (даже без TS)
- ✅ Команда знакома с Vue

**Почему Composition API**:
- ✅ Логика группируется по функциям, не по опциям
- ✅ Composables легко переиспользовать
- ✅ Лучше для больших компонентов
- ✅ Проще тестировать

### 3.2 Build Tool

#### Vite 5+
```json
"vite": "^5.0.0"
```

**Почему Vite**:
- ⚡ Мгновенный HMR (Hot Module Replacement)
- ⚡ Быстрый cold start
- ⚡ Оптимизированная сборка
- 🎯 Идеален для хакатонов (скорость!)

### 3.3 State Management

#### Pinia 2+
```json
"pinia": "^2.1.0"
```

**Почему Pinia, а не Vuex**:
- ✅ Легче и интуитивнее
- ✅ Отличная TypeScript поддержка
- ✅ Composition API-like синтаксис
- ✅ Нет mutations (проще!)
- ✅ Официально рекомендуется Vue team

**Сравнение альтернатив**:
| Feature | Pinia | Vuex 4 | Reactive() |
|---------|-------|--------|------------|
| Простота | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Масштабируемость | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| DevTools | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Рекомендация | ✅ Best | ⚠️ Legacy | ⚠️ Simple apps |

### 3.4 UI Component Library

#### Element Plus 2+
```json
"element-plus": "^2.5.0"
```

**Почему Element Plus**:
- ✅ 25,000+ GitHub stars
- ✅ Enterprise-grade компоненты
- ✅ Чистый, профессиональный дизайн (идеально для банка!)
- ✅ 80+ компонентов
- ✅ Русская локализация из коробки
- ✅ Отличная документация
- ✅ Vue 3 native

**Альтернативы и почему НЕ их**:

| Library | Плюсы | Минусы | Вердикт |
|---------|-------|--------|---------|
| **Element Plus** | Enterprise UI, много компонентов, рус. язык | Чуть тяжелее | ✅ **ВЫБОР** |
| PrimeVue | Много компонентов, темы | Сложнее кастомизация | ⚠️ Overkill |
| Vuetify | Material Design | Слишком "Google-like", не банковский стиль | ❌ |
| Ant Design Vue | Хорошие компоненты | Китайский стиль, сложнее | ⚠️ |
| Naive UI | Современный, Vue 3 | Меньше компонентов | ⚠️ |
| Quasar | Полный фреймворк | Слишком много для хакатона | ❌ |

### 3.5 Visualization

#### vue-mermaid-string 7+
```json
"vue-mermaid-string": "^7.0.0"
```

**Почему vue-mermaid-string**:
- ✅ Работает со строками (backend отдает готовый код)
- ✅ Всегда последняя версия Mermaid
- ✅ Простой API
- ✅ Vue 3 compatible
- ✅ Легкий (20KB)

**Альтернативы**:
- `vue3-mermaid`: Требует структурированные данные
- `@vue-mermaid/core`: Сложнее setup
- Прямой Mermaid.js: Нужно самому управлять рендерингом

### 3.6 Document Generation

#### docx 8+
```json
"docx": "^8.5.0"
```

**Почему docx**:
- ✅ Генерация DOCX в браузере
- ✅ Полный контроль над форматированием
- ✅ Таблицы, изображения, стили
- ✅ 20K+ stars, активная разработка
- ✅ Работает с Vue из коробки

**Пример возможностей**:
```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 720, right: 720, bottom: 720, left: 720 }
      }
    },
    children: [
      new Paragraph({
        text: "Business Requirements Document",
        heading: HeadingLevel.HEADING_1,
        alignment: AlignmentType.CENTER
      }),
      new Table({...}),
      // И многое другое
    ]
  }]
})
```

#### jsPDF 2.5+
```json
"jspdf": "^2.5.0"
```

**Почему jsPDF**:
- ✅ PDF generation в браузере
- ✅ 28K+ stars
- ✅ Легкий и быстрый
- ✅ UTF-8 поддержка (кириллица!)

#### file-saver 2+
```json
"file-saver": "^2.0.5"
```
- Простое скачивание файлов
- Cross-browser совместимость

### 3.7 HTTP Client

#### Axios 1+ (или встроенный fetch)
```json
"axios": "^1.6.0"  // Опционально
```

**Fetch vs Axios**:
- **Fetch**: Встроенный, легкий, современный
- **Axios**: Interceptors, auto JSON parsing, cancellation

**Рекомендация для хакатона**: Начать с **fetch**, добавить Axios только если нужны interceptors.

### 3.8 Дополнительные утилиты

```json
"@vueuse/core": "^10.7.0",     // Коллекция композиций
"dayjs": "^1.11.10",            // Работа с датами (легче moment)
"lodash-es": "^4.17.21"         // Утилиты (debounce, throttle)
```

### 3.9 Полный package.json

```json
{
  "name": "ai-business-analyst",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "vue-mermaid-string": "^7.0.0",
    "docx": "^8.5.0",
    "jspdf": "^2.5.0",
    "file-saver": "^2.0.5",
    "@vueuse/core": "^10.7.0",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

---

## 🎨 4. ДИЗАЙН-СИСТЕМА FORTEBANK <a name="дизайн"></a>

### 4.1 Брендбук Анализ

**Из официального брендбука Fortebank**:

#### Философия дизайна
> "Логотип с современным и динамичным дизайном выражает позитивное и ориентированное на будущее видение. Форма, поднимающаяся вверх, и цветовой градиент, напоминающий восход солнца, символизируют новое начало, период роста и прогресса."

#### Ключевые принципы
1. **Современность** - Clean, минималистичный
2. **Динамика** - Градиенты, плавные переходы
3. **Прогресс** - Восходящие линии, рост
4. **Доверие** - Зеленый цвет (стабильность, надежность)

### 4.2 Цветовая палитра

#### Primary Colors
```css
:root {
  /* Главный зеленый - используется для CTA, акцентов */
  --forte-primary: #00A651;
  --forte-primary-dark: #008C44;
  --forte-primary-light: #33B870;
  --forte-primary-lighter: #E8F5ED;
  
  /* Градиент для логотипа/special elements */
  --forte-gradient: linear-gradient(135deg, #00A651 0%, #33B870 100%);
  
  /* Оранжевый для акцентов (используется реже) */
  --forte-accent-orange: #FF6B00;
}
```

#### Neutral Colors
```css
:root {
  /* Текст */
  --forte-text-primary: #1A1A1A;
  --forte-text-secondary: #6B6B6B;
  --forte-text-disabled: #BEBEBE;
  
  /* Фоны */
  --forte-bg-primary: #FFFFFF;
  --forte-bg-secondary: #F5F5F5;
  --forte-bg-tertiary: #E5E5E5;
  
  /* Границы */
  --forte-border-light: #E5E5E5;
  --forte-border-medium: #CCCCCC;
  --forte-border-dark: #999999;
}
```

#### Semantic Colors
```css
:root {
  /* Success (используем primary green) */
  --forte-success: #00A651;
  --forte-success-light: #E8F5ED;
  
  /* Warning */
  --forte-warning: #FF9800;
  --forte-warning-light: #FFF3E0;
  
  /* Error */
  --forte-error: #F44336;
  --forte-error-light: #FFEBEE;
  
  /* Info */
  --forte-info: #2196F3;
  --forte-info-light: #E3F2FD;
}
```

### 4.3 Typography

#### Font Stack
```css
:root {
  /* Fortebank скорее всего использует системные шрифты */
  --forte-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                        'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 
                        'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
                        sans-serif;
  
  /* Для кода/технических данных */
  --forte-font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', 
                      'Courier New', monospace;
}
```

#### Font Sizes (Scale)
```css
:root {
  --forte-text-xs: 12px;    /* Мелкий текст, timestamps */
  --forte-text-sm: 14px;    /* Вторичный текст */
  --forte-text-base: 16px;  /* Основной текст */
  --forte-text-lg: 18px;    /* Подзаголовки */
  --forte-text-xl: 20px;    /* Заголовки H3 */
  --forte-text-2xl: 24px;   /* Заголовки H2 */
  --forte-text-3xl: 30px;   /* Заголовки H1 */
  --forte-text-4xl: 36px;   /* Hero text */
}
```

#### Font Weights
```css
:root {
  --forte-font-regular: 400;
  --forte-font-medium: 500;
  --forte-font-semibold: 600;
  --forte-font-bold: 700;
}
```

### 4.4 Spacing System (8px grid)

```css
:root {
  --forte-space-1: 4px;   /* 0.5 unit */
  --forte-space-2: 8px;   /* 1 unit - base */
  --forte-space-3: 12px;  /* 1.5 units */
  --forte-space-4: 16px;  /* 2 units */
  --forte-space-5: 20px;  /* 2.5 units */
  --forte-space-6: 24px;  /* 3 units */
  --forte-space-8: 32px;  /* 4 units */
  --forte-space-10: 40px; /* 5 units */
  --forte-space-12: 48px; /* 6 units */
  --forte-space-16: 64px; /* 8 units */
}
```

### 4.5 Border Radius

```css
:root {
  --forte-radius-sm: 4px;   /* Мелкие элементы (badges, tags) */
  --forte-radius-md: 8px;   /* Кнопки, inputs, cards */
  --forte-radius-lg: 12px;  /* Модальные окна, крупные карточки */
  --forte-radius-xl: 16px;  /* Hero sections */
  --forte-radius-full: 9999px; /* Rounded buttons, avatars */
}
```

### 4.6 Shadows (Depth)

```css
:root {
  /* Тени для создания глубины */
  --forte-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --forte-shadow-md: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  --forte-shadow-lg: 0 4px 12px 0 rgba(0, 0, 0, 0.12);
  --forte-shadow-xl: 0 8px 24px 0 rgba(0, 0, 0, 0.15);
  
  /* Цветная тень для hover effects */
  --forte-shadow-primary: 0 4px 12px 0 rgba(0, 166, 81, 0.3);
}
```

### 4.7 Transitions

```css
:root {
  --forte-transition-fast: 150ms ease-in-out;
  --forte-transition-base: 250ms ease-in-out;
  --forte-transition-slow: 350ms ease-in-out;
  
  --forte-ease-out: cubic-bezier(0.33, 1, 0.68, 1);
  --forte-ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
}
```

### 4.8 Component Styles

#### Buttons
```css
.forte-btn-primary {
  background: var(--forte-primary);
  color: white;
  padding: var(--forte-space-3) var(--forte-space-6);
  border-radius: var(--forte-radius-md);
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-base);
  border: none;
  cursor: pointer;
  transition: all var(--forte-transition-base);
}

.forte-btn-primary:hover {
  background: var(--forte-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--forte-shadow-primary);
}

.forte-btn-secondary {
  background: white;
  color: var(--forte-primary);
  border: 2px solid var(--forte-primary);
  /* ... rest similar */
}
```

#### Cards
```css
.forte-card {
  background: var(--forte-bg-primary);
  border-radius: var(--forte-radius-lg);
  padding: var(--forte-space-6);
  box-shadow: var(--forte-shadow-md);
  transition: box-shadow var(--forte-transition-base);
}

.forte-card:hover {
  box-shadow: var(--forte-shadow-lg);
}
```

#### Inputs
```css
.forte-input {
  width: 100%;
  padding: var(--forte-space-3) var(--forte-space-4);
  border: 2px solid var(--forte-border-light);
  border-radius: var(--forte-radius-md);
  font-size: var(--forte-text-base);
  transition: border-color var(--forte-transition-fast);
}

.forte-input:focus {
  outline: none;
  border-color: var(--forte-primary);
  box-shadow: 0 0 0 3px var(--forte-primary-lighter);
}
```

### 4.9 Layout Patterns

#### Container
```css
.forte-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--forte-space-6);
}

@media (max-width: 768px) {
  .forte-container {
    padding: 0 var(--forte-space-4);
  }
}
```

#### Grid System
```css
.forte-grid {
  display: grid;
  gap: var(--forte-space-6);
  grid-template-columns: repeat(12, 1fr);
}

.forte-grid-2 { grid-template-columns: repeat(2, 1fr); }
.forte-grid-3 { grid-template-columns: repeat(3, 1fr); }
.forte-grid-4 { grid-template-columns: repeat(4, 1fr); }
```

### 4.10 Element Plus Customization

```scss
// Настройка Element Plus под Fortebank стиль
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #00A651,
    ),
    'success': (
      'base': #00A651,
    ),
  ),
  $border-radius: (
    'base': 8px,
  ),
);
```

---

## 📂 5. СТРУКТУРА ПРОЕКТА <a name="структура"></a>

### 5.1 Детальная файловая структура

```
ai-business-analyst/
├── public/
│   ├── favicon.ico
│   └── logo-fortebank.svg
│
├── src/
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── main.css              # Глобальные стили
│   │   │   ├── variables.css         # CSS переменные (Fortebank Design)
│   │   │   ├── element-custom.scss   # Кастомизация Element Plus
│   │   │   └── animations.css        # Анимации
│   │   │
│   │   ├── images/
│   │   │   ├── logo.svg
│   │   │   ├── empty-state.svg
│   │   │   └── error-state.svg
│   │   │
│   │   └── fonts/                    # Если нужны кастомные шрифты
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.vue     # Главный контейнер чата
│   │   │   ├── ChatMessage.vue       # Отдельное сообщение
│   │   │   ├── ChatInput.vue         # Поле ввода с кнопкой
│   │   │   ├── ChatHistory.vue       # Sidebar с историей
│   │   │   ├── TypingIndicator.vue   # "AI печатает..."
│   │   │   ├── MessageActions.vue    # Действия (copy, regenerate)
│   │   │   └── WelcomeScreen.vue     # Приветственный экран
│   │   │
│   │   ├── layers/
│   │   │   ├── LayerProgress.vue     # Визуализация 5 слоев
│   │   │   ├── LayerCard.vue         # Карточка отдельного слоя
│   │   │   └── LayerTimeline.vue     # Timeline для слоев
│   │   │
│   │   ├── documents/
│   │   │   ├── DocumentPreview.vue   # Превью документа (markdown)
│   │   │   ├── DocumentHeader.vue    # Заголовок документа
│   │   │   ├── DocumentActions.vue   # Экспорт/Скачать
│   │   │   ├── DocumentList.vue      # Список сгенерированных
│   │   │   ├── QualityBadge.vue      # Бейдж качества (Layer 5)
│   │   │   └── DocumentMetadata.vue  # Метаданные (время, тип)
│   │   │
│   │   ├── visualization/
│   │   │   ├── MermaidChart.vue      # Mermaid диаграммы
│   │   │   ├── ChartExport.vue       # Экспорт в PNG/SVG
│   │   │   ├── ChartToolbar.vue      # Инструменты (zoom, export)
│   │   │   └── ChartEmpty.vue        # Empty state
│   │   │
│   │   ├── forms/
│   │   │   ├── QuestionForm.vue      # Форма для Layer 2
│   │   │   ├── FormField.vue         # Кастомное поле
│   │   │   └── FormProgress.vue      # Прогресс заполнения
│   │   │
│   │   ├── common/
│   │   │   ├── AppHeader.vue         # Шапка приложения
│   │   │   ├── AppSidebar.vue        # Боковое меню
│   │   │   ├── AppFooter.vue         # Футер
│   │   │   ├── LoadingSpinner.vue    # Кастомный спиннер
│   │   │   ├── ErrorBoundary.vue     # Error handling
│   │   │   ├── EmptyState.vue        # Empty states
│   │   │   ├── ConfirmDialog.vue     # Модальные окна
│   │   │   └── Toast.vue             # Уведомления
│   │   │
│   │   └── ui/                       # Обертки над Element Plus
│   │       ├── ForteButton.vue
│   │       ├── ForteInput.vue
│   │       ├── ForteCard.vue
│   │       └── ForteBadge.vue
│   │
│   ├── composables/
│   │   ├── useChat.js               # Логика чата
│   │   ├── useDocument.js           # Генерация/экспорт документов
│   │   ├── useWebSocket.js          # WebSocket соединение
│   │   ├── useAPI.js                # HTTP запросы
│   │   ├── useLayer.js              # Управление слоями
│   │   ├── useNotification.js       # Уведомления
│   │   ├── useClipboard.js          # Копирование в буфер
│   │   └── useExport.js             # Экспорт файлов
│   │
│   ├── stores/
│   │   ├── index.js                 # Export всех stores
│   │   ├── chatStore.js             # История чата, сообщения
│   │   ├── documentStore.js         # Сгенерированные документы
│   │   ├── layerStore.js            # Состояние слоев
│   │   ├── userStore.js             # Данные пользователя
│   │   └── appStore.js              # Глобальное состояние
│   │
│   ├── utils/
│   │   ├── api/
│   │   │   ├── client.js            # Axios/Fetch instance
│   │   │   ├── endpoints.js         # API endpoints
│   │   │   └── interceptors.js      # Request/Response interceptors
│   │   │
│   │   ├── generators/
│   │   │   ├── docxGenerator.js     # DOCX генерация
│   │   │   ├── pdfGenerator.js      # PDF генерация
│   │   │   ├── markdownParser.js    # Markdown → HTML
│   │   │   └── mermaidExporter.js   # Экспорт диаграмм
│   │   │
│   │   ├── formatters/
│   │   │   ├── dateFormatter.js     # Форматирование дат
│   │   │   ├── textFormatter.js     # Текстовые утилиты
│   │   │   └── numberFormatter.js   # Числа
│   │   │
│   │   ├── validators/
│   │   │   ├── inputValidator.js    # Валидация ввода
│   │   │   └── fileValidator.js     # Валидация файлов
│   │   │
│   │   └── helpers/
│   │       ├── storage.js           # LocalStorage обертка
│   │       ├── constants.js         # Константы
│   │       ├── debounce.js          # Debounce/Throttle
│   │       └── logger.js            # Логирование
│   │
│   ├── router/
│   │   └── index.js                 # Vue Router (если нужно)
│   │
│   ├── views/
│   │   ├── MainView.vue             # Главная страница (чат)
│   │   ├── DocumentsView.vue        # Страница документов (опционально)
│   │   └── HistoryView.vue          # История (опционально)
│   │
│   ├── App.vue                      # Root component
│   └── main.js                      # Entry point
│
├── .env.development                 # Dev environment variables
├── .env.production                  # Prod environment variables
├── .gitignore
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

### 5.2 Naming Conventions

#### Файлы компонентов
- **PascalCase**: `ChatContainer.vue`, `DocumentPreview.vue`
- **Префиксы**: 
  - `App` для layout: `AppHeader.vue`
  - `Forte` для UI wrappers: `ForteButton.vue`

#### Composables
- **camelCase**: `useChat.js`, `useDocument.js`
- **Префикс** `use`: Всегда!

#### Stores
- **camelCase** с суффиксом `Store`: `chatStore.js`

#### Utils
- **camelCase**: `docxGenerator.js`, `dateFormatter.js`

### 5.3 Import Organization

```javascript
// Порядок импортов (рекомендация)
// 1. Vue core
import { ref, computed, onMounted } from 'vue'

// 2. External libraries
import { ElMessage } from 'element-plus'

// 3. Composables
import { useChat } from '@/composables/useChat'

// 4. Stores
import { useChatStore } from '@/stores/chatStore'

// 5. Components
import ChatMessage from './ChatMessage.vue'

// 6. Utils
import { formatDate } from '@/utils/formatters/dateFormatter'

// 7. Types (если есть TypeScript)
import type { Message } from '@/types'
```

---

## 🧩 6. ДЕТАЛЬНЫЕ КОМПОНЕНТЫ С КОДОМ <a name="компоненты"></a>

### 6.1 Core: ChatContainer.vue

Это сердце приложения - главный компонент чата.

```vue
<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import { useLayerStore } from '@/stores/layerStore'
import { ElMessage } from 'element-plus'
import { useChat } from '@/composables/useChat'

import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import LayerProgress from '@/components/layers/LayerProgress.vue'
import TypingIndicator from './TypingIndicator.vue'
import WelcomeScreen from './WelcomeScreen.vue'

// Stores
const chatStore = useChatStore()
const layerStore = useLayerStore()

// Composables
const { sendMessage, isLoading } = useChat()

// Refs
const messagesContainer = ref(null)
const isScrolledToBottom = ref(true)

// Computed
const messages = computed(() => chatStore.messages)
const hasMessages = computed(() => messages.value.length > 0)
const currentLayer = computed(() => layerStore.currentLayer)

// Methods
async function handleSendMessage(content) {
  if (!content.trim()) {
    ElMessage.warning('Пожалуйста, введите сообщение')
    return
  }

  try {
    await sendMessage(content)
    await nextTick()
    if (isScrolledToBottom.value) {
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('Ошибка отправки сообщения')
    console.error(error)
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handleScroll() {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const threshold = 100 // pixels from bottom
  isScrolledToBottom.value = scrollHeight - scrollTop - clientHeight < threshold
}

function handleNewChat() {
  chatStore.clearChat()
  layerStore.reset()
}

// Lifecycle
onMounted(() => {
  scrollToBottom()
})

// Watchers
watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    if (isScrolledToBottom.value) {
      scrollToBottom()
    }
  }
)
</script>

<template>
  <div class="chat-container">
    <!-- Header with Layer Progress -->
    <div class="chat-header">
      <div class="chat-header-content">
        <h1 class="chat-title">
          <el-icon><ChatDotRound /></el-icon>
          AI Business Analyst
        </h1>
        
        <el-button 
          type="primary" 
          :icon="Plus"
          @click="handleNewChat"
          v-if="hasMessages"
        >
          Новый чат
        </el-button>
      </div>
      
      <LayerProgress 
        v-if="hasMessages"
        :current-layer="currentLayer"
        class="layer-progress-bar"
      />
    </div>

    <!-- Messages Area -->
    <div 
      ref="messagesContainer"
      class="messages-area"
      @scroll="handleScroll"
    >
      <!-- Welcome Screen -->
      <WelcomeScreen v-if="!hasMessages" />

      <!-- Messages -->
      <TransitionGroup name="message-list">
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
        />
      </TransitionGroup>

      <!-- Typing Indicator -->
      <TypingIndicator v-if="isLoading" />

      <!-- Scroll to Bottom Button -->
      <Transition name="fade">
        <el-button
          v-show="!isScrolledToBottom && hasMessages"
          class="scroll-to-bottom"
          circle
          :icon="ArrowDown"
          @click="scrollToBottom"
        />
      </Transition>
    </div>

    <!-- Input Area -->
    <ChatInput 
      @send="handleSendMessage"
      :disabled="isLoading"
    />
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--forte-bg-secondary);
}

.chat-header {
  background: white;
  border-bottom: 1px solid var(--forte-border-light);
  padding: var(--forte-space-4) var(--forte-space-6);
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-4);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin: 0;
}

.layer-progress-bar {
  margin-top: var(--forte-space-4);
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--forte-space-6);
  scroll-behavior: smooth;
  position: relative;
}

.messages-area::-webkit-scrollbar {
  width: 6px;
}

/* .messages-area::-webkit-scrollbar-track {
  background: transparent;
} */

.messages-area::-webkit-scrollbar-thumb {
  background: var(--forte-border-medium);
  border-radius: var(--forte-radius-full);
}

.scroll-to-bottom {
  position: fixed;
  bottom: 120px;
  right: var(--forte-space-6);
  box-shadow: var(--forte-shadow-lg);
  z-index: 10;
}

/* Animations */
.message-list-enter-active {
  transition: all 0.3s ease-out;
}

.message-list-leave-active {
  transition: all 0.2s ease-in;
}

.message-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-header {
    padding: var(--forte-space-3) var(--forte-space-4);
  }
  
  .chat-title {
    font-size: var(--forte-text-xl);
  }
  
  .messages-area {
    padding: var(--forte-space-4);
  }
}
</style>
```

### 6.2 ChatMessage.vue

```vue
<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useClipboard } from '@/composables/useClipboard'
import { useChatStore } from '@/stores/chatStore'

import MermaidChart from '@/components/visualization/MermaidChart.vue'
import DocumentPreview from '@/components/documents/DocumentPreview.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
    validator: (msg) => {
      return msg.id && msg.role && msg.content && msg.timestamp
    }
  }
})

const chatStore = useChatStore()
const { copy } = useClipboard()

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')
const hasLayer = computed(() => props.message.layer !== null)

// Content analysis
const hasMermaid = computed(() => {
  return typeof props.message.content === 'string' && 
         props.message.content.includes('```mermaid')
})

const hasDocument = computed(() => {
  return props.message.document !== undefined
})

const mermaidCode = computed(() => {
  if (!hasMermaid.value) return ''
  const match = props.message.content.match(/```mermaid\n([\s\S]*?)\n```/)
  return match ? match[1] : ''
})

const textContent = computed(() => {
  if (hasMermaid.value) {
    return props.message.content.replace(/```mermaid[\s\S]*?```/g, '')
  }
  return props.message.content
})

// Layer names mapping
const layerNames = {
  1: { name: 'Intent Understanding', color: '#9C27B0' },
  2: { name: 'Requirement Gathering', color: '#2196F3' },
  3: { name: 'RAG Search', color: '#FF9800' },
  4: { name: 'Document Generation', color: '#00A651' },
  5: { name: 'Quality Validation', color: '#4CAF50' }
}

const layerInfo = computed(() => {
  return hasLayer.value ? layerNames[props.message.layer] : null
})

// Actions
async function handleCopy() {
  try {
    await copy(textContent.value)
    ElMessage.success('Скопировано в буфер обмена')
  } catch (error) {
    ElMessage.error('Ошибка копирования')
  }
}

function handleRegenerate() {
  // TODO: Implement regenerate logic
  chatStore.regenerateMessage(props.message.id)
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div 
    :class="[
      'chat-message',
      { 'message-user': isUser, 'message-assistant': isAssistant }
    ]"
  >
    <!-- Avatar & Header -->
    <div class="message-header">
      <el-avatar 
        :size="40"
        :style="{ 
          background: isUser ? 'var(--forte-accent-orange)' : 'var(--forte-primary)' 
        }"
      >
        <template v-if="isUser">
          <el-icon><User /></el-icon>
        </template>
        <template v-else>
          <el-icon><Robot /></el-icon>
        </template>
      </el-avatar>

      <div class="message-meta">
        <span class="message-author">
          {{ isUser ? 'Вы' : 'AI-аналитик' }}
        </span>
        
        <el-tag 
          v-if="layerInfo"
          :color="layerInfo.color"
          size="small"
          effect="dark"
          class="layer-tag"
        >
          Layer {{ message.layer }}: {{ layerInfo.name }}
        </el-tag>
      </div>

      <span class="message-time">
        {{ formatTime(message.timestamp) }}
      </span>
    </div>

    <!-- Content -->
    <div class="message-body">
      <!-- Text Content -->
      <div 
        v-if="textContent.trim()"
        class="message-content"
        v-html="textContent"
      />

      <!-- Mermaid Diagram -->
      <MermaidChart 
        v-if="hasMermaid"
        :diagram="mermaidCode"
        class="message-diagram"
      />

      <!-- Document Preview -->
      <DocumentPreview
        v-if="hasDocument"
        :document="message.document"
        class="message-document"
      />
    </div>

    <!-- Actions (only for assistant messages) -->
    <div v-if="isAssistant" class="message-actions">
      <el-button 
        text
        :icon="DocumentCopy"
        @click="handleCopy"
        size="small"
      >
        Копировать
      </el-button>
      
      <el-button 
        text
        :icon="RefreshRight"
        @click="handleRegenerate"
        size="small"
      >
        Пересоздать
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  margin-bottom: var(--forte-space-6);
  animation: slideIn 0.3s ease-out;
}

.message-header {
  display: flex;
  align-items: flex-start;
  gap: var(--forte-space-3);
  margin-bottom: var(--forte-space-4);
}

.message-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
}

.message-author {
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-base);
  color: var(--forte-text-primary);
}

.layer-tag {
  width: fit-content;
}

.message-time {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  white-space: nowrap;
}

.message-body {
  margin-left: calc(40px + var(--forte-space-3));
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-4);
}

.message-content {
  padding: var(--forte-space-4);
  border-radius: var(--forte-radius-md);
  line-height: 1.6;
  color: var(--forte-text-primary);
}

.message-user .message-content {
  background: white;
  border: 1px solid var(--forte-border-light);
}

.message-assistant .message-content {
  background: var(--forte-primary-lighter);
}

.message-diagram,
.message-document {
  max-width: 100%;
}

.message-actions {
  margin-left: calc(40px + var(--forte-space-3));
  margin-top: var(--forte-space-2);
  display: flex;
  gap: var(--forte-space-2);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .message-body {
    margin-left: 0;
    margin-top: var(--forte-space-3);
  }
  
  .message-actions {
    margin-left: 0;
  }
}
</style>
```

### 6.3 ChatInput.vue

```vue
<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['send'])

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Опишите требования к проекту...'
  },
  maxLength: {
    type: Number,
    default: 2000
  }
})

const inputText = ref('')
const isComposing = ref(false)

const charCount = computed(() => inputText.value.length)
const canSend = computed(() => {
  return inputText.value.trim().length > 0 && 
         !props.disabled && 
         charCount.value <= props.maxLength
})

function handleSend() {
  if (!canSend.value) return
  
  const message = inputText.value.trim()
  emit('send', message)
  inputText.value = ''
}

function handleKeydown(event) {
  // Ctrl/Cmd + Enter to send
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    handleSend()
  }
  
  // Prevent send on Enter during composition (for Asian languages)
  if (event.key === 'Enter' && !event.shiftKey && !isComposing.value) {
    event.preventDefault()
    handleSend()
  }
}

function handlePaste(event) {
  const pastedText = event.clipboardData?.getData('text')
  if (pastedText && (charCount.value + pastedText.length) > props.maxLength) {
    ElMessage.warning(`Максимальная длина сообщения: ${props.maxLength} символов`)
  }
}
</script>

<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <!-- Main Textarea -->
      <el-input
        v-model="inputText"
        type="textarea"
        :placeholder="placeholder"
        :disabled="disabled"
        :maxlength="maxLength"
        :autosize="{ minRows: 1, maxRows: 6 }"
        resize="none"
        class="chat-textarea"
        @keydown="handleKeydown"
        @paste="handlePaste"
        @compositionstart="isComposing = true"
        @compositionend="isComposing = false"
      />

      <!-- Actions -->
      <div class="input-actions">
        <!-- Character Counter -->
        <span 
          class="char-counter"
          :class="{ 'char-counter-warning': charCount > maxLength * 0.9 }"
        >
          {{ charCount }} / {{ maxLength }}
        </span>

        <!-- Send Button -->
        <el-button
          type="primary"
          :icon="Position"
          :disabled="!canSend"
          @click="handleSend"
          circle
          class="send-button"
        />
      </div>
    </div>

    <!-- Helper Text -->
    <div class="input-helper">
      <span class="helper-text">
        <el-icon><InfoFilled /></el-icon>
        Нажмите Enter для отправки, Shift+Enter для новой строки
      </span>
    </div>
  </div>
</template>

<style scoped>
.chat-input-container {
  background: white;
  border-top: 1px solid var(--forte-border-light);
  padding: var(--forte-space-4) var(--forte-space-6);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--forte-space-3);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-lg);
  padding: var(--forte-space-3);
  border: 2px solid transparent;
  transition: border-color var(--forte-transition-fast);
}

.input-wrapper:focus-within {
  border-color: var(--forte-primary);
}

.chat-textarea {
  flex: 1;
}

.chat-textarea :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: var(--forte-space-2);
  font-size: var(--forte-text-base);
  line-height: 1.5;
}

.chat-textarea :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--forte-space-2);
}

.char-counter {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  transition: color var(--forte-transition-fast);
}

.char-counter-warning {
  color: var(--forte-warning);
  font-weight: var(--forte-font-semibold);
}

.send-button {
  width: 40px;
  height: 40px;
  transition: all var(--forte-transition-base);
}

.send-button:not(:disabled):hover {
  transform: scale(1.1);
}

.input-helper {
  margin-top: var(--forte-space-3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.helper-text {
  display: flex;
  align-items: center;
  gap: var(--forte-space-2);
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .chat-input-container {
    padding: var(--forte-space-3) var(--forte-space-4);
  }
  
  .helper-text {
    display: none;
  }
}
</style>
```

### 6.4 LayerProgress.vue

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentLayer: {
    type: Number,
    default: null,
    validator: (value) => value === null || (value >= 1 && value <= 5)
  }
})

const layers = [
  {
    id: 1,
    name: 'Intent Understanding',
    icon: 'BrainIcon',
    description: 'Анализ намерения пользователя'
  },
  {
    id: 2,
    name: 'Requirement Gathering',
    icon: 'DocumentCheckIcon',
    description: 'Сбор требований через диалог'
  },
  {
    id: 3,
    name: 'RAG Search',
    icon: 'SearchIcon',
    description: 'Поиск похожих документов'
  },
  {
    id: 4,
    name: 'Document Generation',
    icon: 'DocumentIcon',
    description: 'Генерация документа'
  },
  {
    id: 5,
    name: 'Quality Validation',
    icon: 'CheckCircleIcon',
    description: 'Проверка качества'
  }
]

function getLayerStatus(layerId) {
  if (props.currentLayer === null) return 'pending'
  if (layerId < props.currentLayer) return 'completed'
  if (layerId === props.currentLayer) return 'active'
  return 'pending'
}

const progressPercentage = computed(() => {
  if (props.currentLayer === null) return 0
  return (props.currentLayer / 5) * 100
})
</script>

<template>
  <div class="layer-progress">
    <!-- Progress Bar -->
    <div class="progress-bar-container">
      <div 
        class="progress-bar-fill"
        :style="{ width: `${progressPercentage}%` }"
      />
    </div>

    <!-- Layer Steps -->
    <div class="layer-steps">
      <div
        v-for="layer in layers"
        :key="layer.id"
        :class="[
          'layer-step',
          `layer-step-${getLayerStatus(layer.id)}`
        ]"
      >
        <!-- Circle -->
        <div class="layer-circle">
          <el-icon v-if="getLayerStatus(layer.id) === 'completed'">
            <Check />
          </el-icon>
          <el-icon v-else-if="getLayerStatus(layer.id) === 'active'" class="spin">
            <Loading />
          </el-icon>
          <span v-else>{{ layer.id }}</span>
        </div>

        <!-- Info -->
        <div class="layer-info">
          <span class="layer-name">{{ layer.name }}</span>
          <span class="layer-description">{{ layer.description }}</span>
        </div>

        <!-- Connector Line -->
        <div 
          v-if="layer.id < 5"
          class="layer-connector"
          :class="{ 'connector-active': layer.id < currentLayer }"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layer-progress {
  background: white;
  border-radius: var(--forte-radius-md);
  padding: var(--forte-space-6);
}

.progress-bar-container {
  width: 100%;
  height: 4px;
  background: var(--forte-border-light);
  border-radius: var(--forte-radius-full);
  margin-bottom: var(--forte-space-6);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--forte-gradient);
  transition: width 0.5s ease;
  border-radius: var(--forte-radius-full);
}

.layer-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.layer-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  text-align: center;
}

.layer-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--forte-font-bold);
  font-size: var(--forte-text-base);
  transition: all var(--forte-transition-base);
  position: relative;
  z-index: 2;
  background: white;
  border: 3px solid var(--forte-border-light);
  color: var(--forte-text-secondary);
}

.layer-step-active .layer-circle {
  border-color: var(--forte-primary);
  background: var(--forte-primary);
  color: white;
  box-shadow: 0 0 0 4px var(--forte-primary-lighter);
}

.layer-step-completed .layer-circle {
  border-color: var(--forte-primary);
  background: var(--forte-primary);
  color: white;
}

.layer-info {
  margin-top: var(--forte-space-3);
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-1);
}

.layer-name {
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-sm);
  color: var(--forte-text-primary);
}

.layer-description {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
}

.layer-connector {
  position: absolute;
  top: 24px;
  left: calc(50% + 24px);
  right: calc(-50% + 24px);
  height: 3px;
  background: var(--forte-border-light);
  transition: background-color 0.5s ease;
  z-index: 1;
}

.connector-active {
  background: var(--forte-primary);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .layer-steps {
    flex-wrap: wrap;
    gap: var(--forte-space-6);
  }
  
  .layer-step {
    flex-basis: calc(50% - var(--forte-space-3));
  }
  
  .layer-connector {
    display: none;
  }
}

@media (max-width: 640px) {
  .layer-description {
    display: none;
  }
  
  .layer-circle {
    width: 40px;
    height: 40px;
  }
}
</style>
```

*(Продолжение следует в части 2...)*