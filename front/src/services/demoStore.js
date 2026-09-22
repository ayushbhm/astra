const STORAGE_KEY = 'jyotish-register-demo-charts'

const seedCharts = [
  {
    id: 1,
    title: 'Career change during Saturn period',
    dob: '1992-08-14', tob: '08:42', gender: 'Female', place: 'Pune', state: 'Maharashtra',
    story: 'A move from engineering into counselling followed a long period of professional uncertainty. The documented timeline is retained as a study prompt.',
    tags: ['Career Pivot', 'Rahu Dasha'], status: 'APPROVED', verification_status: 'VERIFIED', created_by: 2
  },
  {
    id: 2,
    title: 'Overseas relocation and study',
    dob: '1988-01-23', tob: '18:10', gender: 'Male', place: 'Kochi', state: 'Kerala',
    story: 'A postgraduate move abroad and later return to India are recorded as key events for comparative chart study.',
    tags: ['Foreign Travel', 'Education'], status: 'APPROVED', verification_status: 'UNVERIFIED', created_by: 3
  },
  {
    id: 3,
    title: 'Family business succession',
    dob: '1996-11-05', tob: '06:25', gender: 'Other', place: 'Jaipur', state: 'Rajasthan',
    story: 'Submitted for review with a business transition timeline and supporting notes.',
    tags: ['Business'], status: 'PENDING', verification_status: 'UNVERIFIED', created_by: 2
  }
]

function read() {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored ? JSON.parse(stored) : seedCharts
}

function write(charts) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(charts))
  return charts
}

export const demoStore = {
  all: () => read(),
  mine: (userId = 2) => read().filter(chart => chart.created_by === userId),
  create(data, userId = 2, isAdmin = false) {
    const charts = read()
    const chart = {
      ...data,
      id: Math.max(0, ...charts.map(item => item.id)) + 1,
      created_by: userId,
      status: isAdmin ? (data.status || 'APPROVED') : 'PENDING',
      verification_status: data.verification_status || 'UNVERIFIED'
    }
    write([...charts, chart])
    return chart
  },
  update(id, data) {
    const charts = read().map(chart => chart.id === Number(id) ? { ...chart, ...data } : chart)
    write(charts)
    return charts.find(chart => chart.id === Number(id))
  },
  remove(id) { write(read().filter(chart => chart.id !== Number(id))) },
  setStatus(id, status) { return this.update(id, { status }) },
  toggleVerification(id) {
    const chart = read().find(item => item.id === Number(id))
    return this.update(id, { verification_status: chart.verification_status === 'VERIFIED' ? 'UNVERIFIED' : 'VERIFIED' })
  }
}
