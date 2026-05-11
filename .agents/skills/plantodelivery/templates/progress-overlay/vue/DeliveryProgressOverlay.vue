<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type ProjectStatus = 'active' | 'waiting' | 'blocked' | 'paused' | 'done' | 'warning' | string
type FocusStatus = 'ready' | 'pending' | 'blocked' | string

type ProgressBlocker = {
  title?: string
  severity?: 'low' | 'medium' | 'high' | 'critical' | string
}

type ProgressTask = {
  id?: string
  title?: string
  status?: string
  layer?: string
}

type ProgressDebt = {
  title?: string
  severity?: 'low' | 'medium' | 'high' | 'critical' | string
  revisitStage?: string
}

type ProgressChecks = {
  lastRun?: string
  status?: 'deferred' | 'running' | 'passed' | 'failed' | string
  reason?: string
  updatedAt?: string
}

type ProgressFocus = {
  route?: string
  pageName?: string
  activity?: string
  reason?: string
  status?: FocusStatus
  version?: number
  updatedAt?: string
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
  focus?: ProgressFocus
  checks?: ProgressChecks
  tasks?: ProgressTask[]
  debts?: ProgressDebt[]
  blockers?: ProgressBlocker[]
  recent?: string[]
}

type RouterLike = {
  push: (path: string) => unknown
}

const props = withDefaults(
  defineProps<{
    src?: string
    pollInterval?: number
    initialOpen?: boolean
    position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
    enableFollow?: boolean
    devOnly?: boolean
    router?: RouterLike
  }>(),
  {
    src: '/orchestrator/project-progress.json',
    pollInterval: 2000,
    initialOpen: false,
    position: 'bottom-right',
    enableFollow: true,
    devOnly: true,
  },
)

const env = (import.meta as ImportMeta & { env?: { DEV?: boolean; PROD?: boolean; MODE?: string } }).env
const isDevRuntime = env?.DEV === true || (env?.PROD !== true && env?.MODE !== 'production')

const fallbackProgress = {
  schemaVersion: '1.1',
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
  focus: {
    route: '',
    pageName: '',
    activity: '',
    reason: '',
    status: 'pending',
    version: 0,
    updatedAt: '',
  },
  checks: {
    lastRun: '',
    status: 'deferred',
    reason: 'Full checks deferred until a meaningful checkpoint.',
    updatedAt: '',
  },
  tasks: [] as ProgressTask[],
  debts: [] as ProgressDebt[],
  blockers: [] as ProgressBlocker[],
  recent: [] as string[],
}

const isOpen = ref(props.initialOpen)
const progress = ref<ProgressData>(fallbackProgress)
const isStale = ref(false)
const lastError = ref('')
const followEnabled = ref(false)
const followMessage = ref('')
const lastFollowRoute = ref('')
let timer: ReturnType<typeof setInterval> | undefined

const shouldRender = computed(() => !props.devOnly || isDevRuntime)

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
    focus: {
      ...fallbackProgress.focus,
      ...(current.focus || {}),
      version: Number.isFinite(Number(current.focus?.version)) ? Number(current.focus?.version) : 0,
    },
    checks: {
      ...fallbackProgress.checks,
      ...(current.checks || {}),
    },
    tasks: Array.isArray(current.tasks) ? current.tasks : [],
    debts: Array.isArray(current.debts) ? current.debts : [],
    blockers: Array.isArray(current.blockers) ? current.blockers : [],
    recent: Array.isArray(current.recent) ? current.recent : [],
  }
})

const safeFocusRoute = computed(() => {
  const route = String(mergedProgress.value.focus.route || '').trim()
  if (!route || !route.startsWith('/') || route.startsWith('//')) return ''
  if (/^[a-z][a-z0-9+.-]*:/i.test(route)) return ''
  try {
    const url = new URL(route, window.location.origin)
    if (url.origin !== window.location.origin) return ''
    return `${url.pathname}${url.search}${url.hash}`
  } catch {
    return ''
  }
})

const followAvailable = computed(() => {
  if (!props.enableFollow) return false
  if (!shouldRender.value) return false
  if (mergedProgress.value.project.status === 'paused' || mergedProgress.value.project.status === 'blocked') return false
  if (mergedProgress.value.focus.status !== 'ready') return false
  return Boolean(safeFocusRoute.value)
})

const followUnavailableReason = computed(() => {
  if (!props.enableFollow) return 'Follow disabled by component props.'
  if (mergedProgress.value.project.status === 'paused' || mergedProgress.value.project.status === 'blocked') {
    return 'Follow unavailable while project is paused or blocked.'
  }
  if (mergedProgress.value.focus.status !== 'ready') return `Focus is ${mergedProgress.value.focus.status || 'pending'}.`
  if (!safeFocusRoute.value) return 'No safe focus route.'
  return ''
})

const currentRoute = () => `${window.location.pathname}${window.location.search}${window.location.hash}`

const navigateToFocus = async () => {
  const route = safeFocusRoute.value
  if (!followAvailable.value || !route) return

  try {
    if (currentRoute() !== route) {
      const result = props.router?.push ? props.router.push(route) : undefined
      if (result && typeof (result as Promise<unknown>).then === 'function') {
        await result
      } else if (!props.router?.push) {
        window.history.pushState({}, '', route)
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    }
    lastFollowRoute.value = route
    followEnabled.value = false
    followMessage.value = `Opened ${route}`
  } catch (error) {
    followEnabled.value = false
    followMessage.value = error instanceof Error ? error.message : String(error)
  }
}

const syncManualRouteState = () => {
  if (!followEnabled.value || !lastFollowRoute.value) return
  if (currentRoute() !== lastFollowRoute.value) {
    followEnabled.value = false
    followMessage.value = 'Follow stopped after manual navigation.'
  }
}

watch(
  () => followEnabled.value,
  () => {
    if (followEnabled.value) navigateToFocus()
  },
)

watch(followAvailable, (available) => {
  if (!available) followEnabled.value = false
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
  if (!shouldRender.value) return
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
    syncManualRouteState()
  } catch (error) {
    isStale.value = true
    lastError.value = error instanceof Error ? error.message : String(error)
  }
}

onMounted(() => {
  if (!shouldRender.value) return
  fetchProgress()
  timer = setInterval(fetchProgress, Math.max(1000, props.pollInterval))
  window.addEventListener('popstate', syncManualRouteState)
  window.addEventListener('hashchange', syncManualRouteState)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('popstate', syncManualRouteState)
  window.removeEventListener('hashchange', syncManualRouteState)
})
</script>

<template>
  <aside v-if="shouldRender" class="delivery-progress-overlay" :class="[positionClass, statusClass, { 'is-open': isOpen }]">
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
          x
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

      <section class="focus-card">
        <div>
          <span class="label">Focus</span>
          <strong>{{ mergedProgress.focus.pageName || 'No focus page' }}</strong>
          <code v-if="mergedProgress.focus.route">{{ mergedProgress.focus.route }}</code>
          <p v-if="mergedProgress.focus.activity">{{ mergedProgress.focus.activity }}</p>
          <small v-if="mergedProgress.focus.reason">{{ mergedProgress.focus.reason }}</small>
        </div>
        <label class="follow-toggle" :class="{ 'is-disabled': !followAvailable }">
          <input v-model="followEnabled" type="checkbox" :disabled="!followAvailable">
          <span>Follow</span>
        </label>
      </section>
      <p v-if="followMessage || followUnavailableReason" class="follow-message">
        {{ followMessage || followUnavailableReason }}
      </p>

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
        <div>
          <dt>Checks</dt>
          <dd>
            <strong>{{ mergedProgress.checks.status }}</strong>
            <span v-if="mergedProgress.checks.lastRun"> · {{ mergedProgress.checks.lastRun }}</span>
          </dd>
        </div>
      </dl>
      <p v-if="mergedProgress.checks.reason" class="check-reason">{{ mergedProgress.checks.reason }}</p>

      <div class="layers">
        <div v-for="(value, key) in mergedProgress.layers" :key="key" class="layer-item">
          <span>{{ key }}</span>
          <strong>{{ value }}%</strong>
          <div class="mini-bar"><i :style="{ width: `${value}%` }" /></div>
        </div>
      </div>

      <div v-if="mergedProgress.tasks.length" class="section-block">
        <h3>Tasks</h3>
        <ul>
          <li v-for="(task, index) in mergedProgress.tasks.slice(0, 5)" :key="task.id || `${task.title}-${index}`">
            <span class="pill">{{ task.status || 'planned' }}</span>
            {{ task.title || 'Untitled task' }}
            <small v-if="task.layer">{{ task.layer }}</small>
          </li>
        </ul>
      </div>

      <div v-if="mergedProgress.blockers.length" class="section-block blockers">
        <h3>Blockers</h3>
        <ul>
          <li v-for="(blocker, index) in mergedProgress.blockers" :key="`${blocker.title || 'blocker'}-${index}`">
            <span class="pill">{{ blocker.severity || 'medium' }}</span>
            {{ blocker.title || 'Untitled blocker' }}
          </li>
        </ul>
      </div>

      <div v-if="mergedProgress.debts.length" class="section-block">
        <h3>Debt</h3>
        <ul>
          <li v-for="(debt, index) in mergedProgress.debts.slice(0, 5)" :key="`${debt.title || 'debt'}-${index}`">
            <span class="pill">{{ debt.severity || 'medium' }}</span>
            {{ debt.title || 'Untitled debt' }}
            <small v-if="debt.revisitStage">{{ debt.revisitStage }}</small>
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
  width: min(380px, calc(100vw - 32px));
  margin-bottom: 12px;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.96);
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
.focus-card {
  display: flex;
  align-items: flex-start;
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
  font-size: 18px;
  line-height: 1;
}

.progress-row { margin: 12px 0; }
.progress-row span,
.meta-list dt,
.layer-item span,
footer,
.label,
.focus-card small,
.check-reason,
.follow-message,
li small {
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

.focus-card {
  margin: 14px 0 8px;
  padding: 10px;
  border-radius: 12px;
  background: #f8fafc;
}
.focus-card strong,
.focus-card code,
.focus-card p,
.focus-card small {
  display: block;
  margin-top: 4px;
}
.focus-card code {
  overflow-wrap: anywhere;
  color: var(--accent);
  font-size: 12px;
}
.follow-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}
.follow-toggle.is-disabled {
  color: #94a3b8;
}
.follow-message,
.check-reason {
  margin-top: 6px;
}

.meta-list {
  display: grid;
  gap: 8px;
  margin: 14px 0;
}
.meta-list > div {
  padding: 9px 10px;
  border-radius: 12px;
  background: #f8fafc;
}
.meta-list dd {
  max-width: 220px;
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
.pill {
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
