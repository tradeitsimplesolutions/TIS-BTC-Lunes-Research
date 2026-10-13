//+------------------------------------------------------------------+
//| TIS_BTC_Lunes_v3.mq5 — BTC · Efecto Lunes v3 (Trade It Simple)   |
//| Robot para MetaTrader 5 sobre el CFD de Bitcoin (BTCUSD), velas H1 |
//|                                                                    |
//| Regla (en hora UTC; el EA convierte la hora del servidor):         |
//|  · Vela de señal: la H1 que cierra a las 00:00 UTC del lunes       |
//|    (la de las 23:00 del domingo).                                  |
//|  · Filtro de volatilidad: ATR(48)/precio en % por encima del       |
//|    percentil 30 de las últimas 8.760 velas (un año).               |
//|  · Calendario: no se opera el primer lunes del mes (día 1 a 7).    |
//|  · Entrada: compra a mercado al abrir la vela de las 00:00 UTC.    |
//|  · Salida: cierre a mercado al abrir la vela de las 00:00 UTC del  |
//|    martes (24 velas). Sin stop, sin take profit.                   |
//|  · Tamaño: FraccionCapital del equity (40 %), sin apalancar.       |
//| Versión 1.1 · 2026-10-12 · paridad con el motor de Python:         |
//|  ATR de Wilder, percentil como pandas, horario con cambio de       |
//|  verano, llenado según el símbolo, sin forzar el lote mínimo,      |
//|  salida por tiempo. Reconciliado con el Strategy Tester (Exness,   |
//|  BTCUSDz, 2021-2026): resultados/reconciliacion_mt5.json.          |
//+------------------------------------------------------------------+
#property copyright "Trade It Simple"
#property version   "1.10"
#include <Trade/Trade.mqh>

// horario del servidor: con cambio de verano automático o fijo
enum ENUM_HORARIO
{
   HORARIO_GMT2_GMT3_DST_US = 0,   // GMT+2 invierno / GMT+3 verano EE. UU. (Axi, IC Markets, Pepperstone...)
   HORARIO_FIJO             = 1    // Desfase fijo (Exness = 0)
};

input ENUM_HORARIO ModoHorario      = HORARIO_GMT2_GMT3_DST_US; // horario del servidor del bróker
input int    OffsetFijoUTC          = 0;      // solo con "Desfase fijo": horas que el servidor va por delante de UTC
input int    ATR_Periodo            = 48;     // ATR en velas H1 (Wilder, como el motor)
input int    VentanaPercentil       = 8760;   // velas H1 para el percentil (un año)
input int    MinVelasPercentil      = 500;    // velas mínimas para el percentil (min_periods del motor)
input double PercentilMinimo        = 30.0;   // permiso si el ATR% está por encima de este percentil
input bool   SaltarPrimerLunes      = true;   // no operar el primer lunes del mes (día 1 a 7)
input int    HorasEnPosicion        = 24;     // salida por tiempo: 24 h después de la vela de entrada
input double FraccionCapital        = 0.40;   // fracción del equity por operación (0,40 = 40 %)
input long   Magic                  = 290301;

CTrade   trade;
datetime ultimaVela = 0;

//+------------------------------------------------------------------+
//| Horario: servidor → UTC                                          |
//+------------------------------------------------------------------+
// n-ésimo domingo de un mes (00:00 UTC de ese día)
datetime NesimoDomingo(int anio, int mes, int n)
{
   MqlDateTime d; ZeroMemory(d);
   d.year = anio; d.mon = mes; d.day = 1;
   datetime primero = StructToTime(d);
   MqlDateTime f; TimeToStruct(primero, f);
   int sumar = (7 - f.day_of_week) % 7;                         // días hasta el primer domingo
   return primero + (sumar + 7 * (n - 1)) * 86400;
}

// horario de verano de EE. UU.: del 2.º domingo de marzo (07:00 UTC) al 1.er domingo de noviembre (06:00 UTC)
bool VeranoUS(datetime utc)
{
   MqlDateTime u; TimeToStruct(utc, u);
   datetime ini = NesimoDomingo(u.year, 3, 2)  + 7 * 3600;
   datetime fin = NesimoDomingo(u.year, 11, 1) + 6 * 3600;
   return (utc >= ini && utc < fin);
}

// horas que el servidor va por delante de UTC en ese momento
int OffsetHoras(datetime servidor)
{
   if(ModoHorario == HORARIO_FIJO) return OffsetFijoUTC;
   return VeranoUS(servidor - 2 * 3600) ? 3 : 2;
}

datetime UTC(datetime servidor) { return servidor - OffsetHoras(servidor) * 3600; }

//+------------------------------------------------------------------+
int OnInit()
{
   if(PeriodSeconds(_Period) != 3600) { Print("Este EA debe correr en gráfico H1"); return INIT_FAILED; }
   trade.SetExpertMagicNumber(Magic);
   trade.SetTypeFillingBySymbol(_Symbol);                         // modo de llenado que acepta el bróker
   trade.SetDeviationInPoints(1000);

   // en cuenta real/demo, comprueba que el horario configurado coincide con el del servidor
   if(!MQLInfoInteger(MQL_TESTER))
   {
      int real = (int)MathRound((double)(TimeTradeServer() - TimeGMT()) / 3600.0);
      int conf = OffsetHoras(TimeTradeServer());
      if(real != conf)
         Alert(StringFormat("TIS Lunes v3: el servidor va a UTC%+d pero el EA está configurado a UTC%+d. Revisa ModoHorario / OffsetFijoUTC.", real, conf));
      else
         PrintFormat("TIS Lunes v3: horario OK (servidor = UTC%+d)", real);
   }
   return INIT_SUCCEEDED;
}

// devuelve también la hora de apertura de la posición (para la salida por tiempo)
bool HayPosicion(datetime &abierta)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(PositionSelectByTicket(t) && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic)
      {
         abierta = (datetime)PositionGetInteger(POSITION_TIME);
         return true;
      }
   }
   return false;
}

void CerrarPosicion()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(PositionSelectByTicket(t) && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic)
         if(!trade.PositionClose(t)) Print("Error al cerrar: ", trade.ResultRetcodeDescription());
   }
}

// ATR% de Wilder de la última vela cerrada y su percentil, igual que el motor:
//   ATR  = RMA(TR, 48) sembrada con el primer TR   (pandas ewm(alpha=1/48, adjust=False))
//   pct  = rolling(8760, min_periods=500).rank(pct=True) → incluye la vela actual y promedia los empates
bool Permiso(double &atrPct, double &percentil)
{
   atrPct = 0; percentil = -1;
   int pedir = VentanaPercentil + 1000;                           // 1.000 velas extra para que la RMA converja
   MqlRates r[];
   ArraySetAsSeries(r, false);                                    // r[0] = la más antigua
   int got = CopyRates(_Symbol, PERIOD_H1, 1, pedir, r);          // desde la última vela CERRADA hacia atrás
   if(got < ATR_Periodo + MinVelasPercentil) return false;

   double ap[]; ArrayResize(ap, got);
   double rma = 0;
   for(int i = 0; i < got; i++)
   {
      double tr = r[i].high - r[i].low;
      if(i > 0) tr = MathMax(tr, MathMax(MathAbs(r[i].high - r[i-1].close), MathAbs(r[i].low - r[i-1].close)));
      rma = (i == 0) ? tr : rma + (tr - rma) / ATR_Periodo;
      ap[i] = (i >= ATR_Periodo - 1) ? rma / r[i].close * 100.0 : -1.0;
   }
   atrPct = ap[got - 1];

   int desde = MathMax(ATR_Periodo - 1, got - VentanaPercentil);
   int n = 0, menores = 0, iguales = 0;
   for(int i = desde; i < got; i++)
   {
      n++;
      if(ap[i] < atrPct) menores++;
      else if(ap[i] == atrPct) iguales++;                         // incluye la propia vela
   }
   if(n < MinVelasPercentil) return false;
   percentil = 100.0 * (menores + (iguales + 1) / 2.0) / n;
   return percentil >= PercentilMinimo;
}

// si el 40 % no llega al lote mínimo, NO opera (antes compraba el mínimo y podía apalancar)
double Lotes()
{
   double equity   = AccountInfoDouble(ACCOUNT_EQUITY);
   double precio   = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double contrato = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   double paso     = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minimo   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maximo   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(precio <= 0 || contrato <= 0 || paso <= 0) return 0;
   double lotes = MathFloor(equity * FraccionCapital / (precio * contrato) / paso) * paso;
   int    digs  = (int)MathMax(0, MathCeil(-MathLog10(paso)));
   lotes = NormalizeDouble(MathMin(lotes, maximo), digs);
   if(lotes < minimo)
   {
      PrintFormat("Sin operar: el %.0f %% del equity (%.2f) no llega al lote mínimo %.4f", FraccionCapital * 100, equity * FraccionCapital, minimo);
      return 0;
   }
   return lotes;
}

void OnTick()
{
   datetime apertura = iTime(_Symbol, PERIOD_H1, 0);
   if(apertura == 0 || apertura == ultimaVela) return;            // una decisión por vela, en su apertura
   ultimaVela = apertura;

   // salida por tiempo: al abrir la vela que está HorasEnPosicion después de la vela de entrada
   //          (= martes 00:00 UTC; si falta esa vela, cierra en la siguiente en vez de esperar una semana)
   datetime abierta = 0;
   if(HayPosicion(abierta))
   {
      datetime velaEntrada = (datetime)((long)abierta - (long)abierta % 3600);
      if(apertura >= velaEntrada + HorasEnPosicion * 3600) { CerrarPosicion(); Print("CLOSE martes 00:00 UTC"); }
      return;
   }

   MqlDateTime t; TimeToStruct(UTC(apertura), t);                 // hora UTC de la vela que acaba de abrir
   bool lunes00 = (t.day_of_week == 1 && t.hour == 0);
   if(!lunes00) return;

   if(SaltarPrimerLunes && t.day <= 7) { Print("Sin operar: primer lunes del mes"); return; }
   double atrPct = 0, pct = -1;
   if(!Permiso(atrPct, pct))
   {
      if(pct < 0) Print("Sin permiso: no hay historia suficiente para el percentil");
      else PrintFormat("Sin permiso: ATR%% %.3f = percentil %.1f (< %.0f)", atrPct, pct, PercentilMinimo);
      return;
   }
   double lotes = Lotes();
   if(lotes <= 0) return;
   if(trade.Buy(lotes, _Symbol, 0, 0, 0, "LONG lunes v3"))
      PrintFormat("LONG lunes 00:00 UTC · %.4f lotes · ATR%% %.3f = percentil %.1f", lotes, atrPct, pct);
   else
      Print("Error al comprar: ", trade.ResultRetcodeDescription());
}
//+------------------------------------------------------------------+
