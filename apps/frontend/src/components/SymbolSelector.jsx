export function SymbolSelector({ disabled, markets, value, onChange }) {
  return (
    <label>
      Symbol
      <select
        disabled={disabled}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {markets.map((market) => (
          <option key={market.symbol} disabled={!market.enabled} value={market.symbol}>
            {market.displayName}
          </option>
        ))}
      </select>
    </label>
  )
}
