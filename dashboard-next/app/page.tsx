"use client"

import {

  useEffect,

  useState

} from "react"

export default function Home() {

  const [data, setData] = useState<any>(null)

  async function loadData() {

    try {

      const res = await fetch(

        "/live_data.json?t=" + Date.now()

      )

      const json = await res.json()

      setData(json)

    } catch (err) {

      console.log(err)

    }

  }

  useEffect(() => {

    loadData()

    const interval = setInterval(

      loadData,

      5000

    )

    return () => clearInterval(interval)

  }, [])

  if (!data) {

    return (

      <main className="p-10 text-white bg-black h-screen">

        <h1 className="text-3xl">

          📊 OPIK AI TERMINAL

        </h1>

        <p className="mt-4">

          Loading...

        </p>

      </main>

    )

  }

  return (

    <main className="min-h-screen bg-black text-green-400 p-10">

      <h1 className="text-4xl font-bold mb-10">

        📊 OPIK AI TERMINAL

      </h1>

      <div className="grid grid-cols-3 gap-6 mb-10">

        <div className="border border-green-500 p-6 rounded-xl">

          <h2 className="text-xl mb-2">

            Equity

          </h2>

          <p className="text-3xl font-bold">

            {data.equity.toLocaleString()}

          </p>

        </div>

        <div className="border border-green-500 p-6 rounded-xl">

          <h2 className="text-xl mb-2">

            Floating PnL

          </h2>

          <p className="text-3xl font-bold">

            {data.floating_pnl.toLocaleString()}

          </p>

        </div>

        <div className="border border-green-500 p-6 rounded-xl">

          <h2 className="text-xl mb-2">

            Open Positions

          </h2>

          <p className="text-3xl font-bold">

            {data.open_positions.length}

          </p>

        </div>

      </div>

      <h2 className="text-2xl mb-6">

        📡 Live Positions

      </h2>

      <div className="space-y-4">

        {data.open_positions.map(

          (pos: any, idx: number) => (

            <div

              key={idx}

              className="border border-green-500 p-6 rounded-xl"

            >

              <h3 className="text-2xl font-bold">

                {pos.stock}

              </h3>

              <p>

                {pos.side}

              </p>

              <p>

                Entry: {pos.entry_price}

              </p>

              <p>

                Current: {pos.current_price}

              </p>

              <p>

                PnL: {pos.pnl}

              </p>

              <p>

                SL: {pos.sl}

              </p>

              <p>

                TP1: {pos.tp1}

              </p>

            </div>

          )

        )}

      </div>

    </main>

  )

}
