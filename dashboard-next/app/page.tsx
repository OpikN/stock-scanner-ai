"use client";

import { useEffect, useState } from "react";

export default function Home() {

  const [data, setData] = useState<any>(null);

  async function fetchData() {

    try {

      const res = await fetch(
        "https://raw.githubusercontent.com/OpikN/stock-scanner-ai/main/data/live_data.json"
      );

      const json = await res.json();

      setData(json);

    } catch (err) {

      console.log(err);

    }

  }

  useEffect(() => {

    fetchData();

    const interval = setInterval(() => {

      fetchData();

    }, 5000);

    return () => clearInterval(interval);

  }, []);

  return (

    <main className="min-h-screen bg-black text-white p-6">

      <h1 className="text-4xl font-bold mb-8">

        📊 OPIK AI TERMINAL

      </h1>

      {!data ? (

        <p>Loading...</p>

      ) : (

        <div className="space-y-6">

          <div className="grid grid-cols-3 gap-4">

            <div className="bg-zinc-900 p-4 rounded-2xl">

              <p className="text-zinc-400">

                Equity

              </p>

              <h2 className="text-3xl font-bold">

                {data.equity?.toLocaleString()}

              </h2>

            </div>

            <div className="bg-zinc-900 p-4 rounded-2xl">

              <p className="text-zinc-400">

                Floating PnL

              </p>

              <h2 className="text-3xl font-bold text-green-400">

                {data.floating_pnl?.toLocaleString()}

              </h2>

            </div>

            <div className="bg-zinc-900 p-4 rounded-2xl">

              <p className="text-zinc-400">

                Open Positions

              </p>

              <h2 className="text-3xl font-bold">

                {data.open_positions}

              </h2>

            </div>

          </div>

          <div className="bg-zinc-900 p-4 rounded-2xl">

            <h2 className="text-2xl font-bold mb-4">

              📡 Live Positions

            </h2>

            <div className="space-y-4">

              {data.positions?.map((p:any, i:number) => (

                <div
                  key={i}
                  className="border border-zinc-700 p-4 rounded-xl"
                >

                  <div className="flex justify-between">

                    <div>

                      <h3 className="text-xl font-bold">

                        {p.stock}

                      </h3>

                      <p>

                        {p.side}

                      </p>

                    </div>

                    <div className="text-right">

                      <p>

                        Entry: {p.entry}

                      </p>

                      <p>

                        Current: {p.current}

                      </p>

                      <p className="text-green-400">

                        PnL: {p.pnl}

                      </p>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          </div>

        </div>

      )}

    </main>

  );

}
