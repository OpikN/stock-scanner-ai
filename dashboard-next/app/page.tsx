"use client";

import { useEffect, useState } from "react";

const demoStocks = [
  {
    stock: "BBRI.JK",
    signal: "BUY",
    price: 5260,
    change: "+2.31%",
    confidence: "92%",
  },
  {
    stock: "BBCA.JK",
    signal: "WAIT",
    price: 9850,
    change: "+0.42%",
    confidence: "71%",
  },
  {
    stock: "TLKM.JK",
    signal: "SELL",
    price: 3120,
    change: "-1.20%",
    confidence: "88%",
  },
  {
    stock: "ASII.JK",
    signal: "BUY",
    price: 4880,
    change: "+3.11%",
    confidence: "95%",
  },
  {
    stock: "GOTO.JK",
    signal: "BUY",
    price: 89,
    change: "+5.20%",
    confidence: "84%",
  },
];

export default function Page() {
  const [time, setTime] = useState("");
  const [equity, setEquity] = useState(100021000);
  const [floating, setFloating] = useState(21000);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString());

      setEquity((prev) => prev + Math.floor(Math.random() * 5000));

      setFloating((prev) => {
        const random = Math.floor(Math.random() * 10000) - 5000;
        return prev + random;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white p-4 overflow-hidden">
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex items-center justify-between border border-zinc-800 rounded-2xl p-4 bg-zinc-950">
          <div>
            <h1 className="text-xl md:text-3xl font-bold tracking-wide">
              OPIK AI TERMINAL
            </h1>
            <p className="text-zinc-400 text-xs md:text-sm">
              AI Stock Scanner Realtime Dashboard
            </p>
          </div>

          <div className="text-right">
            <p className="text-green-400 text-sm md:text-lg font-semibold">
              LIVE
            </p>
            <p className="text-zinc-400 text-xs">{time}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card title="Equity" value={equity.toLocaleString()} />
          <Card title="Floating PnL" value={floating.toLocaleString()} />
          <Card title="Open Signals" value="24" />
          <Card title="AI Accuracy" value="91%" />
        </div>

        <div className="border border-zinc-800 rounded-2xl bg-zinc-950 overflow-hidden">
          <div className="p-3 border-b border-zinc-800 flex items-center justify-between">
            <h2 className="text-sm md:text-lg font-semibold">
              LIVE MARKET SIGNALS
            </h2>

            <div className="text-xs text-zinc-400">
              Auto Refresh Enabled
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs md:text-sm">
              <thead className="bg-zinc-900 text-zinc-400">
                <tr>
                  <th className="text-left p-3">Stock</th>
                  <th className="text-left p-3">Signal</th>
                  <th className="text-left p-3">Price</th>
                  <th className="text-left p-3">Change</th>
                  <th className="text-left p-3">AI Confidence</th>
                  <th className="text-left p-3">Mini Chart</th>
                </tr>
              </thead>

              <tbody>
                {demoStocks.map((s, i) => (
                  <tr
                    key={i}
                    className="border-t border-zinc-800 hover:bg-zinc-900/50 transition"
                  >
                    <td className="p-3 font-semibold">{s.stock}</td>

                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded-full text-[10px] md:text-xs font-bold ${
                          s.signal === "BUY"
                            ? "bg-green-500/20 text-green-400"
                            : s.signal === "SELL"
                            ? "bg-red-500/20 text-red-400"
                            : "bg-yellow-500/20 text-yellow-300"
                        }`}
                      >
                        {s.signal}
                      </span>
                    </td>

                    <td className="p-3">{s.price}</td>

                    <td
                      className={`p-3 font-semibold ${
                        s.change.includes("+")
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      {s.change}
                    </td>

                    <td className="p-3 text-cyan-400">{s.confidence}</td>

                    <td className="p-3">
                      <div className="w-24 h-8 bg-zinc-800 rounded-lg overflow-hidden relative">
                        <div className="absolute inset-0 flex items-end gap-[2px] p-1">
                          {[4, 8, 5, 10, 6, 12, 7, 14].map((h, idx) => (
                            <div
                              key={idx}
                              className="bg-green-400 w-1 rounded-sm"
                              style={{ height: `${h * 2}px` }}
                            />
                          ))}
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="border border-zinc-800 rounded-2xl bg-zinc-950 overflow-hidden">
          <div className="whitespace-nowrap animate-marquee p-3 text-xs md:text-sm text-green-400">
            🚀 BBRI BUY +2.31% &nbsp;&nbsp;&nbsp; 🚀 ASII BUY +3.11% &nbsp;&nbsp;&nbsp; ⚠️ TLKM SELL -1.20% &nbsp;&nbsp;&nbsp; 📈 GOTO BREAKOUT +5.20%
          </div>
        </div>
      </div>
    </main>
  );
}

function Card({ title, value }: any) {
  return (
    <div className="border border-zinc-800 rounded-2xl bg-zinc-950 p-4">
      <p className="text-zinc-400 text-[10px] md:text-xs uppercase tracking-wide">
        {title}
      </p>

      <h2 className="text-lg md:text-2xl font-bold mt-2 break-all">
        {value}
      </h2>
    </div>
  );
}