<script setup lang="ts">
import { useDraggable, useLocalStorage, useWindowSize } from '@vueuse/core'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

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
    src: '/public/orchestrator/project-progress.json',
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
const overlayRef = ref<HTMLElement | null>(null)
const dragHandleRef = ref<HTMLElement | null>(null)
const { width: windowWidth, height: windowHeight } = useWindowSize()
const savedPosition = useLocalStorage<{ x: number; y: number } | null>('delivery-progress-overlay-position', null)
const defaultPosition = computed(() => ({
  x: Math.max(12, windowWidth.value - 64),
  y: Math.max(12, windowHeight.value - 110),
}))
const dragInitial = computed(() => {
  const saved = savedPosition.value
  if (!saved || !Number.isFinite(saved.x) || !Number.isFinite(saved.y)) return defaultPosition.value
  return saved
})
const { x, y, isDragging } = useDraggable(overlayRef, {
  handle: dragHandleRef,
  initialValue: dragInitial,
  preventDefault: true,
  stopPropagation: true,
  onEnd: (position) => {
    savedPosition.value = {
      x: Math.round(position.x),
      y: Math.round(position.y),
    }
  },
})
const overlayStyle = computed(() => ({
  left: `${x.value}px`,
  top: `${y.value}px`,
}))

function clampOverlayIntoView() {
  const width = overlayRef.value?.offsetWidth || 52
  const height = overlayRef.value?.offsetHeight || 36
  const nextX = Math.min(Math.max(12, x.value), Math.max(12, windowWidth.value - width - 12))
  const nextY = Math.min(Math.max(12, y.value), Math.max(12, windowHeight.value - height - 76))
  if (nextX !== x.value) x.value = nextX
  if (nextY !== y.value) y.value = nextY
}
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
    schemaVersion: current.schemaVersion || fallbackProgress.schemaVersion,
    updatedAt: current.updatedAt || fallbackProgress.updatedAt,
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
  if (!route) return ''
  if (route.startsWith('javascript:') || route.startsWith('//') || /^[a-z]+:/i.test(route)) return ''
  if (!route.startsWith('/')) return ''
  return route
})

const currentRoute = () => `${window.location.pathname}${window.location.search}${window.location.hash}`

const routeToUrl = (route: string) => {
  const hashRoute = route.startsWith('/#') ? route.slice(2) : route
  return `${window.location.pathname}${window.location.search}#${hashRoute}`
}

const followAvailable = computed(() => props.enableFollow && Boolean(safeFocusRoute.value))
const followUnavailableReason = computed(() => {
  if (!props.enableFollow) return 'Follow is disabled for this project.'
  if (!safeFocusRoute.value && mergedProgress.value.focus.route) return 'Focus route is blocked for safety.'
  if (!safeFocusRoute.value) return 'No focus route provided.'
  return ''
})

const navigateToFocus = async () => {
  const route = safeFocusRoute.value
  if (!route) return
  followMessage.value = ''
  try {
    if (props.router?.push) {
      await props.router.push(route)
    } else {
      const url = routeToUrl(route)
      if (currentRoute() !== url) {
        window.history.pushState({}, '', url)
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    }
    lastFollowRoute.value = currentRoute()
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

watch([windowWidth, windowHeight, isOpen], () => {
  nextTick(clampOverlayIntoView)
})

watch(
  () => [mergedProgress.value.focus.route, mergedProgress.value.focus.version],
  () => {
    if (followEnabled.value) navigateToFocus()
  },
)

watch(followAvailable, (available) => {
  if (!available) followEnabled.value = false
})

const statusClass = computed(() => {
  const status = mergedProgress.value.project.status
  if (mergedProgress.value.blockers.some(item => ['high', 'critical'].includes(String(item.severity)))) {
    return 'is-blocked'
  }
  return `is-${status || 'active'}`
})

const updatedLabel = computed(() => {
  const value = mergedProgress.value.updatedAt
  if (!value) return '未更新'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})

function handleFollowSwitch(event: { detail?: { value?: boolean } }) {
  followEnabled.value = Boolean(event.detail?.value)
  followMessage.value = ''
  if (followEnabled.value) navigateToFocus()
}

const fetchProgress = async () => {
  if (!shouldRender.value) return
  try {
    const separator = props.src.includes('?') ? '&' : '?'
    const response = await fetch(`${props.src}${separator}t=${Date.now()}`, {
      cache: 'no-store',
    })
    if (!response.ok || !String(response.headers.get('content-type') || '').includes('application/json')) {
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
  if (!savedPosition.value) {
    x.value = defaultPosition.value.x
    y.value = defaultPosition.value.y
  }
  nextTick(clampOverlayIntoView)
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
  <aside
    v-if="shouldRender"
    ref="overlayRef"
    class="delivery-progress-overlay"
    :class="[statusClass, { 'is-open': isOpen, 'is-dragging': isDragging }]"
    :style="overlayStyle"
  >
    <button ref="dragHandleRef" class="delivery-progress-button" @click="isOpen = !isOpen">
      <strong>{{ mergedProgress.milestone.progress }}%</strong>
      <span v-if="isStale" class="stale-dot" title="Progress data is stale" />
    </button>

    <section v-if="isOpen" class="delivery-progress-panel">
      <header class="panel-header">
        <div>
          <p class="eyebrow">开发进度</p>
          <h2>{{ mergedProgress.milestone.name || mergedProgress.project.name }}</h2>
        </div>
        <button class="close-button" aria-label="Close progress panel" @click="isOpen = false">
          x
        </button>
      </header>

      <div class="progress-hero">
        <strong>{{ mergedProgress.milestone.progress }}%</strong>
        <div>
          <span>{{ mergedProgress.project.status }}</span>
          <p>{{ mergedProgress.milestone.currentTask }}</p>
        </div>
      </div>
      <div class="bar"><i :style="{ width: `${mergedProgress.milestone.progress}%` }" /></div>

      <section class="focus-card">
        <span class="label">当前页面</span>
        <strong>{{ mergedProgress.focus.pageName || '未指定页面' }}</strong>
        <p v-if="mergedProgress.focus.activity">{{ mergedProgress.focus.activity }}</p>
        <label class="follow-toggle" :class="{ 'is-disabled': !followAvailable }">
          <switch class="follow-switch" :checked="followEnabled" :disabled="!followAvailable" @change="handleFollowSwitch" />
          <span>跟随页面</span>
        </label>
      </section>
      <p v-if="followMessage || followUnavailableReason" class="follow-message">
        {{ followMessage || followUnavailableReason }}
      </p>

      <div class="next-card">
        <span class="label">下一步</span>
        <strong>{{ mergedProgress.milestone.nextAction }}</strong>
      </div>

      <div v-if="mergedProgress.blockers.length" class="section-block blockers">
        <h3>阻塞</h3>
        <ul>
          <li v-for="(blocker, index) in mergedProgress.blockers.slice(0, 2)" :key="`${blocker.title || 'blocker'}-${index}`">
            <span class="pill">{{ blocker.severity || 'medium' }}</span>
            {{ blocker.title || 'Untitled blocker' }}
          </li>
        </ul>
      </div>

      <footer>
        <span>{{ mergedProgress.checks.status }}</span>
        <span>{{ updatedLabel }}</span>
        <span v-if="isStale">{{ lastError }}</span>
      </footer>
    </section>
  </aside>
</template>

<style scoped>
.delivery-progress-overlay {
  --accent: #2563eb;
  --accent-soft: rgba(37, 99, 235, 0.12);
  position: fixed;
  z-index: 9999;
  color: #0f172a;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  touch-action: none;
  user-select: none;
}

.is-dragging .delivery-progress-button {
  cursor: grabbing;
  transform: scale(0.98);
}

.is-dragging .delivery-progress-panel {
  pointer-events: none;
}

.is-waiting { --accent: #7c3aed; --accent-soft: rgba(124, 58, 237, 0.12); }
.is-blocked { --accent: #dc2626; --accent-soft: rgba(220, 38, 38, 0.12); }
.is-paused { --accent: #64748b; --accent-soft: rgba(100, 116, 139, 0.12); }
.is-done { --accent: #16a34a; --accent-soft: rgba(22, 163, 74, 0.12); }
.is-warning { --accent: #d97706; --accent-soft: rgba(217, 119, 6, 0.14); }

.delivery-progress-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 52px;
  height: 36px;
  padding: 0;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), #0f172a);
  color: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.2);
  cursor: pointer;
}

.delivery-progress-button strong { font-size: 13px; line-height: 1; }
.stale-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #fbbf24;
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.25);
}

.delivery-progress-panel {
  position: absolute;
  right: 0;
  bottom: 46px;
  box-sizing: border-box;
  width: min(320px, calc(100vw - 24px));
  max-height: min(62vh, 520px);
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.22);
  backdrop-filter: blur(18px);
}

.panel-header {
  position: relative;
  padding-right: 28px;
  margin-bottom: 12px;
}

.eyebrow,
.label,
footer {
  margin: 0;
  color: #64748b;
  font-size: 10px;
  line-height: 1.35;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel-header h2 {
  margin: 3px 0 0;
  color: #0f172a;
  font-size: 17px;
  line-height: 1.25;
}

.close-button {
  position: absolute;
  top: -4px;
  right: -4px;
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  background: #f8fafc;
  color: #64748b;
  line-height: 1;
  cursor: pointer;
}

.progress-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 12px;
}

.progress-hero > strong {
  color: var(--accent);
  font-size: 38px;
  line-height: 1;
  letter-spacing: -0.06em;
}

.progress-hero span {
  display: inline-flex;
  width: fit-content;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 10px;
  font-weight: 800;
}

.progress-hero p {
  margin: 6px 0 0;
  color: #334155;
  font-size: 13px;
  line-height: 1.45;
}

.bar {
  overflow: hidden;
  width: 100%;
  height: 8px;
  margin-top: 12px;
  border-radius: 999px;
  background: #e2e8f0;
}

.bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), #38bdf8);
}

.focus-card,
.next-card,
.section-block {
  margin-top: 12px;
  padding: 11px;
  border-radius: 16px;
  background: var(--accent-soft);
}

.focus-card,
.next-card {
  display: grid;
  gap: 6px;
}

.focus-card strong,
.next-card strong {
  color: #0f172a;
  font-size: 14px;
  line-height: 1.35;
}

.focus-card p {
  margin: 0;
  color: #475569;
  font-size: 12px;
  line-height: 1.45;
}

.follow-toggle {
  display: inline-flex;
  width: fit-content;
  max-width: 100%;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
  padding: 5px 8px 5px 5px;
  border-radius: 999px;
  background: rgb(255 255 255 / 72%);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}
.follow-switch {
  flex: none;
  transform: scale(0.72);
  transform-origin: left center;
}
.follow-toggle.is-disabled { color: #94a3b8; }
.follow-message {
  margin: 7px 0 0;
  color: #64748b;
  font-size: 12px;
}

.next-card {
  background: #f8fafc;
}

.section-block { background: rgba(220, 38, 38, 0.08); }
.section-block h3 {
  margin: 0 0 8px;
  color: #991b1b;
  font-size: 13px;
}
.section-block ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.section-block li {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 8px;
  color: #0f172a;
  font-size: 12px;
  line-height: 1.45;
}
.pill {
  flex: none;
  border-radius: 999px;
  background: rgba(220, 38, 38, 0.12);
  padding: 2px 7px;
  color: #dc2626;
  font-size: 10px;
  font-weight: 800;
}

footer {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
  text-transform: none;
  letter-spacing: 0;
}
</style>
