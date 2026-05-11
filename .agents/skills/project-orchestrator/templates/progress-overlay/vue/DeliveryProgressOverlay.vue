<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type ProjectStatus = 'active' | 'waiting' | 'blocked' | 'paused' | 'done' | 'warning' | string

type ProgressBlocker = {
  title?: string
  severity?: 'low' | 'medium' | 'high' | 'critical' | string
}

type ProgressData = {
  schemaVersion?: string
  updatedAt?: string
  project?: {
    name?: string
    progress?: number
    stage?: string
    status?: ProjectStatus
  }
  milestone?: {
    id?: string
    name?: string
    progress?: number
    currentTask?: string
    nextAction?: string
  }
  layers?: {
    visual?: number
    interaction?: number
    functional?: number
    hardening?: number
  }
  blockers?: ProgressBlocker[]
  recent?: string[]
}

const props = withDefaults(
  defineProps<{
    src?: string
    pollInterval?: number
    initialOpen?: boolean
    position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  }>(),
  {
    src: '/orchestrator/project-progress.json',
    pollInterval: 2000,
    initialOpen: false,
    position: 'bottom-right',
  },
)

const fallbackProgress: Required<ProgressData> = {
  schemaVersion: '1.0',
  updatedAt: '',
  project: {
    name: 'Project',
    progress: 0,
    stage: 'intake',
    status: 'active',
  },
  milestone: {
    id: 'M1',
    name: 'Milestone',
    progress: 0,
    currentTask: 'Waiting for progress update',
    nextAction: 'Update project-progress.json',
  },
  layers: {
    visual: 0,
    interaction: 0,
    functional: 0,
    hardening: 0,
  },
  blockers: [],
  recent: [],
}

const isOpen = ref(props.initialOpen)
const progress = ref<ProgressData>(fallbackProgress)
const isStale = ref(false)
const lastError = ref('')
let timer: ReturnType<typeof setInterval> | undefined

const clampProgress = (value: unknown): number => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return 0
  return Math.min(100, Math.max(0, Math.round(numeric)))
}

const mergedProgress = computed(() => {
  const current = progress.value || {}
  return {
    ...fallbackProgress,
    ...current,
    project: {
      ...fallbackProgress.project,
      ...(current.project || {}),
      progress: clampProgress(current.project?.progress),
    },
    milestone: {
      ...fallbackProgress.milestone,
      ...(current.milestone || {}),
      progress: clampProgress(current.milestone?.progress),
    },
    layers: {
      visual: clampProgress(current.layers?.visual),
      interaction: clampProgress(current.layers?.interaction),
      functional: clampProgress(current.layers?.functional),
      hardening: clampProgress(current.layers?.hardening),
    },
    blockers: Array.isArray(current.blockers) ? current.blockers : [],
    recent: Array.isArray(current.recent) ? current.recent : [],
  }
})

const statusClass = computed(() => {
  const status = mergedProgress.value.project.status
  if (mergedProgress.value.blockers.some((item) => ['high', 'critical'].includes(String(item.severity)))) {
    return 'is-blocked'
  }
  return `is-${status || 'active'}`
})

const positionClass = computed(() => `position-${props.position}`)

const updatedLabel = computed(() => {
  const value = mergedProgress.value.updatedAt
  if (!value) return 'not updated yet'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
})

const fetchProgress = async () => {
  try {
    const separator = props.src.includes('?') ? '&' : '?'
    const response = await fetch(`${props.src}${separator}t=${Date.now()}`, {
      cache: 'no-store',
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const data = (await response.json()) as ProgressData
    progress.value = data
    isStale.value = false
    lastError.value = ''
  } catch (error) {
    isStale.value = true
    lastError.value = error instanceof Error ? error.message : String(error)
  }
}

onMounted(() => {
  fetchProgress()
  timer = setInterval(fetchProgress, Math.max(1000, props.pollInterval))
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <aside class="delivery-progress-overlay" :class="[positionClass, statusClass, { 'is-open': isOpen }]">
    <button class="delivery-progress-button" type="button" @click="isOpen = !isOpen">
      <span class="milestone-id">{{ mergedProgress.milestone.id }}</span>
      <strong>{{ mergedProgress.milestone.progress }}%</strong>
      <span v-if="isStale" class="stale-dot" title="Progress data is stale" />
    </button>

    <section v-if="isOpen" class="delivery-progress-panel">
      <header class="panel-header">
        <div>
          <p class="eyebrow">Delivery Progress</p>
          <h2>{{ mergedProgress.project.name }}</h2>
        </div>
        <button class="close-button" type="button" aria-label="Close progress panel" @click="isOpen = false">
          ×
        </button>
      </header>

      <div class="progress-row">
        <div>
          <span>Project</span>
          <strong>{{ mergedProgress.project.progress }}%</strong>
        </div>
        <div class="bar"><i :style="{ width: `${mergedProgress.project.progress}%` }" /></div>
      </div>

      <div class="progress-row milestone-row">
        <div>
          <span>{{ mergedProgress.milestone.id }} · {{ mergedProgress.milestone.name }}</span>
          <strong>{{ mergedProgress.milestone.progress }}%</strong>
        </div>
        <div class="bar"><i :style="{ width: `${mergedProgress.milestone.progress}%` }" /></div>
      </div>

      <dl class="meta-list">
        <div>
          <dt>Stage</dt>
          <dd>{{ mergedProgress.project.stage }}</dd>
        </div>
        <div>
          <dt>Current</dt>
          <dd>{{ mergedProgress.milestone.currentTask }}</dd>
        </div>
        <div>
          <dt>Next</dt>
          <dd>{{ mergedProgress.milestone.nextAction }}</dd>
        </div>
      </dl>

      <div class="layers">
        <div v-for="(value, key) in mergedProgress.layers" :key="key" class="layer-item">
          <span>{{ key }}</span>
          <strong>{{ value }}%</strong>
          <div class="mini-bar"><i :style="{ width: `${value}%` }" /></div>
        </div>
      </div>

      <div v-if="mergedProgress.blockers.length" class="section-block blockers">
        <h3>Blockers</h3>
        <ul>
          <li v-for="(blocker, index) in mergedProgress.blockers" :key="`${blocker.title || 'blocker'}-${index}`">
            <span>{{ blocker.severity || 'medium' }}</span>
            {{ blocker.title || 'Untitled blocker' }}
          </li>
        </ul>
      </div>

      <div v-if="mergedProgress.recent.length" class="section-block">
        <h3>Recent</h3>
        <ul>
          <li v-for="(item, index) in mergedProgress.recent.slice(0, 5)" :key="`${item}-${index}`">
            {{ item }}
          </li>
        </ul>
      </div>

      <footer>
        <span>Updated: {{ updatedLabel }}</span>
        <span v-if="isStale">Stale: {{ lastError }}</span>
      </footer>
    </section>
  </aside>
</template>

<style scoped>
.delivery-progress-overlay {
  --accent: #2563eb;
  --accent-soft: rgba(37, 99, 235, 0.14);
  position: fixed;
  z-index: 9999;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #0f172a;
}

.position-bottom-right { right: 18px; bottom: 18px; }
.position-bottom-left { left: 18px; bottom: 18px; }
.position-top-right { right: 18px; top: 18px; }
.position-top-left { left: 18px; top: 18px; }

.is-waiting { --accent: #7c3aed; --accent-soft: rgba(124, 58, 237, 0.14); }
.is-blocked { --accent: #dc2626; --accent-soft: rgba(220, 38, 38, 0.14); }
.is-paused { --accent: #64748b; --accent-soft: rgba(100, 116, 139, 0.14); }
.is-done { --accent: #16a34a; --accent-soft: rgba(22, 163, 74, 0.14); }
.is-warning { --accent: #d97706; --accent-soft: rgba(217, 119, 6, 0.16); }

.delivery-progress-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 96px;
  min-height: 44px;
  padding: 10px 14px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), #0f172a);
  color: #fff;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.22);
  cursor: pointer;
}

.delivery-progress-button strong { font-size: 16px; }
.milestone-id { font-size: 12px; opacity: 0.85; }
.stale-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #fbbf24;
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.25);
}

.delivery-progress-panel {
  width: min(360px, calc(100vw - 32px));
  margin-bottom: 12px;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.24);
  backdrop-filter: blur(18px);
}

.position-top-left .delivery-progress-panel,
.position-top-right .delivery-progress-panel {
  margin-top: 12px;
  margin-bottom: 0;
}

.panel-header,
.progress-row > div:first-child,
.meta-list > div,
.layer-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-header { margin-bottom: 14px; }
.eyebrow {
  margin: 0 0 3px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h2, h3, p { margin: 0; }
h2 { font-size: 17px; }
h3 { margin-bottom: 8px; font-size: 13px; }

.close-button {
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
}

.progress-row { margin: 12px 0; }
.progress-row span,
.meta-list dt,
.layer-item span,
footer {
  color: #64748b;
  font-size: 12px;
}

.bar,
.mini-bar {
  overflow: hidden;
  height: 8px;
  margin-top: 7px;
  border-radius: 999px;
  background: #e2e8f0;
}

.bar i,
.mini-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 220ms ease;
}

.meta-list {
  display: grid;
  gap: 8px;
  margin: 14px 0;
}
.meta-list > div {
  align-items: flex-start;
  padding: 9px 10px;
  border-radius: 12px;
  background: #f8fafc;
}
.meta-list dd {
  max-width: 210px;
  margin: 0;
  text-align: right;
  font-size: 12px;
}

.layers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.layer-item {
  display: block;
  padding: 9px;
  border-radius: 12px;
  background: var(--accent-soft);
}
.layer-item > span,
.layer-item > strong { display: block; }
.layer-item > strong { margin-top: 2px; }
.mini-bar { height: 5px; margin-top: 6px; background: rgba(255, 255, 255, 0.8); }

.section-block {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}
ul {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
li { font-size: 12px; line-height: 1.45; }
.blockers li span {
  margin-right: 6px;
  padding: 2px 6px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
}

footer {
  display: grid;
  gap: 3px;
  margin-top: 12px;
}

@media (max-width: 480px) {
  .position-bottom-right,
  .position-bottom-left {
    right: 12px;
    bottom: 12px;
    left: 12px;
  }
  .delivery-progress-panel { width: auto; }
}
</style>
