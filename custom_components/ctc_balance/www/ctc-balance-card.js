(async () => {
  const CARD_VERSION = "v1.1.6";
  console.log(
    `%cCTC Balance Card ${CARD_VERSION}`,
     "color: #000000ff; font-weight: bold; background: rgba(0,0,0,0.2); padding:3px 8px; border-radius:6px; backdrop-filter: blur(2px);"
  );

  await Promise.race([customElements.whenDefined("ha-card"), customElements.whenDefined("ha-panel-lovelace")]);
  const LitElement = window.LitElement || Object.getPrototypeOf(customElements.get("ha-card"));
  const { html, css } = LitElement.prototype;

  class CtcBalanceCard extends LitElement {
    static get properties() { return { hass:{}, config:{} }; }
    static getGridOptions() { return { rows: "auto", columns: 12 }; }

    setConfig(config) {
      if (!config) throw new Error("Invalid configuration");
      this.config = { title:"CTC 套餐余量", more_info:true, style:"v2", ...config };
    }

    get _stateObj() { return this.hass?.states[this.config.entity] || null; }

    _info(id) {
      if (navigator.vibrate) navigator.vibrate(10);
      this.dispatchEvent(new CustomEvent("hass-more-info", { detail:{ entityId:id }, bubbles:true, composed:true }));
    }

    _attr(e,k) { return e?.attributes?.[k] ?? "--"; }
    _num(e,k) { const v = parseFloat(this._attr(e,k)); return isFinite(v) ? v : null; }

    v1_metric(label, value, icon, danger, e) {
      return html`
        <div class="v1-metric-box ${danger?"danger":""}" @click=${()=>this._info(e.entity_id)}>
          <ha-icon .icon=${icon}></ha-icon>
          <div class="l">${label}</div>
          <div class="v">${value}</div>
        </div>`;
    }

    v1_bar(label, rate, remain, total) {
      if (rate == null) return html``;
      const cls = rate>=90 ? "danger" : rate>=80 ? "warn" : "";
      return html`
        <div class="v1-meter-container ${cls}">
          <div class="m-top"><span>${label}</span><b>${rate}%</b></div>
          <div class="bar-bg"><div class="fill" style="width:${rate}%"></div></div>
          <div class="m-btm"><span>剩余 ${remain}</span><span>总量 ${total}</span></div>
        </div>`;
    }

    v1_group(title, e, items) {
      const rows = items.map(it => html`
        <div class="row" @click=${()=>this._info(e.entity_id)}>
          <span>${it.name}</span><b>${it.value}</b>
        </div>`);

      return rows.length ? html`
        <div class="g-title">${title}</div>
        <div class="g-grid">${rows}</div>` : html``;
    }

    renderV1(e) {
      const a = e.attributes;
      const phone = a.friendly_name?.split(" ")[2] || a.friendly_name || "CTC 套餐余量";
      const isLow = parseFloat(e.state) < 10;

      const brandDomain = "ctc_balance";
      const brandIcon = html`
        <img class="brand-img"
          src="/${brandDomain}-local/icon/icon.png"
          @error=${(ev) => {
            ev.target.style.display = 'none';
            ev.target.nextElementSibling.style.display = 'block';
          }}
        />
        <ha-icon icon="mdi:sim" style="display:none"></ha-icon>
      `;

      return html`
        <div class="v1-card">
          <div class="header">
            <div class="header-text">
              <div class="title">${this.config.title}</div>
              <div class="sub">${phone}</div>
            </div>
            <div class="brand-box">${brandIcon}</div>
          </div>

          <div class="summary-grid">
            ${this.v1_metric("账户余额", `${e.state}元`, "mdi:wallet-outline", isLow, e)}
            ${this.v1_metric("本月消费", a["本月消费"], "mdi:cash-fast", false, e)}
            ${this.v1_metric("号码积分", a["号码积分"], "mdi:star-circle-outline", false, e)}
          </div>

          ${this.v1_bar("流量使用", this._num(e,"流量使用率"), a["流量剩余"], a["流量总量"])}
          ${this.v1_bar("语音通话", this._num(e,"语音使用率"), a["语音剩余"], a["语音总量"])}

          ${this.config.more_info ? html`
            ${this.v1_group("流量明细（剩余/已用/总共）", e, this._detail_items(e,
              ["流量已用","流量剩余"], ["流量包"]))}
            ${this.v1_group("语音明细（剩余/已用/总共）", e, this._detail_items(e,
              ["语音已用","语音剩余"], ["语音包"]))}
          ` : ""}

          <div class="footer">
            数据来源：大六壬 | 更新于：${(() => {
              const t = this._attr(e,"更新时间");
              return t.includes(" ") ? t.split(" ")[1] : t;
            })()}
          </div>
        </div>`;
    }

    v2_metric(label, value, icon, warn, e) {
      return html`
        <div class="metric ${warn?"warning":""}" @click=${()=>this._info(e.entity_id)}>
          <ha-icon icon="${icon}"></ha-icon>
          <div class="metric-label">${label}</div>
          <div class="metric-value">${value}</div>
        </div>`;
    }

    v2_progress(label, rate, remain, total) {
      if (rate == null) return html``;
      return html`
        <div class="meter ${this.v2_level(rate)}">
          <div class="meter-top"><span>${label}</span><span>${rate}%</span></div>
          <div class="bar"><div class="fill" style="--value:${rate}%"></div></div>
          <div class="meter-detail">
            <span>剩余 ${remain}</span>
            <span>总量 ${total}</span>
          </div>
        </div>`;
    }

    v2_level(rate) {
      if (rate >= 90) return "danger";
      if (rate >= 80) return "warn";
      return "";
    }

    // 包名简化
    _short_name(name) {
      const raw = String(name).trim();
      let n = raw.split("-")[0].trim();
      n = n.replace(/（[^）]*）/g, "").replace(/\([^)]*\)/g, "");
      n = n.replace(/电信|移动|联通/g, "");
      n = n.replace(/\d{5,}/g, "");
      n = n.replace(/体验包$/, "").replace(/包$/, "");
      n = n.trim();
      return n || raw;
    }

    // 包值压缩
    _pkg_value(s) {
      const map = {};
      let unit = null, same = true;
      for (const part of s.split("|")) {
        const m = part.trim().match(/^(剩余|已用|共|总共|总量)\s*(.*)$/);
        if (!m) continue;
        const raw = m[2].replace(/\s+/g, "");
        const nm = raw.match(/^([\d.]+)(.*)$/);
        if (!nm) return "";
        const key = (m[1] === "总共" || m[1] === "总量") ? "共" : m[1];
        const u = nm[2] || "";
        if (unit == null) unit = u; else if (u !== unit) same = false;
        map[key] = nm[1].replace(/(\.\d*?)0+$/, "$1").replace(/\.$/, "");
      }
      const vals = ["剩余", "已用", "共"].map(k => map[k]).filter(v => v != null);
      if (vals.length < 2) return "";
      return vals.join("/") + (unit && same ? " " + unit : "");
    }

    // 明细数据清洗：原始属性 -> {name, value} 展示条目
    _detail_items(e, fixed, prefixes) {
      const a = (e && e.attributes) || {};
      const keys = [
        ...fixed.filter(k => a[k] != null),
        ...Object.keys(a).filter(k => prefixes.some(p => k.startsWith(p)))
      ];
      const items = [];
      const seen = {};
      for (const k of keys) {
        const s = a[k] == null ? "" : String(a[k]);
        // 流量包/语音包 -> 简化包名 + "剩余/已用/总共" 三段式
        if (/^(流量包|语音包)/.test(k) && s.includes(":")) {
          const i = s.indexOf(":");
          let name = this._short_name(s.slice(0, i));
          seen[name] = (seen[name] || 0) + 1;
          if (seen[name] > 1) name = `${name}·${seen[name]}`;
          const val = this._pkg_value(s.slice(i + 1)) || s.slice(i + 1).trim();
          items.push({ name, value: val });
          continue;
        }
        seen[k] = (seen[k] || 0) + 1;
        items.push({ name: seen[k] > 1 ? `${k}·${seen[k]}` : k, value: s });
      }
      return items;
    }

    // 明细分组：流量 3 列（2×3）、语音 2 列（2×2）
    v2_details(title, e, items, cols = 2) {
      if (!items.length) return html``;
      return html`
        <div class="attr-group">
          <div class="attr-title">${title}</div>
          <div class="attr-grid cols-${cols}">
            ${items.map(it => html`
              <div class="attr-row" @click=${()=>this._info(e.entity_id)}>
                <div class="attr-name">${it.name}</div>
                <div class="attr-value">${it.value}</div>
              </div>`)}
          </div>
        </div>`;
    }

    renderV2(e) {
      const a = e.attributes;
      const phone = a.friendly_name?.split(" ")[2] || a.friendly_name || "CTC 套餐余量";
      const isLow = parseFloat(e.state) < 10;
      return html`
        <div class="v2-card">
          <div class="header">
            <div>
              <div class="title">${this.config.title}</div>
              <div class="subtitle">${phone}</div>
            </div>
            <ha-icon icon="mdi:sim"></ha-icon>
          </div>

          <div class="summary-grid">
            ${this.v2_metric("账户余额", `${e.state} 元`, "mdi:wallet-outline", isLow, e)}
            ${this.v2_metric("本月消费", a["本月消费"], "mdi:cash", false, e)}
            ${this.v2_metric("号码积分", a["号码积分"], "mdi:star-circle-outline", false, e)}
          </div>

          ${this.v2_progress("流量使用", this._num(e,"流量使用率"), a["流量剩余"], a["流量总量"])}
          ${this.v2_progress("语音通话", this._num(e,"语音使用率"), a["语音剩余"], a["语音总量"])}

          ${this.config.more_info ? (() => {
            const flow = this._detail_items(e, ["流量已用","流量剩余"], ["流量包"]);
            const voice = this._detail_items(e, ["语音已用","语音剩余"], ["语音包"]);
            return html`
              ${this.v2_details("流量明细（剩余/已用/总共）", e, flow, 3)}
              ${this.v2_details("语音明细（剩余/已用/总共）", e, voice, 2)}
            `;
          })() : ""}

          <div class="footer">
            数据来源：大六壬 | 更新于：${(() => {
              const t = this._attr(e,"更新时间");
              return t.includes(" ") ? t.split(" ")[1] : t;
            })()}
          </div>
        </div>`;
    }

    render() {
      if (!this.hass || !this.config) return html``;

      const e = this._stateObj;
      if (!e) {
        return html`
          <ha-card style="padding:16px;">
            <div style="color:var(--error-color);font-weight:bold;">未找到实体</div>
            <div style="font-size:12px;margin-top:4px;">请在编辑器中选择 sensor.ctc_balance_* 实体</div>
          </ha-card>`;
      }

      return html`
        <ha-card>
          ${this.config.style==="v1"
            ? this.renderV1(e)
            : this.renderV2(e)}
        </ha-card>`;
    }

    static styles = css`
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
        display:flex; justify-content:space-between; gap:8px; cursor:pointer; min-width:0; }
      .row span { flex-shrink:0; }
      .row b { color:var(--primary-text-color); word-break:break-all; text-align:right; }
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
      .attr-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:8px; }
      .attr-grid.cols-3 { grid-template-columns:repeat(3,1fr); }
      .attr-row { padding:8px; border-radius:8px; background:rgba(0,163,224,.12); cursor:pointer; min-width:0; }
      .attr-name { font-size:12px; color:var(--secondary-text-color); word-break:break-all; line-height:1.3;
        display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
      .attr-value { font-size:12.5px; font-weight:600; margin-top:4px; word-break:break-all; line-height:1.4; }
    `;
    static getConfigElement() { return document.createElement("ctc-balance-card-editor"); }
    static getStubConfig(hass) { const auto = Object.keys(hass.states).find(e => e.startsWith("sensor.ctc_balance_") && e.endsWith("_balance"));
      return { title: "CTC 套餐余量", more_info: true, style: "v2", entity: auto || ""};
    }
  }

  class CtcBalanceCardEditor extends LitElement {
    static get properties() { return { hass:{}, config:{} }; }
    setConfig(c) { this.config = c; }
    set hass(h) {
      this._hass = h;
      if (h && this.config && !("entity" in this.config)) {
        const auto = Object.keys(h.states).find(e => e.startsWith("sensor.ctc_balance_") && e.endsWith("_balance"));
        if (auto) this._upd({ entity:auto });
      }
    }
    _upd(v) {this.dispatchEvent(new CustomEvent("config-changed", {detail:{ config:{ ...this.config, ...v } } }));}
    render() {
      if (!this.config || !this._hass) return html``;
      return html`
        <ha-form .hass=${this._hass} .data=${this.config} .computeLabel=${s => s.label} @value-changed=${e => this._upd(e.detail.value)}
          .schema=${[
            { name:"title", label:"卡片标题", selector:{ text:{} } },
            { name:"entity", label:"选择余额实体", selector:{ entity:{ domain:"sensor", integration:"ctc_balance" } } },
            { name:"style", label:"样式选择", selector:{ select:{ options:[
              { value:"v1", label:"信息版" },
              { value:"v2", label:"卡片版" }
            ]}} },
            { name:"more_info", label:"展开详细清单", selector:{ boolean:{} } }
          ]}
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
      `;
    }
  }

  customElements.define("ctc-balance-card", CtcBalanceCard);
  customElements.define("ctc-balance-card-editor", CtcBalanceCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "ctc-balance-card",
    name: "CTC 套餐余量卡片",
    preview: false,
    description: "展示 CTC 账户余额、流量和通话使用情况（两种样式切换）"
  });
})();