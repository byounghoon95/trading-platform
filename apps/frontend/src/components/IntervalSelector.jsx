const intervals = ['1m', '5m', '15m', '1h', '1d']

export function IntervalSelector({ disabled, value, onChange }) {
  return (
    <label>
      Interval
      <select
        disabled={disabled}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {intervals.map((interval) => (
          <option key={interval} value={interval}>
            {interval}
          </option>
        ))}
      </select>
    </label>
  )
}
