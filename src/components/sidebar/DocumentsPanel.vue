<script setup>
import { onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documentStore'

const documentStore = useDocumentStore()

onMounted(() => {
  // При первом монтировании грузим список всех документов с бэка
  if (!documentStore.documents.length) {
    documentStore.fetchAllDocuments()
  }
})

const formatDateTime = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime())) return isoString
  return d.toLocaleString()
}
</script>

<template>
  <div class="documents-panel">
    <div class="documents-panel__header">
      <h3>📄 Все документы</h3>

      <button
        class="documents-panel__refresh"
        type="button"
        @click="documentStore.fetchAllDocuments()"
        :disabled="documentStore.isLoading"
      >
        🔄 Обновить
      </button>
    </div>

    <div v-if="documentStore.isLoading" class="documents-panel__state">
      Загружаем документы...
    </div>

    <div v-else-if="documentStore.error" class="documents-panel__state documents-panel__state--error">
      Ошибка загрузки документов
    </div>

    <div
      v-else-if="!documentStore.sortedDocuments.length"
      class="documents-panel__state"
    >
      Документов пока нет
    </div>

    <ul v-else class="documents-panel__list">
      <li
        v-for="doc in documentStore.sortedDocuments"
        :key="doc.filename"
        class="documents-panel__item"
      >
        <div class="documents-panel__item-main">
          <div class="documents-panel__title">
            {{ doc.filename }}
          </div>

          <div class="documents-panel__meta">
            <span v-if="doc.doc_type" class="documents-panel__tag">
              {{ doc.doc_type }}
            </span>
            <span v-if="doc.session_id" class="documents-panel__tag documents-panel__tag--secondary">
              Сессия: {{ doc.session_id }}
            </span>
          </div>
        </div>

        <div class="documents-panel__item-footer">
          <span class="documents-panel__date">
            {{ formatDateTime(doc.created) }}
          </span>
          <span v-if="doc.size" class="documents-panel__size">
            {{ (doc.size / 1024).toFixed(1) }} KB
          </span>

          <a
            v-if="doc.url"
            class="documents-panel__link"
            :href="doc.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            Открыть
          </a>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.documents-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.875rem;
}

.documents-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.documents-panel__header h3 {
  font-size: 0.95rem;
  font-weight: 600;
}

.documents-panel__refresh {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 0.8rem;
  opacity: 0.8;
}

.documents-panel__refresh:disabled {
  opacity: 0.4;
  cursor: default;
}

.documents-panel__state {
  font-size: 0.85rem;
  opacity: 0.8;
}

.documents-panel__state--error {
  color: #ff6b6b;
}

.documents-panel__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.documents-panel__item {
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.documents-panel__item-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.documents-panel__title {
  font-weight: 500;
  word-break: break-all;
}

.documents-panel__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.documents-panel__tag {
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  background: rgba(99, 179, 237, 0.15);
}

.documents-panel__tag--secondary {
  background: rgba(148, 163, 184, 0.2);
}

.documents-panel__item-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
  margin-top: 0.15rem;
}

.documents-panel__date,
.documents-panel__size {
  font-size: 0.75rem;
  opacity: 0.75;
}

.documents-panel__link {
  font-size: 0.8rem;
  text-decoration: none;
  border-radius: 999px;
  padding: 0.2rem 0.6rem;
  border: 1px solid rgba(99, 179, 237, 0.5);
}
</style>
