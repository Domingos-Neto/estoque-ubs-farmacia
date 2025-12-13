document.addEventListener('DOMContentLoaded', () => {
    // --- Config ---
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('entData').value = today;
    document.getElementById('saiData').value = today;
    
    let chartInstance = null;

    // --- Init ---
    refreshAll();

    // --- Core Functions ---
    function refreshAll() {
        loadStats(); // Carrega Cards e Gráfico
        loadEstoque();
        loadHistory();
        loadUsers(); // Se admin
    }

    // 1. Stats & Chart
    async function loadStats() {
        try {
            const res = await fetch('/api/dashboard/stats');
            const data = await res.json();
            
            // Cards
            document.getElementById('statTotal').innerText = data.total_itens;
            document.getElementById('statAlert').innerText = data.alertas;
            document.getElementById('statMov').innerText = data.mov_hoje;
            
            // Chart
            const ctx = document.getElementById('stockChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();
            
            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.chart.labels,
                    datasets: [
                        { label: 'Entrada', data: data.chart.entrada, backgroundColor: '#3b82f6' },
                        { label: 'Saída', data: data.chart.saida, backgroundColor: '#ef4444' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
            });
        } catch(e) { console.error("Stats error", e); }
    }

    // 2. Estoque Table
    async function loadEstoque() {
        const res = await fetch('/api/estoque');
        const data = await res.json();
        const tbody = document.getElementById('tblEstoque');
        
        const term = document.getElementById('searchBox').value.toLowerCase();
        
        tbody.innerHTML = data
            .filter(r => r.descricao.toLowerCase().includes(term) || r.cod.toLowerCase().includes(term))
            .map(r => `
            <tr class="${r.alerta_baixo ? 'table-danger' : ''}">
                <td class="fw-bold">${r.cod}</td>
                <td>${r.descricao}</td>
                <td>${r.unid}</td>
                <td class="text-end text-muted small">${r.estoque_minimo}</td>
                <td class="text-end fw-bold">${r.saldo}</td>
                <td>${r.alerta_baixo ? '<span class="badge bg-danger">BAIXO</span>' : '<span class="badge bg-success">OK</span>'}</td>
                <td><button class="btn btn-sm btn-outline-danger py-0" onclick="alert('Funcionalidade de exclusão mantida no backend, adicione se desejar')"><i class="bi bi-trash"></i></button></td>
            </tr>
        `).join('');
    }
    
    document.getElementById('searchBox').addEventListener('keyup', loadEstoque);

    // 3. Forms (Sem Nota Fiscal)
    setupForm('formEntrada', '/api/entrada', {
        cod: 'entCod', qtd: 'entQtd', data: 'entData'
    });
    setupForm('formSaida', '/api/saida', {
        cod: 'saiCod', qtd: 'saiQtd', data: 'saiData'
    });
    setupForm('formItem', '/api/itens', {
        cod: 'newCod', descricao: 'newDesc', unid: 'newUnid', estoque_minimo: 'newMin'
    }, true); // true = fecha modal

    function setupForm(formId, url, map, isModal=false) {
        document.getElementById(formId).onsubmit = async (e) => {
            e.preventDefault();
            const body = {};
            for (let key in map) body[key] = document.getElementById(map[key]).value;
            
            const res = await fetch(url, {
                method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)
            });
            
            if (res.ok) {
                toast('Sucesso!', 'success');
                e.target.reset();
                if(isModal) bootstrap.Modal.getInstance(document.getElementById('modalItem')).hide();
                refreshAll();
            } else {
                const err = await res.json();
                toast(err.error || 'Erro', 'danger');
            }
        };
    }

    // 4. History
    async function loadHistory() {
        const res = await fetch('/api/movimentacoes');
        const data = await res.json();
        
        const render = (rows, isEnt) => rows.map(r => `
            <tr>
                <td>${r.data.split('-').reverse().slice(0,2).join('/')}</td>
                <td>${r.cod}</td>
                <td class="${isEnt?'text-primary':'text-danger'} fw-bold">${r.quantidade}</td>
            </tr>
        `).join('');
        
        document.getElementById('tblHistEnt').innerHTML = render(data.entradas, true);
        document.getElementById('tblHistSai').innerHTML = render(data.saidas, false);
    }

    // 5. Users (Admin)
    async function loadUsers() {
        const el = document.getElementById('tblUsers');
        if (!el) return; // Não é admin
        
        const res = await fetch('/api/users');
        if (!res.ok) return;
        const users = await res.json();
        
        el.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.username}</td>
                <td>${u.is_admin ? 'SIM' : '-'}</td>
                <td>${u.username === 'admin' ? '' : `<button class="btn btn-sm btn-danger py-0" onclick="delUser(${u.id})">X</button>`}</td>
            </tr>
        `).join('');
    }
    
    // User Form
    const userForm = document.getElementById('formUser');
    if (userForm) {
        userForm.onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch('/api/users', {
                method: 'POST', headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('uUser').value,
                    password: document.getElementById('uPass').value,
                    is_admin: document.getElementById('uAdmin').checked
                })
            });
            if(res.ok) { userForm.reset(); loadUsers(); toast('Usuário criado'); }
        };
    }
    
    window.delUser = async (id) => {
        if(!confirm('Excluir?')) return;
        await fetch(`/api/users/${id}`, {method:'DELETE'});
        loadUsers();
    };

    function toast(msg, type='primary') {
        const area = document.getElementById('toastArea');
        const div = document.createElement('div');
        div.className = `toast align-items-center text-white bg-${type} border-0 show`;
        div.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
        area.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    }
});