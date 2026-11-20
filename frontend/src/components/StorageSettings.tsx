import { useEffect, useState } from 'react'

import { api, formatBytes, type StorageStatus, type StorageValidation } from '../api'
import { ErrorNote } from '../components/ErrorNote'

export function StorageSettings() {
  const [status, setStatus] = useState<StorageStatus | null>(null)
  const [path, setPath] = useState('')
  const [validation, setValidation] = useState<StorageValidation | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const reload = () => {
    void api.storageStatus().then(setStatus).catch((err) => setError(err as Error))
  }

  useEffect(reload, [])

  const validate = async () => {
    if (!path.trim()) return
    setBusy(true)
    setError(null)
    setValidation(null)
    try {
      const result = await api.validateStoragePath(path.trim())
      setValidation(result)
      setPath(result.path)
      reload()
    } catch (err) {
      setError(err as Error)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="rise mt-14">
      <div className="flex items-baseline justify-between gap-4 border-b border-ink-800 pb-2">
        <div>
          <h2 className="eyebrow">Storage</h2>
          <p className="mt-1 text-xs text-ink-500">
            See where data lives and verify another folder before using it.
          </p>
        </div>
        <button onClick={reload} className="btn btn-quiet">Refresh</button>
      </div>

      {error && (
        <div className="mt-4">
          <ErrorNote error={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {status ? (
        <div className="mt-5 space-y-3">
          {status.locations.map((location) => (
            <div key={location.name} className="border-b border-ink-850 pb-3">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="text-sm text-ink-200">{location.name}</span>
                <span className={`text-xs ${location.writable ? 'text-signal-good' : 'text-ink-500'}`}>
                  {location.writable ? 'writable' : 'not confirmed writable'}
                </span>
              </div>
              <code className="mt-1 block break-all text-xs text-ink-500">{location.path}</code>
              <p className="mt-1 text-xs text-ink-600">
                {location.exists ? 'Directory exists' : 'Not created yet'}
                {' · '}
                {location.free_bytes === null ? 'Free space unavailable' : formatBytes(location.free_bytes) + ' free'}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-5 text-sm text-ink-500">Loading storage locations…</p>
      )}

      <div className="mt-7 border-l-2 border-sodium-600 pl-4">
        <h3 className="text-sm text-ink-100">Validate a destination folder</h3>
        <p className="mt-1 text-xs leading-relaxed text-ink-500">
          Enter an absolute path. We create the folder if needed, write and remove a small test file, and report available space.
        </p>
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <label className="min-w-56 flex-1">
            <span className="eyebrow">Folder path</span>
            <input
              className="field mt-1 text-sm"
              value={path}
              onChange={(event) => {
                setPath(event.target.value)
                setValidation(null)
              }}
              placeholder="C:\\Users\\You\\Videos\\Melyqon"
              spellCheck={false}
            />
          </label>
          <button onClick={validate} disabled={!path.trim() || busy} className="btn btn-ghost">
            {busy ? 'Checking…' : 'Validate folder'}
          </button>
        </div>
        {validation && (
          <p className="mt-3 text-xs text-signal-good">
            Folder is writable · {formatBytes(validation.free_bytes)} free
            {validation.directory_created ? ' · folder created' : ''}
          </p>
        )}
        <p className="mt-3 text-xs text-ink-600">
          Validation only: this does not change active storage locations or move existing files. Storage migration is not enabled yet.
        </p>
      </div>
    </section>
  )
}
