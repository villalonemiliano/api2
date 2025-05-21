import yfinance as yf
import pandas as pd
import datetime
import pytz
import sqlite3
import time
import threading
from typing import Dict, Tuple, Optional

class AnalysisService:
    # Configuración
    TICKERS = [ "AAPL", "VOO", "AMZN", "NVDA", "GOOGL", "META", "BRK.B", "AVGO", "TSLA", "UNH",
                "LLY", "V", "JPM", "WMT", "XOM", "MA", "PG", "CVX", "MRK", "COST",
                "ABBV", "HD", "PEP", "BAC", "ADBE", "KO", "PFE", "NFLX", "TMO", "LIN",
                "CRM", "AMD", "WFC", "ACN", "ABT", "DHR", "VZ", "INTC", "MCD", "DIS",
                "NEE", "QCOM", "BMY", "TXN", "LOW", "HON", "AMGN", "UNP", "IBM", "CAT",
                "SPGI", "RTX", "NOW", "GS", "GE", "BLK", "ISRG", "INTU", "ELV", "LMT",
                "MDT", "SYK", "ADP", "AMAT", "TJX", "PLD", "NKE", "CVS", "T", "DE",
                "PANW", "PYPL", "PGR", "C", "VRTX", "ZTS", "MS", "AXP", "MO", "BKNG",
                "MU", "SCHW", "UBER", "HUM", "SO", "FI", "LRCX", "GILD", "ADI", "MMC",
                "REGN", "ETN", "TGT", "FDX", "VRTX", "ATVI", "CI", "CL", "COP", "DUK",
                "EW", "ORCL", "MCK", "APD", "ADSK", "ILMN", "PH", "NXPI", "ROP", "KDP",
                "CSCO", "BSX", "CHTR", "AON", "MAR", "FISV", "MPC", "PXD", "AEP", "NSC",
                "PCAR", "OXY", "TDG", "FTNT", "IDXX", "HCA", "MNST", "SRE", "CDNS", "D",
                "KLAC", "AIG", "DG", "SHW", "CMI", "SLB", "SNPS", "PSX", "WMB", "AJG",
                "CTAS", "MSI", "SBUX", "OKE", "PSA", "F", "VLO", "ADM", "APTV", "BIIB",
                "TRV", "EOG", "MTD", "FIS", "MCO", "ROST", "WELL", "ITW", "XEL", "CB",
                "OTIS", "HPQ", "BKR", "DOW", "KHC", "PAYX", "CME", "ANET", "IQV", "WY",
                "NOC", "HES", "BAX", "FAST", "CTSH", "PPG", "YUM", "ACGL", "DLTR", "AWK",
                "TT", "DHI", "PCG", "VRSK", "ROK", "STZ", "ECL", "HLT", "MTB", "RMD",
                "EFX", "AME", "FLT", "AFL", "SPG", "TTWO", "ALL", "WST", "PRU", "VICI",
                "RSG", "GWW", "FANG", "VTR", "WAB", "SYY", "AVB", "PEG", "CHD", "TDY",
                "BALL", "CARR", "LYB", "KEYS", "STT", "EXC", "IR", "COF", "ED", "MAA",
                "ZBRA", "KMB", "KR", "BRO", "PPL", "HSY", "BF.B", "ALB", "LH", "NDAQ",
                "TSCO", "TYL", "MPWR", "EPAM", "NTRS", "INVH", "CCEP", "NUE", "CF", "VMC",
                "HWM", "TSN", "APA", "DRI", "GLW", "CTVA", "CRWD", "OKE", "MSCI", "GPC",
                "ULTA", "BXP", "ARE", "CNP", "IP", "HOLX", "AES", "MKTX", "DPZ", "AKAM",
                "FMC", "CE", "ABC", "EXPE", "PKG", "NVR", "WDC", "PFG", "NTAP", "HIG",
                "TECH", "LKQ", "CDW", "MOS", "CLX", "BBY", "AEE", "CINF", "BURL", "SWK",
                "ESS", "OMC", "TXT", "WYNN", "LVS", "TSLA", "COIN", "HOOD", "SHOP", "ROKU",
                "LYFT", "SNOW", "NET", "DDOG", "ZS", "OKTA", "TWLO", "TEAM", "DOCU", "WDAY",
                "SQ", "UBER", "CRM", "PYPL", "PANW", "SNPS", "DDOG", "ROKU", "ZM", "DOCU"]
    INTERVAL = "1d"
    HISTORICAL_PERIODS = 20
    MAX_RETRIES = 2
    RETRY_DELAY = 2
    REQUEST_TIMEOUT = 2

    @staticmethod
    def fetch_technical_data(symbol: str) -> Dict:
        """
        Obtiene datos técnicos de Yahoo Finance con validación robusta
        """
        for attempt in range(AnalysisService.MAX_RETRIES):
            try:
                ticker = yf.Ticker(symbol)
                
                # Obtener datos históricos
                hist = ticker.history(period="1y", interval=AnalysisService.INTERVAL)
                
                if hist.empty:
                    print(f"Datos históricos vacíos para {symbol}, intento {attempt + 1}")
                    time.sleep(AnalysisService.RETRY_DELAY)
                    continue
                    
                # Validar que tengamos datos recientes
                last_date = hist.index[-1]
                if (datetime.datetime.now(pytz.UTC) - last_date).days > 7:
                    print(f"Datos desactualizados para {symbol} (última fecha: {last_date})")
                    time.sleep(AnalysisService.RETRY_DELAY)
                    continue
                    
                return {
                    'success': True,
                    'data': hist,
                    'last_update': last_date.isoformat()
                }
                
            except Exception as e:
                print(f"Error obteniendo datos técnicos para {symbol}, intento {attempt + 1}: {str(e)}")
                if attempt < AnalysisService.MAX_RETRIES - 1:
                    time.sleep(AnalysisService.RETRY_DELAY)
        
        return {
            'success': False,
            'error': f"No se pudieron obtener datos técnicos para {symbol} después de {AnalysisService.MAX_RETRIES} intentos"
        }

    @staticmethod
    def fetch_fundamental_data(symbol: str) -> Dict:
        """
        Obtiene datos fundamentales de Yahoo Finance sin reintentos
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
                
            if not info:
                print(f"Datos fundamentales vacíos para {symbol}")
                return {
                    'success': False,
                    'error': "Datos fundamentales no disponibles"
                }
                    
            return {
                'success': True,
                'data': info,
                'last_update': datetime.datetime.now(pytz.UTC).isoformat()
            }
                
        except Exception as e:
            print(f"Error obteniendo datos fundamentales para {symbol}: {str(e)}")
            return {
                'success': False,
                'error': f"Error obteniendo datos fundamentales: {str(e)}"
            }

    @staticmethod
    def calculate_technical_indicators(hist: pd.DataFrame) -> Dict:
        """Calcula indicadores técnicos con validación de datos"""
        try:
            if hist.empty:
                raise ValueError("Datos históricos vacíos")
                
            latest = hist.iloc[-1]
            close = latest['Close']
            high = latest['High']
            low = latest['Low']
            open_price = latest['Open']
            volume = latest['Volume']
            
            # Promedios móviles
            periods = [5, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 100, 150, 200]
            sma = {f'sma_{p}': hist['Close'].rolling(window=p).mean().iloc[-1] for p in periods}
            ema = {f'ema_{p}': hist['Close'].ewm(span=p, adjust=False).mean().iloc[-1] for p in periods}
            
            # Cambios porcentuales respecto al precio
            sma_pct = {f'sma_{p}_pct': ((sma[f'sma_{p}'] - close) / close) * 100 for p in periods}
            ema_pct = {f'ema_{p}_pct': ((ema[f'ema_{p}'] - close) / close) * 100 for p in periods}
            
            # Puntos pivot
            pivot = round((high + low + close) / 3, 2)
            r1 = round((2 * pivot) - low, 2)
            r2 = round(pivot + (high - low), 2)
            s1 = round((2 * pivot) - high, 2)
            s2 = round(pivot - (high - low), 2)
            
            # Cambios porcentuales de puntos pivot
            pivot_pct = ((pivot - close) / close) * 100
            r1_pct = ((r1 - close) / close) * 100
            r2_pct = ((r2 - close) / close) * 100
            s1_pct = ((s1 - close) / close) * 100
            s2_pct = ((s2 - close) / close) * 100
            
            # Cambios porcentuales diarios
            pct_change = {
                '1d': hist['Close'].pct_change().iloc[-1] * 100,
                '5d': hist['Close'].pct_change(5).iloc[-1] * 100,
                '20d': hist['Close'].pct_change(20).iloc[-1] * 100,
                '50d': hist['Close'].pct_change(50).iloc[-1] * 100
            }
            
            # Datos históricos
            historical_pct = {}
            for i in range(1, AnalysisService.HISTORICAL_PERIODS + 1):
                idx = -i
                if abs(idx) <= len(hist):
                    day_close = hist.iloc[idx]['Close']
                    if i == 1:
                        prev_close = hist.iloc[idx-1]['Close'] if abs(idx) < len(hist) else day_close
                        change = ((day_close - prev_close) / prev_close) * 100
                    else:
                        change = ((day_close - close) / close) * 100
                    historical_pct[f'hist_pct_{i}d'] = change
            
            return {
                'price': round(close, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'volume': int(volume),
                **sma,
                **ema,
                **sma_pct,
                **ema_pct,
                'pivot': pivot,
                'r1': r1, 'r2': r2,
                's1': s1, 's2': s2,
                'pivot_pct': pivot_pct,
                'r1_pct': r1_pct,
                'r2_pct': r2_pct,
                's1_pct': s1_pct,
                's2_pct': s2_pct,
                'pct_change': pct_change,
                **historical_pct
            }
        except Exception as e:
            raise ValueError(f"Error calculando indicadores técnicos: {str(e)}")

    @staticmethod
    def _classify_short_term(price: float, indicators: Dict) -> Tuple[str, float]:
        """Clasificación a corto plazo según el PDF"""
        try:
            ema5 = indicators.get('ema_5', price)
            ema10 = indicators.get('ema_10', price)
            pivot = indicators.get('pivot', price)
            r1 = indicators.get('r1', price * 1.05)
            s1 = indicators.get('s1', price * 0.95)
            
            # Evaluación de Puntos Pivot (40% peso)
            if price > r1 * 1.02:
                pivot_score = 2.5
            elif price > r1:
                pivot_score = 1.5
            elif price > pivot * 1.01:
                pivot_score = 0.5
            elif abs(price - pivot) / pivot <= 0.01:
                pivot_score = 0
            elif price > s1 * 0.99:
                pivot_score = -1
            else:
                pivot_score = -2
            
            # Evaluación de EMAs (40% peso)
            if price > ema5 > ema10 and price > ema5 * 1.02:
                ema_score = 2.5
            elif price > (ema5 + ema10) / 2 * 1.02:
                ema_score = 1.5
            elif min(ema5, ema10) <= price <= max(ema5, ema10):
                ema_score = 0
            else:
                ema_score = -1.5
            
            # Momentum (20% peso)
            momentum_1d = indicators.get('pct_change', {}).get('1d', 0)
            if momentum_1d > 2.5:
                momentum_score = 1.5
            elif momentum_1d > 1.0:
                momentum_score = 0.75
            elif momentum_1d < -2.5:
                momentum_score = -1.5
            elif momentum_1d < -1.0:
                momentum_score = -0.75
            else:
                momentum_score = 0
            
            total_score = (pivot_score * 0.3) + (ema_score * 0.6) + (momentum_score * 0.1)
            
            if total_score >= 2.0:
                return "Muy Buena", round(total_score, 2)
            elif total_score >= 1.0:
                return "Buena", round(total_score, 2)
            elif total_score >= -0.5:
                return "Neutral", round(total_score, 2)
            elif total_score >= -1.5:
                return "Mala", round(total_score, 2)
            else:
                return "Muy Mala", round(total_score, 2)
        except Exception as e:
            print(f"Error en clasificación corto plazo: {str(e)}")
            return "Error", 0

    @staticmethod
    def _classify_medium_term(price: float, indicators: Dict, fundamental_score: float) -> Tuple[str, float]:
        """Clasificación a mediano plazo según el PDF (80% técnico, 20% fundamental)"""
        try:
            sma20 = indicators.get('sma_20', price)
            sma50 = indicators.get('sma_50', price)
            pivot = indicators.get('pivot', price)
            r1 = indicators.get('r1', price * 1.05)
            s1 = indicators.get('s1', price * 0.95)
            
            # Evaluación de Promedios Móviles (50% peso técnico)
            if price > sma50 > sma20 and price > sma50 * 1.05:
                ma_score = 2.5
            elif price > sma50 and price > sma20:
                ma_score = 1.5
            elif min(sma20, sma50) <= price <= max(sma20, sma50):
                ma_score = 0
            elif price < sma20 and price > sma50:
                ma_score = -1
            else:
                ma_score = -2.5
            
            # Evaluación de Puntos Pivot (30% peso técnico)
            if price > r1 * 1.02:
                pivot_score = 1.5
            elif price > r1:
                pivot_score = 1.0
            elif price > pivot * 1.01:
                pivot_score = 0.5
            elif abs(price - pivot) / pivot <= 0.01:
                pivot_score = 0
            elif price > s1 * 0.99:
                pivot_score = -0.5
            else:
                pivot_score = -1.5
            
            # Normalizar fundamental_score a escala de -2.5 a 2.5 (20% peso)
            fund_score = (fundamental_score / 100 * 5) - 2.5 if fundamental_score is not None else 0
            
            total_score = (ma_score * 0.7) + (pivot_score * 0.2) + (fund_score * 0.1)
            
            if total_score >= 2.0:
                return "Muy Buena", round(total_score, 2)
            elif total_score >= 1.0:
                return "Buena", round(total_score, 2)
            elif total_score >= -0.5:
                return "Neutral", round(total_score, 2)
            elif total_score >= -1.5:
                return "Mala", round(total_score, 2)
            else:
                return "Muy Mala", round(total_score, 2)
        except Exception as e:
            print(f"Error en clasificación mediano plazo: {str(e)}")
            return "Error", 0

    @staticmethod
    def _classify_long_term(price: float, indicators: Dict, fundamental_score: float) -> Tuple[str, float]:
        """Clasificación a largo plazo según el PDF (55% técnico, 45% fundamental)"""
        try:
            sma100 = indicators.get('sma_100', price)
            sma200 = indicators.get('sma_200', price)
            pivot = indicators.get('pivot', price)
            r1 = indicators.get('r1', price * 1.05)
            s1 = indicators.get('s1', price * 0.95)
            
            # Evaluación de Promedios Móviles (30% peso técnico)
            if price > sma200 > sma100 and price > sma200 * 1.1:
                ma_score = 2.5
            elif price > sma200 and price > sma100:
                ma_score = 1.5
            elif min(sma100, sma200) <= price <= max(sma100, sma200):
                ma_score = 0
            elif price < sma100 and price > sma200:
                ma_score = -1
            else:
                ma_score = -2.5
            
            # Evaluación de Puntos Pivot (25% peso técnico)
            if price > r1 * 1.02:
                pivot_score = 1.25
            elif price > r1:
                pivot_score = 0.75
            elif price > pivot * 1.01:
                pivot_score = 0.25
            elif abs(price - pivot) / pivot <= 0.01:
                pivot_score = 0
            elif price > s1 * 0.99:
                pivot_score = -0.5
            else:
                pivot_score = -1.25
            
            # Normalizar fundamental_score a escala de -2.25 a 2.25 (45% peso)
            fund_score = (fundamental_score / 100 * 4.5) - 2.25 if fundamental_score is not None else 0
            
            total_score = (ma_score * 0.4) + (pivot_score * 0.15) + fund_score
            
            if total_score >= 2.0:
                return "Muy Buena", round(total_score, 2)
            elif total_score >= 1.0:
                return "Buena", round(total_score, 2)
            elif total_score >= -0.5:
                return "Neutral", round(total_score, 2)
            elif total_score >= -1.5:
                return "Mala", round(total_score, 2)
            else:
                return "Muy Mala", round(total_score, 2)
        except Exception as e:
            print(f"Error en clasificación largo plazo: {str(e)}")
            return "Error", 0

    @staticmethod
    def _calculate_fundamental_score(info: Dict) -> Optional[float]:
        """Calcula el score fundamental con validación robusta"""
        try:
            if not info:
                return None
                
            # Extraer datos con valores por defecto
            debt_equity = info.get('debtToEquity', 0)
            eps_growth = (info.get('earningsGrowth', 0) or 0) * 100
            gross_margin = (info.get('grossMargins', 0) or 0) * 100
            operating_margin = (info.get('operatingMargins', 0) or 0) * 100
            quick_ratio = info.get('quickRatio', 0)
            roa = (info.get('returnOnAssets', 0) or 0) * 100
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            pe_ratio = info.get('trailingPE', 0)
            revenue_growth = (info.get('revenueGrowth', 0) or 0) * 100
            
            # Funciones de scoring
            def score_debt_equity(x):
                if x < 0.3: return 100
                elif x < 0.6: return 80
                elif x < 0.9: return 60
                elif x < 1.2: return 40
                elif x < 1.8: return 20
                else: return 0
                
            def score_growth(x):
                if x > 25: return 100
                elif x > 18: return 85
                elif x > 12: return 70
                elif x > 6: return 50
                elif x > 0: return 30
                else: return 0
                
            def score_margin(x):
                if x > 55: return 100
                elif x > 45: return 85
                elif x > 35: return 70
                elif x > 25: return 50
                elif x > 15: return 30
                else: return 10
                
            def score_ratio(x, ideal=1):
                if x > ideal * 1.8: return 70
                elif x > ideal * 1.5: return 85
                elif x > ideal * 1.2: return 95
                elif x > ideal: return 80
                elif x > ideal * 0.8: return 60
                elif x > ideal * 0.5: return 40
                else: return 20
                
            # Pesos
            scores = {
                'debt_equity': score_debt_equity(debt_equity) * 0.12,
                'eps_growth': score_growth(eps_growth) * 0.15,
                'gross_margin': score_margin(gross_margin) * 0.12,
                'operating_margin': score_margin(operating_margin) * 0.12,
                'quick_ratio': score_ratio(quick_ratio) * 0.06,
                'roa': score_margin(roa) * 0.09,
                'roe': score_margin(roe) * 0.09,
                'pe_ratio': score_ratio(pe_ratio, 15) * 0.05,
                'revenue_growth': score_growth(revenue_growth) * 0.12
            }
            
            total_score = min(100, sum(scores.values()))
            return round(total_score, 2)
        except Exception as e:
            print(f"Error calculando score fundamental: {str(e)}")
            return None

    @staticmethod
    def _init_db():
        """Inicializa la base de datos con el esquema correcto"""
        try:
            conn = sqlite3.connect('stock_analysis.db')
            c = conn.cursor()
            
            # Verificar si la tabla ya existe
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis'")
            table_exists = c.fetchone()
            
            # Solo crear la tabla si no existe
            if not table_exists:
                # Crear nueva tabla con todas las columnas necesarias
                c.execute('''CREATE TABLE analysis
                             (symbol TEXT, 
                              timestamp DATETIME, 
                              price REAL,
                              open REAL,
                              high REAL,
                              low REAL,
                              volume INTEGER,
                              short_term TEXT, 
                              short_score REAL,
                              medium_term TEXT, 
                              medium_score REAL,
                              long_term TEXT, 
                              long_score REAL,
                              fund_score REAL,
                              sma_5 REAL, sma_5_pct REAL,
                              sma_8 REAL, sma_8_pct REAL,
                              sma_10 REAL, sma_10_pct REAL,
                              sma_12 REAL, sma_12_pct REAL,
                              sma_15 REAL, sma_15_pct REAL,
                              sma_20 REAL, sma_20_pct REAL,
                              sma_25 REAL, sma_25_pct REAL,
                              sma_30 REAL, sma_30_pct REAL,
                              sma_35 REAL, sma_35_pct REAL,
                              sma_40 REAL, sma_40_pct REAL,
                              sma_45 REAL, sma_45_pct REAL,
                              sma_50 REAL, sma_50_pct REAL,
                              sma_60 REAL, sma_60_pct REAL,
                              sma_75 REAL, sma_75_pct REAL,
                              sma_100 REAL, sma_100_pct REAL,
                              sma_150 REAL, sma_150_pct REAL,
                              sma_200 REAL, sma_200_pct REAL,
                              ema_5 REAL, ema_5_pct REAL,
                              ema_8 REAL, ema_8_pct REAL,
                              ema_10 REAL, ema_10_pct REAL,
                              ema_12 REAL, ema_12_pct REAL,
                              ema_15 REAL, ema_15_pct REAL,
                              ema_20 REAL, ema_20_pct REAL,
                              ema_25 REAL, ema_25_pct REAL,
                              ema_30 REAL, ema_30_pct REAL,
                              ema_35 REAL, ema_35_pct REAL,
                              ema_40 REAL, ema_40_pct REAL,
                              ema_45 REAL, ema_45_pct REAL,
                              ema_50 REAL, ema_50_pct REAL,
                              ema_60 REAL, ema_60_pct REAL,
                              ema_75 REAL, ema_75_pct REAL,
                              ema_100 REAL, ema_100_pct REAL,
                              ema_150 REAL, ema_150_pct REAL,
                              ema_200 REAL, ema_200_pct REAL,
                              pivot REAL, pivot_pct REAL,
                              r1 REAL, r1_pct REAL,
                              r2 REAL, r2_pct REAL,
                              s1 REAL, s1_pct REAL,
                              s2 REAL, s2_pct REAL,
                              debt_equity REAL,
                              eps_growth REAL,
                              gross_margin REAL,
                              operating_margin REAL,
                              quick_ratio REAL,
                              current_ratio REAL,
                              roa REAL,
                              roe REAL,
                              pe_ratio REAL,
                              forward_pe REAL,
                              peg_ratio REAL,
                              ps_ratio REAL,
                              pb_ratio REAL,
                              dividend_yield REAL,
                              beta REAL,
                              market_cap REAL,
                              enterprise_value REAL,
                              free_cash_flow REAL,
                              revenue_growth REAL,
                              operating_cash_flow REAL,
                              ebitda REAL,
                              total_debt REAL,
                              total_cash REAL,
                              shares_outstanding REAL,
                              PRIMARY KEY (symbol, timestamp))''')
                print("Tabla 'analysis' creada exitosamente")
            else:
                print("La tabla 'analysis' ya existe, no se necesita crear")
                
            conn.commit()
            conn.close()
        except Exception as e:
            raise RuntimeError(f"Error inicializando la base de datos: {str(e)}")

    @staticmethod
    def _store_analysis(symbol: str, technical_data: Dict, fundamental_data: Dict) -> bool:
        """Almacena el análisis en la base de datos"""
        try:
            # Clasificaciones
            short_term, short_score = AnalysisService._classify_short_term(technical_data['price'], technical_data)
            
            # Calcular score fundamental (puede ser None si no hay datos)
            fund_score = AnalysisService._calculate_fundamental_score(fundamental_data['data']) if fundamental_data['success'] else None
            
            # Clasificaciones con ponderación de datos fundamentales
            medium_term, medium_score = AnalysisService._classify_medium_term(technical_data['price'], technical_data, fund_score)
            long_term, long_score = AnalysisService._classify_long_term(technical_data['price'], technical_data, fund_score)
            
            # Conexión a la base de datos
            conn = sqlite3.connect('stock_analysis.db')
            c = conn.cursor()
            
            # Insertar datos
            values = (
                symbol,
                datetime.datetime.now(pytz.UTC).isoformat(),
                technical_data['price'],
                technical_data['open'],
                technical_data['high'],
                technical_data['low'],
                technical_data['volume'],
                short_term,
                short_score,
                medium_term,
                medium_score,
                long_term,
                long_score,
                fund_score,
                # SMAs y sus porcentajes
                technical_data.get('sma_5', 0), technical_data.get('sma_5_pct', 0),
                technical_data.get('sma_8', 0), technical_data.get('sma_8_pct', 0),
                technical_data.get('sma_10', 0), technical_data.get('sma_10_pct', 0),
                technical_data.get('sma_12', 0), technical_data.get('sma_12_pct', 0),
                technical_data.get('sma_15', 0), technical_data.get('sma_15_pct', 0),
                technical_data.get('sma_20', 0), technical_data.get('sma_20_pct', 0),
                technical_data.get('sma_25', 0), technical_data.get('sma_25_pct', 0),
                technical_data.get('sma_30', 0), technical_data.get('sma_30_pct', 0),
                technical_data.get('sma_35', 0), technical_data.get('sma_35_pct', 0),
                technical_data.get('sma_40', 0), technical_data.get('sma_40_pct', 0),
                technical_data.get('sma_45', 0), technical_data.get('sma_45_pct', 0),
                technical_data.get('sma_50', 0), technical_data.get('sma_50_pct', 0),
                technical_data.get('sma_60', 0), technical_data.get('sma_60_pct', 0),
                technical_data.get('sma_75', 0), technical_data.get('sma_75_pct', 0),
                technical_data.get('sma_100', 0), technical_data.get('sma_100_pct', 0),
                technical_data.get('sma_150', 0), technical_data.get('sma_150_pct', 0),
                technical_data.get('sma_200', 0), technical_data.get('sma_200_pct', 0),
                # EMAs y sus porcentajes
                technical_data.get('ema_5', 0), technical_data.get('ema_5_pct', 0),
                technical_data.get('ema_8', 0), technical_data.get('ema_8_pct', 0),
                technical_data.get('ema_10', 0), technical_data.get('ema_10_pct', 0),
                technical_data.get('ema_12', 0), technical_data.get('ema_12_pct', 0),
                technical_data.get('ema_15', 0), technical_data.get('ema_15_pct', 0),
                technical_data.get('ema_20', 0), technical_data.get('ema_20_pct', 0),
                technical_data.get('ema_25', 0), technical_data.get('ema_25_pct', 0),
                technical_data.get('ema_30', 0), technical_data.get('ema_30_pct', 0),
                technical_data.get('ema_35', 0), technical_data.get('ema_35_pct', 0),
                technical_data.get('ema_40', 0), technical_data.get('ema_40_pct', 0),
                technical_data.get('ema_45', 0), technical_data.get('ema_45_pct', 0),
                technical_data.get('ema_50', 0), technical_data.get('ema_50_pct', 0),
                technical_data.get('ema_60', 0), technical_data.get('ema_60_pct', 0),
                technical_data.get('ema_75', 0), technical_data.get('ema_75_pct', 0),
                technical_data.get('ema_100', 0), technical_data.get('ema_100_pct', 0),
                technical_data.get('ema_150', 0), technical_data.get('ema_150_pct', 0),
                technical_data.get('ema_200', 0), technical_data.get('ema_200_pct', 0),
                # Puntos pivot y sus porcentajes
                technical_data.get('pivot', 0), technical_data.get('pivot_pct', 0),
                technical_data.get('r1', 0), technical_data.get('r1_pct', 0),
                technical_data.get('r2', 0), technical_data.get('r2_pct', 0),
                technical_data.get('s1', 0), technical_data.get('s1_pct', 0),
                technical_data.get('s2', 0), technical_data.get('s2_pct', 0),
                # Datos fundamentales
                fundamental_data['data'].get('debtToEquity', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('earningsGrowth', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('grossMargins', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('operatingMargins', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('quickRatio', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('currentRatio', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('returnOnAssets', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('returnOnEquity', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('trailingPE', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('forwardPE', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('pegRatio', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('priceToSalesTrailing12Months', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('priceToBook', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('dividendYield', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('beta', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('marketCap', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('enterpriseValue', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('freeCashflow', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('revenueGrowth', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('operatingCashflow', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('ebitda', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('totalDebt', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('totalCash', 0) if fundamental_data['success'] else 0,
                fundamental_data['data'].get('sharesOutstanding', 0) if fundamental_data['success'] else 0
            )

            # Construir la consulta SQL con el número correcto de placeholders
            placeholders = ','.join(['?'] * len(values))
            query = f"INSERT OR REPLACE INTO analysis VALUES ({placeholders})"
            
            c.execute(query, values)
            conn.commit()
            conn.close()
            print(f"Análisis completo de {symbol} almacenado correctamente")
            return True
        except Exception as e:
            print(f"Error almacenando análisis para {symbol}: {str(e)}")
            return False

    @staticmethod
    def get_stock_analysis(symbol: str) -> Dict:
        """Método principal para obtener análisis de acciones"""
        try:
            symbol = symbol.upper()
            
            # Validar símbolo
            if symbol not in AnalysisService.TICKERS:
                return {"error": f"Símbolo {symbol} no soportado"}
            
            # Inicializar base de datos (solo una vez)
            try:
                AnalysisService._init_db()
            except Exception as e:
                print(f"Advertencia: No se pudo inicializar la base de datos: {str(e)}")
            
            # Obtener datos técnicos
            technical_result = AnalysisService.fetch_technical_data(symbol)
            if not technical_result['success']:
                return {"error": technical_result['error']}
            
            # Obtener datos fundamentales (sin reintentos)
            fundamental_result = AnalysisService.fetch_fundamental_data(symbol)
            
            # Calcular indicadores técnicos
            try:
                technical_indicators = AnalysisService.calculate_technical_indicators(technical_result['data'])
            except Exception as e:
                return {"error": f"Error calculando indicadores técnicos: {str(e)}"}
            
            # Clasificaciones
            short_term, short_score = AnalysisService._classify_short_term(technical_indicators['price'], technical_indicators)
            
            # Calcular score fundamental (puede ser None si no hay datos)
            fund_score = AnalysisService._calculate_fundamental_score(fundamental_result['data']) if fundamental_result['success'] else None
            
            # Clasificaciones con ponderación de datos fundamentales
            medium_term, medium_score = AnalysisService._classify_medium_term(technical_indicators['price'], technical_indicators, fund_score)
            long_term, long_score = AnalysisService._classify_long_term(technical_indicators['price'], technical_indicators, fund_score)
            
            # Almacenar en base de datos (en segundo plano)
            threading.Thread(
                target=AnalysisService._store_analysis,
                args=(symbol, technical_indicators, fundamental_result)
            ).start()
            
            # Construir respuesta
            response = {
                "symbol": symbol,
                "timestamp": datetime.datetime.now(pytz.UTC).isoformat(),
                "price_data": {
                    "price": technical_indicators['price'],
                    "open": technical_indicators['open'],
                    "high": technical_indicators['high'],
                    "low": technical_indicators['low'],
                    "volume": technical_indicators['volume']
                },
                "technical_indicators": {
                    "sma": {k: technical_indicators[k] for k in technical_indicators if k.startswith('sma_') and not k.endswith('_pct')},
                    "ema": {k: technical_indicators[k] for k in technical_indicators if k.startswith('ema_') and not k.endswith('_pct')},
                    "pivot_points": {
                        "pivot": technical_indicators['pivot'],
                        "r1": technical_indicators['r1'],
                        "r2": technical_indicators['r2'],
                        "s1": technical_indicators['s1'],
                        "s2": technical_indicators['s2']
                    },
                    "percentage_changes": {
                        "sma_pct": {k: technical_indicators[k] for k in technical_indicators if k.startswith('sma_') and k.endswith('_pct')},
                        "ema_pct": {k: technical_indicators[k] for k in technical_indicators if k.startswith('ema_') and k.endswith('_pct')},
                        "pivot_pct": technical_indicators['pivot_pct'],
                        "r1_pct": technical_indicators['r1_pct'],
                        "r2_pct": technical_indicators['r2_pct'],
                        "s1_pct": technical_indicators['s1_pct'],
                        "s2_pct": technical_indicators['s2_pct'],
                        "daily_changes": technical_indicators['pct_change']
                    }
                },
                "fundamental_analysis": {
                    "score": fund_score,
                    "debt_equity": fundamental_result['data'].get('debtToEquity', 0) if fundamental_result['success'] else None,
                    "pe_ratio": fundamental_result['data'].get('trailingPE', 0) if fundamental_result['success'] else None,
                    "roe": (fundamental_result['data'].get('returnOnEquity', 0) or 0) * 100 if fundamental_result['success'] else None,
                    "market_cap": fundamental_result['data'].get('marketCap', 0) if fundamental_result['success'] else None
                },
                "classifications": {
                    "short_term": {
                        "classification": short_term,
                        "score": short_score
                    },
                    "medium_term": {
                        "classification": medium_term,
                        "score": medium_score
                    },
                    "long_term": {
                        "classification": long_term,
                        "score": long_score
                    }
                }
            }
            
            return response
        except Exception as e:
            return {"error": f"Error procesando la solicitud: {str(e)}"}

    @staticmethod
    def scheduled_analysis():
        """Tarea programada para actualizar datos periódicamente"""
        while True:
            try:
                print(f"\nIniciando análisis automático a las {datetime.datetime.now(pytz.UTC)}")
                for symbol in AnalysisService.TICKERS:
                    try:
                        # Obtener datos
                        technical_result = AnalysisService.fetch_technical_data(symbol)
                        fundamental_result = AnalysisService.fetch_fundamental_data(symbol)
                        
                        if not technical_result['success']:
                            continue
                        
                        # Calcular indicadores
                        technical_indicators = AnalysisService.calculate_technical_indicators(technical_result['data'])
                        
                        # Almacenar en base de datos
                        AnalysisService._store_analysis(symbol, technical_indicators, fundamental_result)
                        
                        time.sleep(5)  # Pausa entre símbolos
                    except Exception as e:
                        print(f"Error procesando {symbol}: {str(e)}")
                        continue
                
                print(f"Análisis completado a las {datetime.datetime.now(pytz.UTC)}")
                time.sleep(4 * 3600)  # Esperar 4 horas
            except Exception as e:
                print(f"Error en el análisis programado: {str(e)}")
                time.sleep(60)