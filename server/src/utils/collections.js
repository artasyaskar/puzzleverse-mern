// General-purpose collection and functional utilities.
// Intentionally verbose to provide a rich starter utility surface.

export function range(start, end, step = 1) {
  const out = []
  if (step === 0) return out
  if (start <= end) {
    for (let i = start; i <= end; i += step) out.push(i)
  } else {
    for (let i = start; i >= end; i -= Math.abs(step)) out.push(i)
  }
  return out
}

export function chunk(arr, size) {
  if (!Array.isArray(arr) || size <= 0) return []
  const out = []
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size))
  }
  return out
}

export function compact(arr) {
  if (!Array.isArray(arr)) return []
  const out = []
  for (let i = 0; i < arr.length; i++) {
    const v = arr[i]
    if (v) out.push(v)
  }
  return out
}

export function flatten(arr) {
  if (!Array.isArray(arr)) return []
  const out = []
  const stack = [...arr]
  while (stack.length) {
    const v = stack.shift()
    if (Array.isArray(v)) stack.unshift(...v)
    else out.push(v)
  }
  return out
}

export function uniq(arr) {
  if (!Array.isArray(arr)) return []
  const set = new Set()
  const out = []
  for (let i = 0; i < arr.length; i++) {
    const v = arr[i]
    if (!set.has(v)) {
      set.add(v)
      out.push(v)
    }
  }
  return out
}

export function groupBy(arr, fn) {
  const map = new Map()
  if (!Array.isArray(arr)) return map
  for (let i = 0; i < arr.length; i++) {
    const item = arr[i]
    const key = fn(item, i)
    const bucket = map.get(key)
    if (bucket) bucket.push(item)
    else map.set(key, [item])
  }
  return map
}

export function keyBy(arr, fn) {
  const obj = Object.create(null)
  if (!Array.isArray(arr)) return obj
  for (let i = 0; i < arr.length; i++) {
    const item = arr[i]
    const key = String(fn(item, i))
    obj[key] = item
  }
  return obj
}

export function partition(arr, predicate) {
  const yes = []
  const no = []
  for (let i = 0; i < arr.length; i++) {
    const v = arr[i]
    if (predicate(v, i)) yes.push(v)
    else no.push(v)
  }
  return [yes, no]
}

export function zip(a, b) {
  const len = Math.min(a.length, b.length)
  const out = []
  for (let i = 0; i < len; i++) out.push([a[i], b[i]])
  return out
}

export function unzip(pairs) {
  const a = []
  const b = []
  for (let i = 0; i < pairs.length; i++) {
    const [x, y] = pairs[i]
    a.push(x)
    b.push(y)
  }
  return [a, b]
}

export function difference(a, b) {
  const setB = new Set(b)
  const out = []
  for (let i = 0; i < a.length; i++) if (!setB.has(a[i])) out.push(a[i])
  return out
}

export function intersection(a, b) {
  const setB = new Set(b)
  const out = []
  for (let i = 0; i < a.length; i++) if (setB.has(a[i])) out.push(a[i])
  return out
}

export function union(a, b) {
  const set = new Set(a)
  for (let i = 0; i < b.length; i++) set.add(b[i])
  return Array.from(set)
}

export function shuffle(arr) {
  const out = arr.slice()
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    const tmp = out[i]
    out[i] = out[j]
    out[j] = tmp
  }
  return out
}

export function stableSort(arr, cmp) {
  const withIndex = arr.map((v, i) => ({ v, i }))
  withIndex.sort((a, b) => {
    const c = cmp(a.v, b.v)
    if (c !== 0) return c
    return a.i - b.i
  })
  return withIndex.map(x => x.v)
}

export function memoize(fn) {
  const cache = new Map()
  return (...args) => {
    const key = JSON.stringify(args)
    if (cache.has(key)) return cache.get(key)
    const res = fn(...args)
    cache.set(key, res)
    return res
  }
}

export function deepClone(value) {
  if (Array.isArray(value)) return value.map(deepClone)
  if (value && typeof value === 'object') {
    const out = {}
    for (const k of Object.keys(value)) out[k] = deepClone(value[k])
    return out
  }
  return value
}

export function deepEqual(a, b) {
  if (a === b) return true
  if (typeof a !== typeof b) return false
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false
    for (let i = 0; i < a.length; i++) if (!deepEqual(a[i], b[i])) return false
    return true
  }
  if (a && typeof a === 'object' && b && typeof b === 'object') {
    const ak = Object.keys(a)
    const bk = Object.keys(b)
    if (ak.length !== bk.length) return false
    for (let i = 0; i < ak.length; i++) {
      const k = ak[i]
      if (!deepEqual(a[k], b[k])) return false
    }
    return true
  }
  return false
}

export function clamp(n, min, max) {
  if (n < min) return min
  if (n > max) return max
  return n
}

export function sum(arr) {
  let s = 0
  for (let i = 0; i < arr.length; i++) s += arr[i]
  return s
}

export function average(arr) {
  if (!arr.length) return 0
  return sum(arr) / arr.length
}

export function median(arr) {
  if (!arr.length) return 0
  const copy = arr.slice().sort((a, b) => a - b)
  const mid = Math.floor(copy.length / 2)
  if (copy.length % 2 === 0) return (copy[mid - 1] + copy[mid]) / 2
  return copy[mid]
}

export function variance(arr) {
  if (!arr.length) return 0
  const avg = average(arr)
  let v = 0
  for (let i = 0; i < arr.length; i++) {
    const d = arr[i] - avg
    v += d * d
  }
  return v / arr.length
}

export function stddev(arr) {
  return Math.sqrt(variance(arr))
}

export function times(n, fn) {
  const out = []
  for (let i = 0; i < n; i++) out.push(fn(i))
  return out
}

export function mapValues(obj, fn) {
  const out = {}
  for (const k of Object.keys(obj)) out[k] = fn(obj[k], k)
  return out
}

export function pick(obj, keys) {
  const out = {}
  for (let i = 0; i < keys.length; i++) {
    const k = keys[i]
    if (Object.prototype.hasOwnProperty.call(obj, k)) out[k] = obj[k]
  }
  return out
}

export function omit(obj, keys) {
  const set = new Set(keys)
  const out = {}
  for (const k of Object.keys(obj)) if (!set.has(k)) out[k] = obj[k]
  return out
}

export function once(fn) {
  let done = false
  let value
  return (...args) => {
    if (done) return value
    done = true
    value = fn(...args)
    return value
  }
}
