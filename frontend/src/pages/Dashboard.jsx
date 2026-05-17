import ServiceCard from '../components/ServiceCard'

const SERVICES = ['auth', 'products', 'orders', 'users', 'chat', 'payments']

const MONITORING_LINKS = [
  { label: 'Prometheus', href: 'http://localhost:9090', desc: 'Metrics collection · Port 9090' },
  { label: 'Grafana',    href: 'http://localhost:3000', desc: 'Dashboards · Port 3000' },
  { label: 'Alertmanager', href: 'http://localhost:9093', desc: 'Alerts · Port 9093' },
  { label: 'Loki',       href: 'http://localhost:3100', desc: 'Logs · Port 3100' },
]

export default function Dashboard() {
  return (
    <div className="space-y-10">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">SRE End Term · Microservices Monitoring · Auto-refresh every 10s</p>
      </div>

      {/* Service health grid */}
      <section>
        <p className="text-xs text-slate-500 uppercase tracking-widest mb-4">Service Health</p>
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {SERVICES.map(svc => (
            <ServiceCard key={svc} service={svc} />
          ))}
        </div>
      </section>

      {/* Quick stats */}
      <section>
        <p className="text-xs text-slate-500 uppercase tracking-widest mb-4">Quick Stats</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard value="6" label="Microservices" accent="sky" />
          <StatCard value="80"  label="Frontend Port" accent="violet" />
          <StatCard value="9090" label="Prometheus Port" accent="orange" />
          <StatCard value="3000" label="Grafana Port" accent="green" />
        </div>
      </section>

      {/* Monitoring links */}
      <section>
        <p className="text-xs text-slate-500 uppercase tracking-widest mb-4">Monitoring Tools</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {MONITORING_LINKS.map(({ label, href, desc }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noreferrer"
              className="bg-slate-900 border border-slate-700 rounded-xl p-4 text-center hover:border-sky-500 transition-colors group block"
            >
              <div className="text-sky-400 font-semibold text-sm group-hover:text-sky-300">{label}</div>
              <div className="text-slate-500 text-xs mt-1">{desc}</div>
            </a>
          ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({ value, label, accent }) {
  const colors = {
    sky: 'text-sky-400',
    violet: 'text-violet-400',
    orange: 'text-orange-400',
    green: 'text-green-400',
  }
  return (
    <div className="card text-center">
      <div className={`text-3xl font-bold ${colors[accent] ?? 'text-sky-400'}`}>{value}</div>
      <div className="text-slate-500 text-xs mt-1">{label}</div>
    </div>
  )
}
