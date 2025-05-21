import yfinance as yf
from tabulate import tabulate
from datetime import datetime

class NSEMarketAgent:
    def __init__(self):
        self.nse_suffix = ".NS"

    def _add_ns_suffix(self, symbol):
        if ".NS" not in symbol:
            return symbol + ".NS"
        return symbol

    def get_stock_info(self, symbol):
        symbol = self._add_ns_suffix(symbol)
        return yf.Ticker(symbol).info

    def evaluate_fundamentals(self, symbol):
        symbol = self._add_ns_suffix(symbol)
        try:
            info = yf.Ticker(symbol).info
            checks = []

            def check_metric(name, condition, value, formatter=lambda x: x):
                result = condition(value)
                checks.append({
                    "Metric": name,
                    "Value": formatter(value),
                    "Status": "GREEN" if result else "RED"
                })
                return result

            pe = info.get("trailingPE", None)
            ind_pe = info.get("forwardPE", None)
            roe = info.get("returnOnEquity", 0) * 100
            roic = info.get("returnOnAssets", 0) * 100
            roce = info.get("returnOnCapitalEmployed", None)
            opm = info.get("operatingMargins", 0) * 100
            sales_3y = info.get("revenueGrowth", 0) * 100
            market_cap = info.get("marketCap", 0)
            revenue = info.get("totalRevenue", 1)
            promoter = info.get("heldPercentInsiders", 0) * 100
            interest_cover = info.get("interestCoverage", 0)
            peg = info.get("pegRatio", None)
            free_cash_flow = info.get("freeCashflow", None)
            debt_equity = info.get("debtToEquity", 0)
            cash_flow_ops = info.get("operatingCashflow", 1)

            check_metric("P/E < Industry P/E", lambda x: x < ind_pe if ind_pe else False, pe)
            check_metric("P/E < 20", lambda x: x < 20, pe)
            check_metric("ROE > 15%", lambda x: x > 15, roe)
            check_metric("ROIC > 15%", lambda x: x > 15, roic)
            check_metric("ROCE > 15%", lambda x: x and x > 15, roce)
            check_metric("OPM < 20%", lambda x: x < 20, opm)
            check_metric("3Y Sales Growth > 15%", lambda x: x > 15, sales_3y)
            check_metric("Market Cap / Sales > 3", lambda x: x > 3, market_cap / revenue)
            check_metric("Promoter Holding > 50%", lambda x: x > 50, promoter)
            check_metric("Interest Coverage > 5", lambda x: x > 5, interest_cover)
            check_metric("PEG < 1", lambda x: x and x < 1, peg)
            check_metric("Positive Free Cash Flow", lambda x: x and x > 0, free_cash_flow)
            check_metric("D/E < 1", lambda x: x < 1, debt_equity)
            check_metric("Price to Cash Flow Low", lambda x: x < 20, market_cap / cash_flow_ops)

            satisfied = sum([1 for c in checks if c['Status'] == 'GREEN'])
            total = len(checks)
            percent = int((satisfied / total) * 100)
            bar = '[' + '=' * (percent // 10) + ' ' * (10 - percent // 10) + f'] {percent}%'

            return {
                "symbol": symbol,
                "parameters": checks,
                "satisfied": satisfied,
                "total": total,
                "recommendation_percentage": percent,
                "recommendation_bar": bar
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

if __name__ == "__main__":
    agent = NSEMarketAgent()
    symbol = input("Enter NSE stock symbol (e.g., TCS): ")
    result = agent.evaluate_fundamentals(symbol)

    if "error" in result:
        print(f"Error evaluating {symbol}: {result['error']}")
    else:
        print("\nParameter Evaluation:")
        print(tabulate(result["parameters"], headers="keys"))
        print("\nRecommendation:")
        print(result["recommendation_bar"])
