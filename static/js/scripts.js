document.addEventListener('DOMContentLoaded', () => {
    initAllModules();
});

const U = {
    isMob: () => /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent),
    cap: s => s.toLowerCase().replace(/\b\w/g, c => c.toUpperCase()),
    fmtPh: v => { v = v.replace(/\D/g,''); return v ? v.match(/(\d{0,3})(\d{0,3})(\d{0,4})/).slice(1).filter(Boolean).join('-') : ''; },
    alert: (m,t='info') => { const a=document.createElement('div'); a.className=`alert alert-${t}`; a.innerHTML=`${m}<button class="btn-close" onclick="this.parentElement.remove()"></button>`; a.style.cssText='position:fixed;top:20px;right:20px;z-index:9999;max-width:300px;'; document.body.appendChild(a); setTimeout(()=>a.remove(),5000); },
    conf: m => confirm(m),
    anim: (el,a='fadeIn') => { el.style.animation=`${a} 0.5s ease`; setTimeout(()=>el.style.animation='',500); }
};

const Main = {
    init() { this.animFade(); this.delConfirm(); this.passToggle(); },
    animFade() { document.querySelectorAll('.fade-in').forEach((e,i)=>{ e.style.opacity='0'; setTimeout(()=>{ e.style.transition='opacity 0.6s'; e.style.opacity='1'; },100*i); }); },
    delConfirm() { document.querySelectorAll('.btn-delete,.delete-btn').forEach(b=>b.addEventListener('click',e=>{ if(!U.conf(b.dataset.name?'Сигурни ли сте да изтриете "'+b.dataset.name+'"?':'Сигурни ли сте?')) e.preventDefault(); })); },
    passToggle() { document.querySelector('.toggle-password')?.addEventListener('click',function(){ const i=document.querySelector('#id_password'); i.type=i.type==='password'?'text':'password'; this.classList.toggle('fa-eye-slash'); }); }
};

const Cat = {
    init() { document.getElementById('sortSelect')?.addEventListener('change',function(){ const p=new URLSearchParams(window.location.search); p.set(this.value.substring(1).split('=')[0],this.value.substring(1).split('=')[1]); window.location.href=window.location.pathname+'?'+p; }); this.animCards(); },
    animCards() { document.querySelectorAll('.category-card').forEach((c,i)=>{ setTimeout(()=>c.style.cssText='transition:all 0.5s;opacity:1;transform:translateY(0)',100*i); }); }
};

class OrderForm {
    constructor() { this.f=document.querySelector('#orderForm'); if(this.f) this.init(); }
    init() { this.fieldEnhance(); this.validation(); this.formSubmit(); }
    fieldEnhance() {
        document.querySelector('input:not([type="hidden"])')?.focus();
        this.f.querySelectorAll('input[name*="name"]').forEach(f=>f.addEventListener('blur',()=>f.value&&(f.value=U.cap(f.value))));
        this.f.querySelector('input[name*="phone"]')?.addEventListener('input',e=>e.target.value=U.fmtPh(e.target.value));
        this.f.querySelectorAll('input[name*="price"],input[name*="total"]').forEach(f=>{ f.addEventListener('blur',()=>{ const n=parseFloat(f.value.replace(/[^\d.]/g,'')); !isNaN(n)&&(f.value=n.toFixed(2)); }); });
    }
    validation() { this.f.querySelectorAll('input,select,textarea').forEach(f=>{ f.addEventListener('blur',()=>this.valField(f)); f.addEventListener('input',()=>f.classList.contains('is-invalid')&&this.clearErr(f)); }); }
    valField(f) {
        const v=f.value.trim(); this.clearErr(f);
        if(f.hasAttribute('required')&&!v) return this.showErr(f,'Задължително поле');
        if(f.type==='email'&&v&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return this.showErr(f,'Невалиден имейл');
        if(f.name.includes('phone')&&v&&!/^[\+]?[0-9\s\-\(\)]{6,15}$/.test(v)) return this.showErr(f,'Невалиден телефон');
        return true;
    }
    showErr(f,m) { f.classList.add('is-invalid'); const d=document.createElement('div'); d.className='error-message'; d.textContent=m; f.parentNode.appendChild(d); f.focus(); return false; }
    clearErr(f) { f.classList.remove('is-invalid'); f.parentNode.querySelector('.error-message')?.remove(); }
    formSubmit() { this.f.addEventListener('submit',e=>{ if(!this.valForm()) e.preventDefault(); }); }
    valForm() { let v=true; this.f.querySelectorAll('input:not([type="hidden"]),select,textarea').forEach(f=>{ if(!this.valField(f)) v=false; }); if(!v) U.alert('Поправете грешките преди изпращане','warning'); return v; }
}

const Prod = {
    init() { const f=document.getElementById('productForm'); if(!f) return; f.querySelectorAll('input,select,textarea').forEach(i=>{ i.addEventListener('blur',()=>this.valF(i)); i.addEventListener('input',()=>this.valF(i)); }); f.addEventListener('submit',e=>{ if(!this.valAll()) { e.preventDefault(); U.alert('Поправете грешките','warning'); } }); },
    valF(f) { f.classList.remove('input-valid','input-invalid'); f.classList.add(f.checkValidity()?'input-valid':'input-invalid'); return f.checkValidity(); },
    valAll() { let v=true; document.getElementById('productForm')?.querySelectorAll('input,select,textarea').forEach(f=>{ if(!this.valF(f)) v=false; }); return v; }
};

const Orders = {
    init() { document.getElementById('statusFilter')?.addEventListener('change',function(){ const p=new URLSearchParams(window.location.search); this.value?p.set('status',this.value):p.delete('status'); window.location.href=window.location.pathname+'?'+p; }); document.querySelectorAll('.order-row').forEach(r=>{ r.addEventListener('mouseenter',()=>r.classList.add('row-hover')); r.addEventListener('mouseleave',()=>r.classList.remove('row-hover')); r.addEventListener('click',e=>{ if(!e.target.closest('button,a')) { const id=r.dataset.orderId; id&&(window.location.href='/orders/'+id+'/'); } }); }); this.anim(); },
    anim() { ['stats-card','order-row'].forEach(s=>document.querySelectorAll('.'+s).forEach((e,i)=>{ setTimeout(()=>e.style.cssText='transition:all 0.5s;opacity:1;transform:translateY(0)',i*50); })); }
};

const Privacy = {
    init() { const e=document.querySelector('.last-updated'); if(e) { const d=new Date(), m=['яну','фев','мар','апр','май','юни','юли','авг','сеп','окт','ное','дек']; e.textContent=`Актуализация: ${d.getDate()} ${m[d.getMonth()]} ${d.getFullYear()}`; } document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{ e.preventDefault(); document.querySelector(a.getAttribute('href'))?.scrollIntoView({behavior:'smooth'}); })); if(!document.querySelector('.print-btn')) { const b=document.createElement('button'); b.className='print-btn'; b.innerHTML='🖨 Принтирай'; b.onclick=()=>window.print(); document.body.appendChild(b); } }
};

function initAllModules() {
    Main.init();
    const p=window.location.pathname;
    if(p.includes('categories')) Cat.init();
    if(p.includes('product')&&p.includes('form')) Prod.init();
    if(p.includes('orders')) Orders.init();
    if(p.includes('privacy')||p.includes('terms')) Privacy.init();
    new OrderForm();
}



