export default function Help() {
  return (
    <div className="max-w-3xl prose prose-invert">
      <h1 className="text-2xl font-bold mb-4 text-zinc-100">Help</h1>
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 text-sm text-zinc-300 space-y-4">
        <section>
          <h2 className="text-lg font-semibold text-amber-300">Workflow</h2>
          <ol className="list-decimal list-inside space-y-1 text-zinc-400">
            <li>scope_device(operation=&quot;connect&quot;, device_id=&quot;sim-001&quot;)</li>
            <li>scope_capture(operation=&quot;single&quot;)</li>
            <li>scope_measure(operation=&quot;all&quot;)</li>
          </ol>
        </section>
        <section>
          <h2 className="text-lg font-semibold text-amber-300">Hardware</h2>
          <p className="text-zinc-400">
            Recommended: PicoScope 2204A (picoscope backend) or Hantek 6022BE (hantek backend).
            See docs/HARDWARE.md in the repo.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold text-amber-300">USBXI note</h2>
          <p className="text-zinc-400">
            USBXI is Hantek&apos;s proprietary modular docking port for chaining scope/logic/PSU modules.
            It is not USBTMC or SCPI. Budget 6022BE units use standard USB + libusb, not the USBXI chassis system.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold text-amber-300">Safety</h2>
          <p className="text-zinc-400">Never probe mains. Budget USB scopes are typically 35-50 V max input.</p>
        </section>
      </div>
    </div>
  );
}
