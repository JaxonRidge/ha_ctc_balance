const t=globalThis,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=/* @__PURE__ */Symbol(),s=/* @__PURE__ */new WeakMap;let r=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const i=this.t;if(e&&void 0===t){const e=void 0!==i&&1===i.length;e&&(t=s.get(i)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&s.set(i,t))}return t}toString(){return this.cssText}};const n=(t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new r(s,t,i)},o=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:a,defineProperty:c,getOwnPropertyDescriptor:l,getOwnPropertyNames:d,getOwnPropertySymbols:h,getPrototypeOf:p}=Object,u=globalThis,v=u.trustedTypes,g=v?v.emptyScript:"",m=u.reactiveElementPolyfillSupport,f=(t,e)=>t,$={toAttribute(t,e){switch(e){case Boolean:t=t?g:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(s){i=null}}return i}},_=(t,e)=>!a(t,e),b={attribute:!0,type:String,converter:$,reflect:!1,useDefault:!1,hasChanged:_};Symbol.metadata??=/* @__PURE__ */Symbol("metadata"),u.litPropertyMetadata??=/* @__PURE__ */new WeakMap;let y=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=/* @__PURE__ */Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&c(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:r}=l(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const n=s?.call(this);r?.call(this,e),this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??b}static _$Ei(){if(this.hasOwnProperty(f("elementProperties")))return;const t=p(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(f("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(f("properties"))){const t=this.properties,e=[...d(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=/* @__PURE__ */new Map;for(const[e,i]of this.elementProperties){const t=this._$Eu(e,i);void 0!==t&&this._$Eh.set(t,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(o(t))}else void 0!==t&&e.push(o(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=/* @__PURE__ */new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=/* @__PURE__ */new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=/* @__PURE__ */new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const i=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((i,s)=>{if(e)i.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const e of s){const s=document.createElement("style"),r=t.litNonce;void 0!==r&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}})(i,this.constructor.elementStyles),i}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:$).toAttribute(e,i.type);this._$Em=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:$;this._$Em=s;const n=r.fromAttribute(e,t.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(t,e,i,s=!1,r){if(void 0!==t){const n=this.constructor;if(!1===s&&(r=this[t]),i??=n.getPropertyOptions(t),!((i.hasChanged??_)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:r},n){i&&!(this._$Ej??=/* @__PURE__ */new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),!0!==r||void 0!==n)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=/* @__PURE__ */new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(i){throw t=!1,this._$EM(),i}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=/* @__PURE__ */new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[f("elementProperties")]=/* @__PURE__ */new Map,y[f("finalized")]=/* @__PURE__ */new Map,m?.({ReactiveElement:y}),(u.reactiveElementVersions??=[]).push("2.1.2");const x=globalThis,A=t=>t,w=x.trustedTypes,E=w?w.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,k="?"+C,P=`<${k}>`,O=document,U=()=>O.createComment(""),z=t=>null===t||"object"!=typeof t&&"function"!=typeof t,T=Array.isArray,H="[ \t\n\f\r]",M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,N=/-->/g,R=/>/g,j=RegExp(`>|${H}(?:([^\\s"'>=/]+)(${H}*=${H}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),D=/'/g,L=/"/g,B=/^(?:script|style|textarea|title)$/i,I=(J=1,(t,...e)=>({_$litType$:J,strings:t,values:e})),V=/* @__PURE__ */Symbol.for("lit-noChange"),W=/* @__PURE__ */Symbol.for("lit-nothing"),q=/* @__PURE__ */new WeakMap,F=O.createTreeWalker(O,129);var J;function K(t,e){if(!T(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}class Z{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let r=0,n=0;const o=t.length-1,a=this.parts,[c,l]=((t,e)=>{const i=t.length-1,s=[];let r,n=2===e?"<svg>":3===e?"<math>":"",o=M;for(let a=0;a<i;a++){const e=t[a];let i,c,l=-1,d=0;for(;d<e.length&&(o.lastIndex=d,c=o.exec(e),null!==c);)d=o.lastIndex,o===M?"!--"===c[1]?o=N:void 0!==c[1]?o=R:void 0!==c[2]?(B.test(c[2])&&(r=RegExp("</"+c[2],"g")),o=j):void 0!==c[3]&&(o=j):o===j?">"===c[0]?(o=r??M,l=-1):void 0===c[1]?l=-2:(l=o.lastIndex-c[2].length,i=c[1],o=void 0===c[3]?j:'"'===c[3]?L:D):o===L||o===D?o=j:o===N||o===R?o=M:(o=j,r=void 0);const h=o===j&&t[a+1].startsWith("/>")?" ":"";n+=o===M?e+P:l>=0?(s.push(i),e.slice(0,l)+S+e.slice(l)+C+h):e+C+(-2===l?a:h)}return[K(t,n+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]})(t,e);if(this.el=Z.createElement(c,i),F.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=F.nextNode())&&a.length<o;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(S)){const e=l[n++],i=s.getAttribute(t).split(C),o=/([.?@])?(.*)/.exec(e);a.push({type:1,index:r,name:o[2],strings:i,ctor:"."===o[1]?tt:"?"===o[1]?et:"@"===o[1]?it:X}),s.removeAttribute(t)}else t.startsWith(C)&&(a.push({type:6,index:r}),s.removeAttribute(t));if(B.test(s.tagName)){const t=s.textContent.split(C),e=t.length-1;if(e>0){s.textContent=w?w.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],U()),F.nextNode(),a.push({type:2,index:++r});s.append(t[e],U())}}}else if(8===s.nodeType)if(s.data===k)a.push({type:2,index:r});else{let t=-1;for(;-1!==(t=s.data.indexOf(C,t+1));)a.push({type:7,index:r}),t+=C.length-1}r++}}static createElement(t,e){const i=O.createElement("template");return i.innerHTML=t,i}}function G(t,e,i=t,s){if(e===V)return e;let r=void 0!==s?i._$Co?.[s]:i._$Cl;const n=z(e)?void 0:e._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),void 0===n?r=void 0:(r=new n(t),r._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=r:i._$Cl=r),void 0!==r&&(e=G(t,r._$AS(t,e.values),r,s)),e}class Y{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??O).importNode(e,!0);F.currentNode=s;let r=F.nextNode(),n=0,o=0,a=i[0];for(;void 0!==a;){if(n===a.index){let e;2===a.type?e=new Q(r,r.nextSibling,this,t):1===a.type?e=new a.ctor(r,a.name,a.strings,this,t):6===a.type&&(e=new st(r,this,t)),this._$AV.push(e),a=i[++o]}n!==a?.index&&(r=F.nextNode(),n++)}return F.currentNode=O,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class Q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=W,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=G(this,t,e),z(t)?t===W||null==t||""===t?(this._$AH!==W&&this._$AR(),this._$AH=W):t!==this._$AH&&t!==V&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>T(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==W&&z(this._$AH)?this._$AA.nextSibling.data=t:this.T(O.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Z.createElement(K(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Y(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=q.get(t.strings);return void 0===e&&q.set(t.strings,e=new Z(t)),e}k(t){T(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const r of t)s===e.length?e.push(i=new Q(this.O(U()),this.O(U()),this,this.options)):i=e[s],i._$AI(r),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=A(t).nextSibling;A(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,r){this.type=1,this._$AH=W,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=W}_$AI(t,e=this,i,s){const r=this.strings;let n=!1;if(void 0===r)t=G(this,t,e,0),n=!z(t)||t!==this._$AH&&t!==V,n&&(this._$AH=t);else{const s=t;let o,a;for(t=r[0],o=0;o<r.length-1;o++)a=G(this,s[i+o],e,o),a===V&&(a=this._$AH[o]),n||=!z(a)||a!==this._$AH[o],a===W?t=W:t!==W&&(t+=(a??"")+r[o+1]),this._$AH[o]=a}n&&!s&&this.j(t)}j(t){t===W?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends X{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===W?void 0:t}}class et extends X{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==W)}}class it extends X{constructor(t,e,i,s,r){super(t,e,i,s,r),this.type=5}_$AI(t,e=this){if((t=G(this,t,e,0)??W)===V)return;const i=this._$AH,s=t===W&&i!==W||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==W&&(i===W||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class st{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){G(this,t)}}const rt=x.litHtmlPolyfillSupport;rt?.(Z,Q),(x.litHtmlVersions??=[]).push("3.3.3");const nt=globalThis;class ot extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let r=s._$litPart$;if(void 0===r){const t=i?.renderBefore??null;s._$litPart$=r=new Q(e.insertBefore(U(),t),t,void 0,i??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return V}}ot._$litElement$=!0,ot.finalized=!0,nt.litElementHydrateSupport?.({LitElement:ot});const at=nt.litElementPolyfillSupport;at?.({LitElement:ot}),(nt.litElementVersions??=[]).push("4.2.2");console.log("%cCTC Balance Card v1.1.2","color: #000000ff; font-weight: bold; background: rgba(0,0,0,0.2); padding:3px 8px; border-radius:6px; backdrop-filter: blur(2px);");class ct extends ot{static get properties(){return{hass:{},config:{}}}static getGridOptions(){return{rows:"auto",columns:12}}setConfig(t){if(!t)throw new Error("Invalid configuration");this.config={title:"CTC 套餐余量",more_info:!0,style:"v2",...t}}get _stateObj(){return this.hass?.states[this.config.entity]||null}_info(t){navigator.vibrate&&navigator.vibrate(10),this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:t},bubbles:!0,composed:!0}))}_attr(t,e){return t?.attributes?.[e]??"--"}_num(t,e){const i=parseFloat(this._attr(t,e));return isFinite(i)?i:null}v1_metric(t,e,i,s,r){return I`
      <div class="v1-metric-box ${s?"danger":""}" @click=${()=>this._info(r.entity_id)}>
        <ha-icon .icon=${i}></ha-icon>
        <div class="l">${t}</div>
        <div class="v">${e}</div>
      </div>`}v1_bar(t,e,i,s){if(null==e)return I``;return I`
      <div class="v1-meter-container ${e>=90?"danger":e>=80?"warn":""}">
        <div class="m-top"><span>${t}</span><b>${e}%</b></div>
        <div class="bar-bg"><div class="fill" style="width:${e}%"></div></div>
        <div class="m-btm"><span>剩余 ${i}</span><span>总量 ${s}</span></div>
      </div>`}v1_group(t,e,i){const s=i.map(t=>{const i=this._attr(e,t);return"--"!==i?I`
        <div class="row" @click=${()=>this._info(e.entity_id)}>
          <span>${t}</span><b>${i}</b>
        </div>`:null}).filter(Boolean);return s.length?I`
      <div class="g-title">${t}</div>
      <div class="g-grid">${s}</div>`:I``}renderV1(t){const e=t.attributes,i=e.friendly_name?.split(" ")[2]||e.friendly_name||"CTC 套餐余量",s=parseFloat(t.state)<10,r=I`
      <img class="brand-img"
        src="/${"ctc_balance"}-local/icon/icon.png"
        @error=${t=>{t.target.style.display="none",t.target.nextElementSibling.style.display="block"}}
      />
      <ha-icon icon="mdi:sim" style="display:none"></ha-icon>
    `;return I`
      <div class="v1-card">
        <div class="header">
          <div class="header-text">
            <div class="title">${this.config.title}</div>
            <div class="sub">${i}</div>
          </div>
          <div class="brand-box">${r}</div>
        </div>

        <div class="summary-grid">
          ${this.v1_metric("账户余额",`${t.state}元`,"mdi:wallet-outline",s,t)}
          ${this.v1_metric("本月消费",e["本月消费"],"mdi:cash-fast",!1,t)}
          ${this.v1_metric("号码积分",e["号码积分"],"mdi:star-circle-outline",!1,t)}
        </div>

        ${this.v1_bar("流量使用",this._num(t,"流量使用率"),e["流量剩余"],e["流量总量"])}
        ${this.v1_bar("语音通话",this._num(t,"语音使用率"),e["语音剩余"],e["语音总量"])}

        ${this.config.more_info?I`
          ${this.v1_group("流量明细",t,["流量已用","流量剩余","通用总量","通用已用","专用总量","专用已用"])}
          ${this.v1_group("语音/云盘",t,["语音已用","语音剩余","云盘剩余"])}
        `:""}

        <div class="footer">
          数据来源：大六壬 | 更新于：${(()=>{const e=this._attr(t,"更新时间");return e.includes(" ")?e.split(" ")[1]:e})()}
        </div>
      </div>`}v2_metric(t,e,i,s,r){return I`
      <div class="metric ${s?"warning":""}" @click=${()=>this._info(r.entity_id)}>
        <ha-icon icon="${i}"></ha-icon>
        <div class="metric-label">${t}</div>
        <div class="metric-value">${e}</div>
      </div>`}v2_progress(t,e,i,s){return null==e?I``:I`
      <div class="meter ${this.v2_level(e)}">
        <div class="meter-top"><span>${t}</span><span>${e}%</span></div>
        <div class="bar"><div class="fill" style="--value:${e}%"></div></div>
        <div class="meter-detail">
          <span>剩余 ${i}</span>
          <span>总量 ${s}</span>
        </div>
      </div>`}v2_level(t){return t>=90?"danger":t>=80?"warn":""}v2_attrs(t,e,i){const s=i.map(t=>{const i=this._attr(e,t);return"--"!==i?I`
        <div class="attr-row" @click=${()=>this._info(e.entity_id)}>
          <div class="attr-name">${t}</div>
          <div class="attr-value">${i}</div>
        </div>`:null}).filter(Boolean);return s.length?I`
      <div class="attr-group">
        <div class="attr-title">${t}</div>
        <div class="attr-grid">${s}</div>
      </div>`:I``}renderV2(t){const e=t.attributes,i=e.friendly_name?.split(" ")[2]||e.friendly_name||"CTC 套餐余量",s=parseFloat(t.state)<10;return I`
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
          ${this.v2_metric("本月消费",e["本月消费"],"mdi:cash",!1,t)}
          ${this.v2_metric("号码积分",e["号码积分"],"mdi:star-circle-outline",!1,t)}
        </div>

        ${this.v2_progress("流量使用",this._num(t,"流量使用率"),e["流量剩余"],e["流量总量"])}
        ${this.v2_progress("语音通话",this._num(t,"语音使用率"),e["语音剩余"],e["语音总量"])}

        ${this.config.more_info?I`
          ${this.v2_attrs("流量明细",t,["流量已用","流量剩余","流量总量","流量超量","通用总量","通用已用","通用超额","专用总量","专用已用"])}
          ${this.v2_attrs("语音/云盘",t,["语音已用","语音剩余","语音总量","云盘剩余"])}
        `:""}

        <div class="footer">
          数据来源：大六壬 | 更新于：${(()=>{const e=this._attr(t,"更新时间");return e.includes(" ")?e.split(" ")[1]:e})()}
        </div>
      </div>`}render(){if(!this.hass||!this.config)return I``;const t=this._stateObj;return t?I`
      <ha-card>
        ${"v1"===this.config.style?this.renderV1(t):this.renderV2(t)}
      </ha-card>`:I`
        <ha-card style="padding:16px;">
          <div style="color:var(--error-color);font-weight:bold;">未找到实体</div>
          <div style="font-size:12px;margin-top:4px;">请在编辑器中选择 sensor.ctc_balance_* 实体</div>
        </ha-card>`}static styles=n`
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
  `;static getConfigElement(){return document.createElement("ctc-balance-card-editor")}static getStubConfig(t){return{title:"CTC 套餐余量",more_info:!0,style:"v2",entity:Object.keys(t.states).find(t=>t.startsWith("sensor.")&&t.includes("_ctc_account_balance"))||""}}}customElements.define("ctc-balance-card",ct),customElements.define("ctc-balance-card-editor",class extends ot{static get properties(){return{hass:{},config:{}}}setConfig(t){this.config=t}set hass(t){if(this._hass=t,t&&this.config&&!("entity"in this.config)){const e=Object.keys(t.states).find(t=>t.startsWith("sensor.")&&t.includes("_ctc_account_balance"));e&&this._upd({entity:e})}}_upd(t){this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:{...this.config,...t}}}))}render(){return this.config&&this._hass?I`
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
    `:I``}}),window.customCards=window.customCards||[],window.customCards.push({type:"ctc-balance-card",name:"CTC 套餐余量卡片",preview:!1,description:"展示 CTC 账户余额、流量和通话使用情况（两种样式切换）"});
