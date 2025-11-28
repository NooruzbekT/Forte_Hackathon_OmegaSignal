<script setup>
import { ref, computed } from 'vue'
import FormField from './FormField.vue'
import FormProgress from './FormProgress.vue'

const props = defineProps({
  questions: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['submit'])

const currentStep = ref(1)
const answers = ref({})

const currentQuestion = computed(() => {
  return props.questions[currentStep.value - 1]
})

const isLastStep = computed(() => {
  return currentStep.value === props.questions.length
})

const canProceed = computed(() => {
  const answer = answers.value[currentQuestion.value?.id]
  return answer && answer.toString().trim().length > 0
})

function handleNext() {
  if (canProceed.value && !isLastStep.value) {
    currentStep.value++
  }
}

function handlePrevious() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

function handleSubmit() {
  if (canProceed.value) {
    emit('submit', answers.value)
  }
}
</script>

<template>
  <div class="question-form">
    <FormProgress
      :current="currentStep"
      :total="questions.length"
      :steps="questions.map(q => q.label)"
    />
    
    <div class="question-content">
      <FormField
        v-if="currentQuestion"
        :key="currentQuestion.id"
        v-model="answers[currentQuestion.id]"
        :label="currentQuestion.label"
        :type="currentQuestion.type || 'text'"
        :placeholder="currentQuestion.placeholder"
        :required="currentQuestion.required"
        :help-text="currentQuestion.helpText"
      >
        <template v-if="currentQuestion.options" #options>
          <el-option
            v-for="option in currentQuestion.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </template>
      </FormField>
    </div>
    
    <div class="question-actions">
      <el-button
        v-if="currentStep > 1"
        @click="handlePrevious"
      >
        Назад
      </el-button>
      
      <el-button
        v-if="!isLastStep"
        type="primary"
        :disabled="!canProceed"
        @click="handleNext"
      >
        Далее
      </el-button>
      
      <el-button
        v-else
        type="primary"
        :disabled="!canProceed"
        @click="handleSubmit"
      >
        Отправить
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.question-form {
  max-width: 600px;
  margin: 0 auto;
}

.question-content {
  min-height: 200px;
  padding: var(--forte-space-6) 0;
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--forte-space-3);
  padding-top: var(--forte-space-6);
  border-top: 1px solid var(--forte-border-light);
}
</style>