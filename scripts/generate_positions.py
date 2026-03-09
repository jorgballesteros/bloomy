#!/usr/bin/env python3
"""
Generate config/positions.json from data/delta_transactions.csv

Calcula el cost basis efectivo (dinero neto invertido / shares actuales)
según el método definido en MEMORY.md del portfolio.
"""

import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path

def extract_ticker(base_currency):
    """Extrae ticker del formato 'TICKER (Company Name)'"""
    match = re.match(r'^([A-Z]+)\s+\(', base_currency)
    return match.group(1) if match else None

def calculate_positions(csv_path):
    """
    Calcula posiciones desde CSV de transacciones.
    
    Método:
    - Total dinero invertido = suma(compras) - suma(ventas)
    - Shares actuales = suma(shares compradas) - suma(shares vendidas)
    - Cost basis efectivo = dinero neto invertido / shares actuales
    """
    positions = defaultdict(lambda: {
        'shares_bought': 0,
        'shares_sold': 0,
        'money_paid': 0.0,
        'money_received': 0.0
    })
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            way = row['Way']
            base_type = row['Base type']
            
            # Solo procesar operaciones de STOCK (BUY/SELL)
            if base_type != 'STOCK' or way not in ['BUY', 'SELL']:
                continue
            
            ticker = extract_ticker(row['Base currency (name)'])
            if not ticker:
                continue
            
            shares = float(row['Base amount'])
            amount_usd = float(row['Quote amount'])
            
            if way == 'BUY':
                positions[ticker]['shares_bought'] += shares
                positions[ticker]['money_paid'] += amount_usd
            elif way == 'SELL':
                positions[ticker]['shares_sold'] += shares
                positions[ticker]['money_received'] += amount_usd
    
    # Calcular posiciones finales
    result = {}
    
    for ticker, data in positions.items():
        current_shares = data['shares_bought'] - data['shares_sold']
        
        # Solo incluir si hay shares actualmente
        if current_shares <= 0:
            continue
        
        net_invested = data['money_paid'] - data['money_received']
        cost_basis = net_invested / current_shares
        
        result[ticker] = {
            'shares': int(current_shares),
            'cost_basis': round(cost_basis, 2)
        }
    
    return result

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    csv_path = project_dir / 'data' / 'delta_transactions.csv'
    output_path = project_dir / 'config' / 'positions.json'
    
    # Verificar que existe el CSV
    if not csv_path.exists():
        print(f"❌ Error: No se encontró {csv_path}")
        print("   Coloca el archivo delta_transactions.csv en la carpeta data/")
        return 1
    
    # Calcular posiciones
    print(f"📊 Leyendo transacciones desde {csv_path.name}...")
    positions = calculate_positions(csv_path)
    
    if not positions:
        print("⚠️  No se encontraron posiciones activas")
        return 1
    
    # Mostrar resumen
    print(f"\n✅ Posiciones calculadas:")
    print(f"{'Ticker':<10} {'Shares':<10} {'Cost Basis':<12} {'Invested':<12}")
    print("-" * 50)
    
    for ticker, data in sorted(positions.items()):
        invested = data['shares'] * data['cost_basis']
        print(f"{ticker:<10} {data['shares']:<10} ${data['cost_basis']:<11.2f} ${invested:,.2f}")
    
    total_invested = sum(p['shares'] * p['cost_basis'] for p in positions.values())
    print("-" * 50)
    print(f"{'TOTAL':<10} {'':<10} {'':<12} ${total_invested:,.2f}")
    
    # Crear directorio config si no existe
    output_path.parent.mkdir(exist_ok=True)
    
    # Guardar JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(positions, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Archivo generado: {output_path}")
    print(f"\n🚀 Reinicia BLOOMY para ver los cambios:")
    print(f"   launchctl kickstart -k gui/$(id -u)/com.jballesteros.bloomy")
    
    return 0

if __name__ == '__main__':
    exit(main())
