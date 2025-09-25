import React, { useEffect, useState } from 'react'

const api = {
  base: import.meta.env.VITE_API_BASE || '/api'
}

export default function App() {
  const [users, setUsers] = useState([])
  const [tasks, setTasks] = useState([])
  const [username, setUsername] = useState('')
  const [title, setTitle] = useState('')
  const [selectedUser, setSelectedUser] = useState('')

  const load = async () => {
    const [uRes, tRes] = await Promise.all([
      fetch(`${api.base}/users`),
      fetch(`${api.base}/tasks`)
    ])
    setUsers(await uRes.json())
    setTasks(await tRes.json())
  }

  useEffect(() => { load() }, [])

  const createUser = async (e) => {
    e.preventDefault()
    if (!username.trim()) return
    await fetch(`${api.base}/users`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ username }) })
    setUsername('')
    load()
  }

  const createTask = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    const payload = { title }
    if (selectedUser) payload.user_id = Number(selectedUser)
    await fetch(`${api.base}/tasks`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    setTitle('')
    load()
  }

  const toggleTask = async (id, completed) => {
    await fetch(`${api.base}/tasks/${id}`, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ completed: !completed }) })
    load()
  }

  const removeTask = async (id) => {
    await fetch(`${api.base}/tasks/${id}`, { method:'DELETE' })
    load()
  }

  return (
    <div style={{fontFamily:'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif', color:'#eaf0f1', background:'#0b0c10', minHeight:'100vh'}}>
      <nav style={{display:'flex', gap:12, alignItems:'center', padding:'12px 16px', background:'#0f1116', borderBottom:'1px solid #1b1f2a'}}>
        <strong>Microservices UI</strong>
        <div style={{flex:1}} />
        <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer">Flask</a>
        <a href="https://react.dev/" target="_blank" rel="noreferrer">React</a>
      </nav>
      <main style={{maxWidth:980, margin:'24px auto', padding:'0 16px'}}>
        <section style={{display:'grid', gap:16, gridTemplateColumns:'1fr 1fr'}}>
          <div style={{background:'#121317', border:'1px solid #1b1f2a', borderRadius:12, padding:16}}>
            <h2>Users</h2>
            <form onSubmit={createUser} style={{display:'flex', gap:8, marginBottom:12}}>
              <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="Username" style={{flex:1, background:'#0d0f14', color:'#eaf0f1', border:'1px solid #1b1f2a', borderRadius:8, padding:'8px 10px'}} />
              <button style={{background:'#1e2637', color:'#eaf0f1', border:'1px solid #2a3550', borderRadius:8, padding:'8px 12px'}}>Add</button>
            </form>
            <ul style={{margin:0, paddingLeft:16}}>
              {users.map(u => <li key={u.id}>@{u.username} <span style={{color:'#828b93'}}>#{u.id}</span></li>)}
            </ul>
          </div>

          <div style={{background:'#121317', border:'1px solid #1b1f2a', borderRadius:12, padding:16}}>
            <h2>Tasks</h2>
            <form onSubmit={createTask} style={{display:'flex', gap:8, marginBottom:12}}>
              <input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Task title" style={{flex:1, background:'#0d0f14', color:'#eaf0f1', border:'1px solid #1b1f2a', borderRadius:8, padding:'8px 10px'}} />
              <select value={selectedUser} onChange={e=>setSelectedUser(e.target.value)} style={{background:'#0d0f14', color:'#eaf0f1', border:'1px solid #1b1f2a', borderRadius:8, padding:'8px 10px'}}>
                <option value="">Unassigned</option>
                {users.map(u => <option key={u.id} value={u.id}>@{u.username}</option>)}
              </select>
              <button style={{background:'#1e2637', color:'#eaf0f1', border:'1px solid #2a3550', borderRadius:8, padding:'8px 12px'}}>Add</button>
            </form>
            <ul style={{listStyle:'none', padding:0, margin:0, display:'grid', gap:8}}>
              {tasks.map(t => (
                <li key={t.id} style={{display:'grid', gridTemplateColumns:'auto 1fr auto', gap:8, alignItems:'center', background:'#0f1116', border:'1px solid #1b1f2a', borderRadius:8, padding:'8px 10px'}}>
                  <button onClick={()=>toggleTask(t.id, t.completed)} style={{width:24, height:24, borderRadius:6, background:t.completed?'#1f2a27':'#121317', color:'#eaf0f1', border:'1px solid #2a3550'}}>{t.completed ? '✓' : ''}</button>
                  <div>
                    <div style={{textDecoration: t.completed ? 'line-through' : 'none'}}>{t.title}</div>
                    <div style={{color:'#828b93', fontSize:13}}>{t.user_id ? `Assigned to #${t.user_id}` : 'Unassigned'}</div>
                  </div>
                  <button onClick={()=>removeTask(t.id)} style={{background:'#3b2226', border:'1px solid #5c2b33', color:'#eaf0f1', borderRadius:6, padding:'6px 10px'}}>Delete</button>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </div>
  )
}