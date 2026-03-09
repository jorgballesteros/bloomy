# 📊 BLOOMY

**Bloomberg-style Opportunity Monitor You**

Dashboard profesional de portfolio con datos en tiempo real, estilo Binance/trading moderno.

## ✨ Características

- 📈 **Monitoreo en vivo** de posiciones (NBIS, NVDA, OKLO)
- 📊 **Gráficos profesionales**: Candlestick + RSI + Volumen
- 🎯 **Watchlist** con oportunidades paginadas
- 🔄 **Auto-refresh** cada 60 segundos
- 📝 **Análisis integrado** del último informe de portfolio
- 🎨 **Diseño moderno** inspirado en Binance (negro azulado + cyan)

## 🚀 Stack Técnico

- **Python 3.9+**
- **Dash 2.14+** - Framework web
- **Plotly 5.18+** - Gráficos interactivos
- **yfinance 0.2.32+** - Datos de mercado en tiempo real
- **Dash Bootstrap Components 1.5+** - UI components

## 📦 Instalación

```bash
# Clonar repo
git clone git@github.com:jorgballesteros/bloomy.git
cd bloomy

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar posiciones y watchlist
cp config/positions.example.json config/positions.json
cp config/opportunities.example.json config/opportunities.json

# Editar con tus datos
nano config/positions.json
nano config/opportunities.json
```

## 🏃 Uso

### Inicio Manual

```bash
./scripts/start_dashboard.sh
```

Dashboard disponible en: http://127.0.0.1:8050

### Servicio Automático (macOS)

Configurar como servicio launchd para auto-start:

```bash
# Copiar plist
cp com.jballesteros.bloomy.plist ~/Library/LaunchAgents/

# Editar rutas en el archivo (si necesario)
nano ~/Library/LaunchAgents/com.jballesteros.bloomy.plist

# Cargar servicio
launchctl load ~/Library/LaunchAgents/com.jballesteros.bloomy.plist

# Verificar estado
launchctl list | grep bloomy
```

**Comandos útiles:**

```bash
# Reiniciar
launchctl kickstart -k gui/$(id -u)/com.jballesteros.bloomy

# Ver logs
tail -f ~/Library/Logs/bloomy.log

# Detener
launchctl unload ~/Library/LaunchAgents/com.jballesteros.bloomy.plist
```

## 📂 Estructura

```
bloomy/
├── app.py                          # Aplicación principal Dash
├── requirements.txt                # Dependencias Python
├── config/
│   ├── positions.json              # Tus posiciones (no en git)
│   ├── opportunities.json          # Tu watchlist (no en git)
│   ├── positions.example.json      # Template posiciones
│   └── opportunities.example.json  # Template watchlist
├── data/
│   ├── delta_transactions.csv      # Histórico de transacciones (no en git)
│   └── README.md                   # Documentación data/
├── reports/
│   └── analysis.json               # Análisis del último informe (no en git)
├── scripts/
│   ├── start_dashboard.sh          # Script de inicio manual
│   ├── check_status.sh             # Verificador de estado
│   └── update_positions.sh         # Actualiza positions y reinicia
├── src/
│   └── generate_positions.py       # Genera positions.json desde CSV
├── assets/
│   └── style.css                   # Estilos personalizados
└── README.md                       # Este archivo
```

## 🎨 Paleta de Colores

- **Background Primary:** `#0B0E11` (Negro azulado)
- **Background Card:** `#181A20` (Gris oscuro)
- **Accent (Branding):** `#51C4C8` (Cyan)
- **Green (Up):** `#0ECB81` (Verde trading)
- **Red (Down):** `#F6465D` (Rojo trading)
- **Text Primary:** `#EAECEF` (Blanco suave)
- **Text Secondary:** `#848E9C` (Gris medio)

## 📝 Configuración

### Personalizar Posiciones

**Opción 1: Generar desde CSV de transacciones (Recomendado)**

1. Coloca tu CSV de transacciones en `data/delta_transactions.csv`
2. Ejecuta el script generador:
   ```bash
   python3 src/generate_positions.py
   ```
3. Se genera automáticamente `config/positions.json` con el cost basis real

**Opción 2: Editar manualmente**

Editar `config/positions.json`:

```json
{
  "TICKER": {
    "shares": 100,
    "cost_basis": 50.00
  }
}
```

### Actualizar Watchlist

Editar `config/opportunities.json`:

```json
[
  {
    "ticker": "TICKER",
    "name": "Company Name",
    "sector": "Sector"
  }
]
```

### Actualizar Análisis

Editar `reports/analysis.json`:

```json
{
  "last_update": "2026-03-09 10:00",
  "TICKER": {
    "recommendation": "MANTENER",
    "key_points": ["Point 1", "Point 2"],
    "alert_levels": "Niveles clave"
  }
}
```

**Nota:** Los archivos `config/positions.json`, `config/opportunities.json` y `reports/analysis.json` están en `.gitignore` y no se subirán a git (datos privados).

## 📊 Indicadores Técnicos

- **RSI (14):** Índice de Fuerza Relativa
- **SMA 20/50:** Medias móviles simples
- **Volumen:** Con colores según dirección del precio
- **Sparklines:** Mini gráficos de tendencia en cards
- **52W High Distance:** Distancia desde máximo anual

## 🛠️ Desarrollo

```bash
# Modo debug
python app.py  # Con debug=True en código

# Hot reload automático con cambios
# (Dash incluye hot reload por defecto en debug mode)
```

## 📜 Licencia

MIT License - Uso libre y modificación permitida

## 👤 Autor

Jorge Ballesteros ([@jorgballesteros](https://github.com/jorgballesteros))

---

**Versión:** 3.0 (Binance Aesthetic)  
**Última actualización:** 9 Marzo 2026
