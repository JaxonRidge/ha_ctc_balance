const U=globalThis,R=U.ShadowRoot&&(U.ShadyCSS===void 0||U.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,j=Symbol(),I=new WeakMap;let X=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==j)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(R&&t===void 0){const i=e!==void 0&&e.length===1;i&&(t=I.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&I.set(e,t))}return t}toString(){return this.cssText}};const nt=n=>new X(typeof n=="string"?n:n+"",void 0,j),ot=(n,...t)=>{const e=n.length===1?n[0]:t.reduce((i,s,r)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+n[r+1],n[0]);return new X(e,n,j)},at=(n,t)=>{if(R)n.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const e of t){const i=document.createElement("style"),s=U.litNonce;s!==void 0&&i.setAttribute("nonce",s),i.textContent=e.cssText,n.appendChild(i)}},V=R?n=>n:n=>n instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return nt(e)})(n):n;const{is:ct,defineProperty:lt,getOwnPropertyDescriptor:dt,getOwnPropertyNames:ht,getOwnPropertySymbols:pt,getPrototypeOf:ut}=Object,T=globalThis,W=T.trustedTypes,vt=W?W.emptyScript:"",ft=T.reactiveElementPolyfillSupport,E=(n,t)=>n,N={toAttribute(n,t){switch(t){case Boolean:n=n?vt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,t){let e=n;switch(t){case Boolean:e=n!==null;break;case Number:e=n===null?null:Number(n);break;case Object:case Array:try{e=JSON.parse(n)}catch{e=null}}return e}},tt=(n,t)=>!ct(n,t),q={attribute:!0,type:String,converter:N,reflect:!1,useDefault:!1,hasChanged:tt};Symbol.metadata??=Symbol("metadata"),T.litPropertyMetadata??=new WeakMap;let b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=q){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);s!==void 0&&lt(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:r}=dt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:s,set(o){const c=s?.call(this);r?.call(this,o),this.requestUpdate(t,c,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??q}static _$Ei(){if(this.hasOwnProperty(E("elementProperties")))return;const t=ut(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(E("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(E("properties"))){const e=this.properties,i=[...ht(e),...pt(e)];for(const s of i)this.createProperty(s,e[s])}const t=this[Symbol.metadata];if(t!==null){const e=litPropertyMetadata.get(t);if(e!==void 0)for(const[i,s]of e)this.elementProperties.set(i,s)}this._$Eh=new Map;for(const[e,i]of this.elementProperties){const s=this._$Eu(e,i);s!==void 0&&this._$Eh.set(s,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const s of i)e.unshift(V(s))}else t!==void 0&&e.push(V(t));return e}static _$Eu(t,e){const i=e.attribute;return i===!1?void 0:typeof i=="string"?i:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return at(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(s!==void 0&&i.reflect===!0){const r=(i.converter?.toAttribute!==void 0?i.converter:N).toAttribute(e,i.type);this._$Em=t,r==null?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(s!==void 0&&this._$Em!==s){const r=i.getPropertyOptions(s),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:N;this._$Em=s;const c=o.fromAttribute(e,r.type);this[s]=c??this._$Ej?.get(s)??c,this._$Em=null}}requestUpdate(t,e,i,s=!1,r){if(t!==void 0){const o=this.constructor;if(s===!1&&(r=this[t]),i??=o.getPropertyOptions(t),!((i.hasChanged??tt)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,i))))return;this.C(t,e,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:r},o){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),r!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),s===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[s,r]of this._$Ep)this[s]=r;this._$Ep=void 0}const i=this.constructor.elementProperties;if(i.size>0)for(const[s,r]of i){const{wrapped:o}=r,c=this[s];o!==!0||this._$AL.has(s)||c===void 0||this.C(s,void 0,r,c)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(e)):this._$EM()}catch(i){throw t=!1,this._$EM(),i}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[E("elementProperties")]=new Map,b[E("finalized")]=new Map,ft?.({ReactiveElement:b}),(T.reactiveElementVersions??=[]).push("2.1.2");const D=globalThis,F=n=>n,z=D.trustedTypes,Z=z?z.createPolicy("lit-html",{createHTML:n=>n}):void 0,et="$lit$",m=`lit$${Math.random().toFixed(9).slice(2)}$`,it="?"+m,mt=`<${it}>`,_=document,C=()=>_.createComment(""),S=n=>n===null||typeof n!="object"&&typeof n!="function",L=Array.isArray,gt=n=>L(n)||typeof n?.[Symbol.iterator]=="function",M=`[ 	
\f\r]`,w=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,J=/-->/g,K=/>/g,g=RegExp(`>|${M}(?:([^\\s"'>=/]+)(${M}*=${M}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),G=/'/g,Y=/"/g,st=/^(?:script|style|textarea|title)$/i,$t=n=>(t,...e)=>({_$litType$:n,strings:t,values:e}),d=$t(1),x=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),Q=new WeakMap,$=_.createTreeWalker(_,129);function rt(n,t){if(!L(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return Z!==void 0?Z.createHTML(t):t}const _t=(n,t)=>{const e=n.length-1,i=[];let s,r=t===2?"<svg>":t===3?"<math>":"",o=w;for(let c=0;c<e;c++){const a=n[c];let h,u,l=-1,v=0;for(;v<a.length&&(o.lastIndex=v,u=o.exec(a),u!==null);)v=o.lastIndex,o===w?u[1]==="!--"?o=J:u[1]!==void 0?o=K:u[2]!==void 0?(st.test(u[2])&&(s=RegExp("</"+u[2],"g")),o=g):u[3]!==void 0&&(o=g):o===g?u[0]===">"?(o=s??w,l=-1):u[1]===void 0?l=-2:(l=o.lastIndex-u[2].length,h=u[1],o=u[3]===void 0?g:u[3]==='"'?Y:G):o===Y||o===G?o=g:o===J||o===K?o=w:(o=g,s=void 0);const f=o===g&&n[c+1].startsWith("/>")?" ":"";r+=o===w?a+mt:l>=0?(i.push(h),a.slice(0,l)+et+a.slice(l)+m+f):a+m+(l===-2?c:f)}return[rt(n,r+(n[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),i]};class P{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let r=0,o=0;const c=t.length-1,a=this.parts,[h,u]=_t(t,e);if(this.el=P.createElement(h,i),$.currentNode=this.el.content,e===2||e===3){const l=this.el.content.firstChild;l.replaceWith(...l.childNodes)}for(;(s=$.nextNode())!==null&&a.length<c;){if(s.nodeType===1){if(s.hasAttributes())for(const l of s.getAttributeNames())if(l.endsWith(et)){const v=u[o++],f=s.getAttribute(l).split(m),O=/([.?@])?(.*)/.exec(v);a.push({type:1,index:r,name:O[2],strings:f,ctor:O[1]==="."?yt:O[1]==="?"?xt:O[1]==="@"?At:H}),s.removeAttribute(l)}else l.startsWith(m)&&(a.push({type:6,index:r}),s.removeAttribute(l));if(st.test(s.tagName)){const l=s.textContent.split(m),v=l.length-1;if(v>0){s.textContent=z?z.emptyScript:"";for(let f=0;f<v;f++)s.append(l[f],C()),$.nextNode(),a.push({type:2,index:++r});s.append(l[v],C())}}}else if(s.nodeType===8)if(s.data===it)a.push({type:2,index:r});else{let l=-1;for(;(l=s.data.indexOf(m,l+1))!==-1;)a.push({type:7,index:r}),l+=m.length-1}r++}}static createElement(t,e){const i=_.createElement("template");return i.innerHTML=t,i}}function A(n,t,e=n,i){if(t===x)return t;let s=i!==void 0?e._$Co?.[i]:e._$Cl;const r=S(t)?void 0:t._$litDirective$;return s?.constructor!==r&&(s?._$AO?.(!1),r===void 0?s=void 0:(s=new r(n),s._$AT(n,e,i)),i!==void 0?(e._$Co??=[])[i]=s:e._$Cl=s),s!==void 0&&(t=A(n,s._$AS(n,t.values),s,i)),t}class bt{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??_).importNode(e,!0);$.currentNode=s;let r=$.nextNode(),o=0,c=0,a=i[0];for(;a!==void 0;){if(o===a.index){let h;a.type===2?h=new k(r,r.nextSibling,this,t):a.type===1?h=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(h=new wt(r,this,t)),this._$AV.push(h),a=i[++c]}o!==a?.index&&(r=$.nextNode(),o++)}return $.currentNode=_,s}p(t){let e=0;for(const i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=A(this,t,e),S(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==x&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):gt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&S(this._$AH)?this._$AA.nextSibling.data=t:this.T(_.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s=typeof i=="number"?this._$AC(t):(i.el===void 0&&(i.el=P.createElement(rt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const r=new bt(s,this),o=r.u(this.options);r.p(e),this.T(o),this._$AH=r}}_$AC(t){let e=Q.get(t.strings);return e===void 0&&Q.set(t.strings,e=new P(t)),e}k(t){L(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const r of t)s===e.length?e.push(i=new k(this.O(C()),this.O(C()),this,this.options)):i=e[s],i._$AI(r),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const i=F(t).nextSibling;F(t).remove(),t=i}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,r){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=p}_$AI(t,e=this,i,s){const r=this.strings;let o=!1;if(r===void 0)t=A(this,t,e,0),o=!S(t)||t!==this._$AH&&t!==x,o&&(this._$AH=t);else{const c=t;let a,h;for(t=r[0],a=0;a<r.length-1;a++)h=A(this,c[i+a],e,a),h===x&&(h=this._$AH[a]),o||=!S(h)||h!==this._$AH[a],h===p?t=p:t!==p&&(t+=(h??"")+r[a+1]),this._$AH[a]=h}o&&!s&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class yt extends H{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}}class xt extends H{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}}class At extends H{constructor(t,e,i,s,r){super(t,e,i,s,r),this.type=5}_$AI(t,e=this){if((t=A(this,t,e,0)??p)===x)return;const i=this._$AH,s=t===p&&i!==p||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==p&&(i===p||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class wt{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){A(this,t)}}const Et=D.litHtmlPolyfillSupport;Et?.(P,k),(D.litHtmlVersions??=[]).push("3.3.3");const Ct=(n,t,e)=>{const i=e?.renderBefore??t;let s=i._$litPart$;if(s===void 0){const r=e?.renderBefore??null;i._$litPart$=s=new k(t.insertBefore(C(),r),r,void 0,e??{})}return s._$AI(n),s};const B=globalThis;class y extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Ct(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}}y._$litElement$=!0,y.finalized=!0,B.litElementHydrateSupport?.({LitElement:y});const St=B.litElementPolyfillSupport;St?.({LitElement:y});(B.litElementVersions??=[]).push("4.2.2");const Pt="v1.1.1-lit";console.log(`%cCTC Balance Card ${Pt} vite`,"color:#1976d2;font-weight:bold;background:#e3f2fd;border:1px solid #1976d2;border-radius:4px;padding:2px 6px;");class kt extends y{static get properties(){return{hass:{},config:{}}}static getGridOptions(){return{rows:"auto",columns:12}}setConfig(t){if(!t)throw new Error("Invalid configuration");this.config={title:"CTC 套餐余量",more_info:!0,style:"v2",...t}}get _stateObj(){return this.hass?.states[this.config.entity]||null}_info(t){navigator.vibrate&&navigator.vibrate(10),this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:t},bubbles:!0,composed:!0}))}_attr(t,e){return t?.attributes?.[e]??"--"}_num(t,e){const i=parseFloat(this._attr(t,e));return isFinite(i)?i:null}v1_metric(t,e,i,s,r){return d`
      <div class="v1-metric-box ${s?"danger":""}" @click=${()=>this._info(r.entity_id)}>
        <ha-icon .icon=${i}></ha-icon>
        <div class="l">${t}</div>
        <div class="v">${e}</div>
      </div>`}v1_bar(t,e,i,s){if(e==null)return d``;const r=e>=90?"danger":e>=80?"warn":"";return d`
      <div class="v1-meter-container ${r}">
        <div class="m-top"><span>${t}</span><b>${e}%</b></div>
        <div class="bar-bg"><div class="fill" style="width:${e}%"></div></div>
        <div class="m-btm"><span>剩余 ${i}</span><span>总量 ${s}</span></div>
      </div>`}v1_group(t,e,i){const s=i.map(r=>{const o=this._attr(e,r);return o!=="--"?d`
        <div class="row" @click=${()=>this._info(e.entity_id)}>
          <span>${r}</span><b>${o}</b>
        </div>`:null}).filter(Boolean);return s.length?d`
      <div class="g-title">${t}</div>
      <div class="g-grid">${s}</div>`:d``}renderV1(t){const e=t.attributes,i=e.friendly_name?.split(" ")[2]||e.friendly_name||"CTC 套餐余量",s=parseFloat(t.state)<10,o=d`
      <img class="brand-img"
        src="/${"ctc_balance"}-local/icon/icon.png"
        @error=${c=>{c.target.style.display="none",c.target.nextElementSibling.style.display="block"}}
      />
      <ha-icon icon="mdi:sim" style="display:none"></ha-icon>
    `;return d`
      <div class="v1-card">
        <div class="header">
          <div class="header-text">
            <div class="title">${this.config.title}</div>
            <div class="sub">${i}</div>
          </div>
          <div class="brand-box">${o}</div>
        </div>

        <div class="summary-grid">
          ${this.v1_metric("账户余额",`${t.state}元`,"mdi:wallet-outline",s,t)}
          ${this.v1_metric("本月消费",e.本月消费,"mdi:cash-fast",!1,t)}
          ${this.v1_metric("号码积分",e.号码积分,"mdi:star-circle-outline",!1,t)}
        </div>

        ${this.v1_bar("流量使用",this._num(t,"流量使用率"),e.流量剩余,e.流量总量)}
        ${this.v1_bar("语音通话",this._num(t,"语音使用率"),e.语音剩余,e.语音总量)}

        ${this.config.more_info?d`
          ${this.v1_group("流量明细",t,["流量已用","流量剩余","通用总量","通用已用","专用总量","专用已用"])}
          ${this.v1_group("语音/云盘",t,["语音已用","语音剩余","云盘剩余"])}
        `:""}

        <div class="footer">
          数据来源：大六壬 | 更新于：${(()=>{const c=this._attr(t,"更新时间");return c.includes(" ")?c.split(" ")[1]:c})()}
        </div>
      </div>`}v2_metric(t,e,i,s,r){return d`
      <div class="metric ${s?"warning":""}" @click=${()=>this._info(r.entity_id)}>
        <ha-icon icon="${i}"></ha-icon>
        <div class="metric-label">${t}</div>
        <div class="metric-value">${e}</div>
      </div>`}v2_progress(t,e,i,s){return e==null?d``:d`
      <div class="meter ${this.v2_level(e)}">
        <div class="meter-top"><span>${t}</span><span>${e}%</span></div>
        <div class="bar"><div class="fill" style="--value:${e}%"></div></div>
        <div class="meter-detail">
          <span>剩余 ${i}</span>
          <span>总量 ${s}</span>
        </div>
      </div>`}v2_level(t){return t>=90?"danger":t>=80?"warn":""}v2_attrs(t,e,i){const s=i.map(r=>{const o=this._attr(e,r);return o!=="--"?d`
        <div class="attr-row" @click=${()=>this._info(e.entity_id)}>
          <div class="attr-name">${r}</div>
          <div class="attr-value">${o}</div>
        </div>`:null}).filter(Boolean);return s.length?d`
      <div class="attr-group">
        <div class="attr-title">${t}</div>
        <div class="attr-grid">${s}</div>
      </div>`:d``}renderV2(t){const e=t.attributes,i=e.friendly_name?.split(" ")[2]||e.friendly_name||"CTC 套餐余量",s=parseFloat(t.state)<10;return d`
      <div class="v2-card">
        <div class="header">
          <div>
            <div class="title">${this.config.title}</div>
            <div class="subtitle">${i}</div>
          </div>
          <ha-icon icon="mdi:sim"></ha-icon>
        </div>

        <div class="summary-grid">
          ${this.v2_metric("账户余额",`${t.state} 元`,"mdi:wallet-outline",s,t)}
          ${this.v2_metric("本月消费",e.本月消费,"mdi:cash",!1,t)}
          ${this.v2_metric("号码积分",e.号码积分,"mdi:star-circle-outline",!1,t)}
        </div>

        ${this.v2_progress("流量使用",this._num(t,"流量使用率"),e.流量剩余,e.流量总量)}
        ${this.v2_progress("语音通话",this._num(t,"语音使用率"),e.语音剩余,e.语音总量)}

        ${this.config.more_info?d`
          ${this.v2_attrs("流量明细",t,["流量已用","流量剩余","流量总量","流量超量","通用总量","通用已用","通用超额","专用总量","专用已用"])}
          ${this.v2_attrs("语音/云盘",t,["语音已用","语音剩余","语音总量","云盘剩余"])}
        `:""}

        <div class="footer">
          数据来源：大六壬 | 更新于：${(()=>{const r=this._attr(t,"更新时间");return r.includes(" ")?r.split(" ")[1]:r})()}
        </div>
      </div>`}render(){if(!this.hass||!this.config)return d``;const t=this._stateObj;return t?d`
      <ha-card>
        ${this.config.style==="v1"?this.renderV1(t):this.renderV2(t)}
      </ha-card>`:d`
        <ha-card style="padding:16px;">
          <div style="color:var(--error-color);font-weight:bold;">未找到实体</div>
          <div style="font-size:12px;margin-top:4px;">请在编辑器中选择 sensor.ctc_balance_* 实体</div>
        </ha-card>`}static styles=ot`
    .v1-card { --c-blue:var(--primary-color,#fff); --c-sky:#00a3e0; --c-red:#ef4444; --c-orange:#f59e0b;
      padding:16px; color:var(--primary-text-color); }
    .v1-card .header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px; }
    .v1-card .title { font-size:20px; font-weight:700; letter-spacing:-0.5px; }
    .v1-card .sub { font-size:13px; color:var(--secondary-text-color); margin-top:4px; }
    .v1-card .brand-box { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }
    .v1-card .brand-img { width:100%; height:100%; object-fit:contain; }
    .v1-card ha-icon { color:var(--c-blue); --mdc-icon-size:32px; }
    .summary-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:24px; }
    .v1-metric-box { padding:12px 8px; border-radius:12px; text-align:center; cursor:pointer;
      background:var(--secondary-background-color); border:1px solid var(--divider-color); transition:.2s; }
    .v1-metric-box:hover { border-color:var(--c-blue); transform:translateY(-2px); }
    .v1-metric-box.danger { border-color:var(--c-red); background:rgba(239,68,68,.05); }
    .v1-metric-box.danger .v, .v1-metric-box.danger ha-icon { color:var(--c-red); }
    .v1-metric-box ha-icon { --mdc-icon-size:22px; color:var(--c-blue); margin-bottom:4px; }
    .v1-metric-box .l { font-size:11px; color:var(--secondary-text-color); }
    .v1-metric-box .v { font-size:13px; font-weight:700; margin-top:2px; }
    .v1-meter-container { margin-bottom:16px; }
    .v1-meter-container .m-top { display:flex; justify-content:space-between; font-size:14px; font-weight:600; margin-bottom:8px; }
    .v1-meter-container .bar-bg { height:8px; background:var(--secondary-background-color); border-radius:4px; overflow:hidden; }
    .v1-meter-container .fill { height:100%; border-radius:4px; background:linear-gradient(90deg,var(--c-blue),var(--c-sky)); transition:width 1s cubic-bezier(.4,0,.2,1); }
    .v1-meter-container.warn .fill { background:var(--c-orange); }
    .v1-meter-container.warn .m-top b { color:var(--c-orange); }
    .v1-meter-container.danger .fill { background:var(--c-red); }
    .v1-meter-container.danger .m-top b { color:var(--c-red); }
    .v1-meter-container .m-btm { display:flex; justify-content:space-between; font-size:10.5px; color:var(--secondary-text-color); margin-top:10px; opacity:.8; }
    .g-title { font-size:14px; font-weight:700; color:var(--c-blue); margin:16px 0 10px; padding-left:4px; border-left:3px solid var(--c-blue); }
    .g-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
    .row { padding:10px 12px; background:var(--secondary-background-color); border-radius:8px; font-size:12px;
      display:flex; justify-content:space-between; cursor:pointer; }
    .row b { color:var(--primary-text-color); }
    .footer { margin-top:24px; padding-top:16px; border-top:1px solid var(--divider-color);
      text-align:center; font-size:11px; color:var(--secondary-text-color); opacity:.8; }

    .v2-card { --c-blue:var(--primary-color,#fff); --ctm-sky:#00a3e0; --ctm-orange:#f59e0b; --ctm-red:#e60012;
      padding:16px; color:var(--primary-text-color); }
    .v2-card .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
    .v2-card ha-icon { color:var(--c-blue); }
    .v2-card .title { font-size:18px; font-weight:650; }
    .v2-card .subtitle { margin-top:4px; font-size:13px; color:var(--secondary-text-color); }
    .metric { padding:10px; border-radius:8px; cursor:pointer; border:1px solid rgba(0,91,172,.18);
      background:linear-gradient(180deg,rgba(0,91,172,.08),transparent); }
    .metric ha-icon { --mdc-icon-size:22px; margin-bottom:4px; color:var(--c-blue); }
    .metric-label { font-size:11px; color:var(--secondary-text-color); }
    .metric-value { font-size:13px; font-weight:700; margin-top:2px; }
    .metric.warning .metric-value { color:var(--ctm-red); }
    .meter { margin-bottom:12px; }
    .meter-top { display:flex; justify-content:space-between; font-size:14px; font-weight:600; margin-bottom:6px; }
    .bar { height:8px; border-radius:999px; background:rgba(0,91,172,.16); overflow:hidden; }
    .fill { height:100%; width:var(--value); background:linear-gradient(90deg,var(--c-blue),var(--ctm-sky)); transition:width .8s cubic-bezier(.4,0,.2,1); }
    .meter.warn .fill { background:var(--ctm-orange); }
    .meter.danger .fill { background:var(--ctm-red); }
    .meter-detail { display:flex; justify-content:space-between; margin-top:10px; font-size:11px;
      font-weight:400; color:var(--secondary-text-color); opacity:.85; }
    .attr-group { margin-top:16px; }
    .attr-title { font-size:14px; font-weight:650; margin-bottom:8px; color:var(--c-blue); }
    .attr-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
    .attr-row { padding:8px; border-radius:8px; background:rgba(0,163,224,.12); cursor:pointer; }
    .attr-name { font-size:12px; color:var(--secondary-text-color); }
    .attr-value { font-size:14px; font-weight:600; margin-top:4px; }
  `;static getConfigElement(){return document.createElement("ctc-balance-card-editor")}static getStubConfig(t){return{title:"CTC 套餐余量",more_info:!0,style:"v2",entity:Object.keys(t.states).find(i=>i.startsWith("sensor.ctc_balance_")&&i.includes("_account_balance"))||""}}}class Ot extends y{static get properties(){return{hass:{},config:{}}}setConfig(t){this.config=t}set hass(t){if(this._hass=t,t&&this.config&&!("entity"in this.config)){const e=Object.keys(t.states).find(i=>i.startsWith("sensor.ctc_balance_")&&i.includes("_account_balance"));e&&this._upd({entity:e})}}_upd(t){this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:{...this.config,...t}}}))}render(){return!this.config||!this._hass?d``:d`
      <ha-form .hass=${this._hass} .data=${this.config} .computeLabel=${t=>t.label} @value-changed=${t=>this._upd(t.detail.value)}
        .schema=${[{name:"title",label:"卡片标题",selector:{text:{}}},{name:"entity",label:"选择余额实体",selector:{entity:{domain:"sensor",integration:"ctc_balance"}}},{name:"style",label:"样式选择",selector:{select:{options:[{value:"v1",label:"信息版"},{value:"v2",label:"卡片版"}]}}},{name:"more_info",label:"展开详细清单",selector:{boolean:{}}}]}
      ></ha-form>

      <div style="
        background:var(--secondary-background-color);
        padding:12px;
        border-radius:8px;
        margin-top:16px;
        border-left:4px solid var(--primary-color);
        font-size:12px;
        line-height:1.6;
      ">
        <div style="font-weight:bold;display:flex;align-items:center;margin-bottom:4px;">
          <ha-icon icon="mdi:information-outline"
            style="--mdc-icon-size:18px;margin-right:4px;color:var(--primary-color);">
          </ha-icon>
          配置说明
        </div>
        请选择<b> 账户余量 </b>实体，并选择你喜欢的样式。
      </div>
    `}}customElements.define("ctc-balance-card",kt);customElements.define("ctc-balance-card-editor",Ot);window.customCards=window.customCards||[];window.customCards.push({type:"ctc-balance-card",name:"CTC 套餐余量卡片",preview:!1,description:"展示 CTC 账户余额、流量和通话使用情况（两种样式切换）"});
