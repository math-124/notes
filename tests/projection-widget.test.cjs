// Run with: node --test tests/projection-widget.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname,'../ch03/projection-widget.html'),'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
function widget() {
  const elements = new Map();
  for (const [,id] of html.matchAll(/id="([^"]+)"/g)) elements.set(id,{
    value: id==='height'?'1':'0', textContent:'', hidden:true, attributes:{}, handlers:{},
    setAttribute(k,v){this.attributes[k]=v}, addEventListener(k,v){this.handlers[k]=v}, querySelectorAll(){return []}
  });
  const draws=[];
  const context=vm.createContext({document:{getElementById:id=>elements.get(id)},console,Plotly:{react:async (...args)=>draws.push(args)}});
  vm.runInContext(script,context);
  return {elements,draws,run:code=>JSON.parse(JSON.stringify(vm.runInContext(code,context))),async event(id,type,value){const el=elements.get(id);if(value!==undefined)el.value=String(value);el.handlers[type]();await new Promise(resolve=>setImmediate(resolve));}};
}
test('coordinate rules: basis columns, roof heights, and all intermediate maps are linear',()=>{
 const w=widget();
 assert.deepEqual(w.run('[[1,0,0],[0,1,0],[0,0,1]].map(p=>project(p,A))'),[[40,20],[-40,20],[0,-40]]);
 assert.deepEqual(w.run('[0,1,2].map(h=>project([1,1,h],A))'),[[0,40],[0,0],[0,-40]]);
 assert.deepEqual(w.run('project([1,1,2],TOP)'),[40,40]);
 for(const t of [0,.25,.5,.75,1]) {
  assert.deepEqual(w.run(`project([5,3,4],matrixAt(${t}))`),w.run(`project([2,0,1],matrixAt(${t})).map((v,i)=>v+project([3,3,3],matrixAt(${t}))[i])`));
 }
 for(const t of [0,.25,.5,.75,1]) assert.ok(w.run(`(()=>{const m=matrixAt(${t});return m[0][0]*m[1][1]-m[0][1]*m[1][0]})()`)>0, 'Ground tile must not collapse between views');
 assert.deepEqual(w.run('project([2,0,1],A)'),w.run('project([3,1,2],A)'));
});
test('controls redraw actual geometry, synchronize readouts, and reset',async()=>{
 const w=widget();await w.event('game','click');
 assert.deepEqual(w.run('geometry().roof'),[0,0]);
 await w.event('height','input',2);
 assert.deepEqual(w.run('geometry().roof'),[0,-40]);
 assert.equal(w.elements.get('screen-y').textContent,'−40');
 assert.equal(w.elements.get('height').attributes['aria-valuetext'],'2.00 units');
 await w.event('height','input',0);
 assert.deepEqual(w.run('geometry().roof'),[0,40]);
 assert.ok(w.draws.at(-1)[1].every(trace=>trace.x.every(x=>x===null||Number.isFinite(x))));
 await w.event('basis','click'); assert.equal(w.elements.get('basis').attributes['aria-pressed'],'true');
 await w.event('reveal','click');assert.deepEqual(w.run('geometry().roof'),[0,0]);assert.match(w.elements.get('status').textContent,/Same pixel!/);
 await w.event('reset','click');assert.deepEqual(w.run('state'),{view:0,height:1,basis:false,reveal:false});
 assert.equal(w.elements.get('view').value,0);assert.equal(w.elements.get('basis').attributes['aria-pressed'],'false');
});
test('rapid slider events render the latest input and preserve finite geometry',async()=>{
 const w=widget();
 for(let i=0;i<=100;i++){w.elements.get('view').value=i;w.elements.get('view').handlers.input();}
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(w.elements.get('map-name').textContent,'Apply A');
 const marker=w.draws.at(-1)[1].at(-1);assert.deepEqual(JSON.parse(JSON.stringify([marker.x,marker.y])),[[0],[0]]);
});
