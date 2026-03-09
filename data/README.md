# 📂 Data Directory

Carpeta para almacenar datos privados del portfolio (no incluidos en git).

## 📄 Archivos

### `delta_transactions.csv`

Archivo CSV con el histórico completo de transacciones del portfolio.

**Formato esperado:**
```csv
"Date","Way","Base amount","Base currency (name)","Base type","Quote amount",...
"2025-01-24T19:18:00.000Z","BUY",8,"NVDA (NVIDIA Corp)","STOCK",1015.2,"USD",...
```

**Campos importantes:**
- `Way`: `BUY` o `SELL`
- `Base amount`: Cantidad de shares
- `Base currency (name)`: Ticker y nombre (ej: `NVDA (NVIDIA Corp)`)
- `Base type`: Debe ser `STOCK`
- `Quote amount`: Dinero pagado/recibido en USD

**Origen:** Exportado desde Delta app o broker.

## 🔧 Uso

### Generar `config/positions.json` desde CSV

```bash
python3 scripts/generate_positions.py
```

El script:
1. ✅ Lee todas las transacciones de `data/delta_transactions.csv`
2. ✅ Calcula shares actuales (compras - ventas)
3. ✅ Calcula cost basis efectivo (dinero neto invertido / shares actuales)
4. ✅ Genera `config/positions.json` con el formato correcto

**Método de cálculo:**
- **Dinero neto invertido** = Σ(compras) - Σ(ventas)
- **Shares actuales** = Σ(shares compradas) - Σ(shares vendidas)
- **Cost basis efectivo** = Dinero neto invertido / Shares actuales

Ejemplo:
```
NVDA:
- Comprado 8 @ $1,015.20 + 16 @ $1,505.92 + ... = Total pagado
- Vendido 8 @ $1,118.00 = Total recibido
- Dinero neto = Total pagado - Total recibido = $4,748.25
- Shares actuales = 39
- Cost basis = $4,748.25 / 39 = $121.75
```

Este método refleja el **dinero real que tienes invertido actualmente** en cada posición.

## 🔒 Privacidad

⚠️ **Todos los archivos `.csv` en esta carpeta están en `.gitignore`**

Nunca se subirán a git para proteger tu información financiera privada.

## 📊 Workflow Recomendado

1. **Actualiza el CSV** cuando hagas nuevas transacciones
2. **Regenera positions.json:**
   ```bash
   python3 scripts/generate_positions.py
   ```
3. **Reinicia BLOOMY:**
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.jballesteros.bloomy
   ```
4. ✅ Dashboard actualizado con tus posiciones reales

## 📝 Notas

- Solo se incluyen posiciones con `shares > 0` (posiciones cerradas se excluyen)
- El cost basis se redondea a 2 decimales
- Soporta cualquier ticker de acciones US
