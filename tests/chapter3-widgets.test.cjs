const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
function load(file,values={}){
 const html=fs.readFileSync(path.join(__dirname,'../ch03',file),'utf8');
 const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
 const elements=new Map();
 for(const [,id]of html.matchAll(/id="([^"]+)"/g))elements.set(id,{value:values[id]??'',textContent:'',innerHTML:'',attributes:{},style:{},setAttribute(k,v){this.attributes[k]=v},getAttribute(k){return this.attributes[k]},querySelectorAll(){return []}});
 const main={clientWidth:700,getBoundingClientRect(){return {height:700}}},draws=[];
 const context=vm.createContext({document:{getElementById:id=>elements.get(id),querySelector:()=>main},window:{frameElement:null},ResizeObserver:class{observe(){}},Plotly:{react:async(...args)=>draws.push(args)}});
 vm.runInContext(script,context);
 return {elements,draws,run:code=>JSON.parse(JSON.stringify(vm.runInContext(code,context))),tick:()=>new Promise(r=>setImmediate(r))};
}
test('transformation playground preserves correct basis images at meaningful settings',async()=>{
 const w=load('transformation-widget.html',{kind:'shear',amount:'1'});await w.tick();
 assert.deepEqual(w.run("matrix('shear',2)"),[[1,2],[0,1]]);
 assert.deepEqual(w.run("matrix('scale',0)"),[[0,0],[0,1]]);
 assert.deepEqual(w.run("project([1,1],matrix('reflection',1))"),[1,-1]);
 assert.deepEqual(w.run("project([3,5],matrix('projection',1))"),[3,0]);
 const rotated=w.run("project([1,0],matrix('rotation',90))");assert.ok(Math.abs(rotated[0])<1e-12);assert.equal(rotated[1],1);
 w.elements.get('kind').value='projection';w.elements.get('kind').onchange();await w.tick();assert.equal(w.elements.get('amount').disabled,true);assert.match(w.elements.get('description').textContent,/second column is zero/);
});
test('product explorer maps each input column to its matching output column',async()=>{
 const w=load('matrix-product-widget.html');await w.tick();assert.deepEqual(w.run('product'),[[0,9],[7,1]]);
 assert.match(w.elements.get('ab').attributes['aria-label'],/0, not revealed; 7, not revealed/);
 w.elements.get('column2').onclick();await w.tick();assert.match(w.elements.get('calculation').attributes['aria-label'],/4 times column 1 of A plus -1 times column 2 of A/);
 assert.match(w.elements.get('ab').attributes['aria-label'],/not revealed, 9; not revealed, 1/);
 w.elements.get('both').onclick();await w.tick();assert.match(w.elements.get('ab').attributes['aria-label'],/0, 9; 7, 1/);
 assert.equal(w.elements.get('both').attributes['aria-pressed'],'true');
});
test('composition explorer computes both orders, including cases that commute',async()=>{
 const w=load('composition-widget.html',{angle:'90',stretch:'2'});await w.tick();
 assert.equal(w.elements.get('rh').attributes['aria-label'],'RH rows 0, −1; 2, 0');
 assert.equal(w.elements.get('hr').attributes['aria-label'],'HR rows 0, −2; 1, 0');
 assert.match(w.elements.get('result').textContent,/Different outputs/);
 w.elements.get('stretch').value='1';w.elements.get('stretch').oninput();await w.tick();assert.match(w.elements.get('result').textContent,/same matrix/);
 w.elements.get('angle').value='0';w.elements.get('stretch').value='3';w.elements.get('angle').oninput();await w.tick();assert.match(w.elements.get('result').textContent,/same matrix/);
});
