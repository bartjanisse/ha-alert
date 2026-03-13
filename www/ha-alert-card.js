/**
 * HA Alert Card v1.2.5
 * Maximum compatibility build
 */

var HA_ALERT_TRANSLATIONS = {
  nl: {
    acknowledge:     'Herinner',
    acknowledged:    'Herinnerd',
    dismiss:         'Sluiten',
    no_alerts:       'Geen actieve alerts',
    every:           'elke',
    min:             'min',
    error:           'FOUT',
    warning:         'WAARSCHUWING',
    info:            'INFO',
    success:         'SUCCES'
  },
  en: {
    acknowledge:     'Acknowledge',
    acknowledged:    'Acknowledged',
    dismiss:         'Dismiss',
    no_alerts:       'No active alerts',
    every:           'every',
    min:             'min',
    error:           'ERROR',
    warning:         'WARNING',
    info:            'INFO',
    success:         'SUCCESS'
  },
  de: {
    acknowledge:     'Bestätigen',
    acknowledged:    'Bestätigt',
    dismiss:         'Schließen',
    no_alerts:       'Keine aktiven Meldungen',
    every:           'alle',
    min:             'min',
    error:           'FEHLER',
    warning:         'WARNUNG',
    info:            'INFO',
    success:         'ERFOLG'
  },
  fr: {
    acknowledge:     'Confirmer',
    acknowledged:    'Confirmé',
    dismiss:         'Fermer',
    no_alerts:       'Aucune alerte active',
    every:           'toutes les',
    min:             'min',
    error:           'ERREUR',
    warning:         'AVERTISSEMENT',
    info:            'INFO',
    success:         'SUCCÈS'
  },
  es: {
    acknowledge:     'Confirmar',
    acknowledged:    'Confirmado',
    dismiss:         'Cerrar',
    no_alerts:       'No hay alertas activas',
    every:           'cada',
    min:             'min',
    error:           'ERROR',
    warning:         'ADVERTENCIA',
    info:            'INFO',
    success:         'ÉXITO'
  },
  pt: {
    acknowledge:     'Confirmar',
    acknowledged:    'Confirmado',
    dismiss:         'Fechar',
    no_alerts:       'Sem alertas ativos',
    every:           'cada',
    min:             'min',
    error:           'ERRO',
    warning:         'AVISO',
    info:            'INFO',
    success:         'SUCESSO'
  },
  it: {
    acknowledge:     'Conferma',
    acknowledged:    'Confermato',
    dismiss:         'Chiudi',
    no_alerts:       'Nessun avviso attivo',
    every:           'ogni',
    min:             'min',
    error:           'ERRORE',
    warning:         'AVVISO',
    info:            'INFO',
    success:         'SUCCESSO'
  },
  pl: {
    acknowledge:     'Potwierdź',
    acknowledged:    'Potwierdzone',
    dismiss:         'Zamknij',
    no_alerts:       'Brak aktywnych alertów',
    every:           'co',
    min:             'min',
    error:           'BŁĄD',
    warning:         'OSTRZEŻENIE',
    info:            'INFO',
    success:         'SUKCES'
  }
};

function haGetT(lang) {
  if (!lang) return HA_ALERT_TRANSLATIONS.en;
  var code = lang.toLowerCase().split('-')[0];
  return HA_ALERT_TRANSLATIONS[code] || HA_ALERT_TRANSLATIONS.en;
}

function haFormatTime(iso) {
  if (!iso) return '';
  try {
    var d = new Date(iso);
    var dd = ('0' + d.getDate()).slice(-2);
    var mm = ('0' + (d.getMonth() + 1)).slice(-2);
    var yy = d.getFullYear();
    var hh = ('0' + d.getHours()).slice(-2);
    var mi = ('0' + d.getMinutes()).slice(-2);
    var ss = ('0' + d.getSeconds()).slice(-2);
    return dd + '-' + mm + '-' + yy + ' ' + hh + ':' + mi + ':' + ss;
  } catch(e) { return iso; }
}

function haBuildAlert(alert, isAcked, t) {
  var repeatMin = alert.repeat_interval ? Math.round(alert.repeat_interval / 60) : 0;
  var repeat = alert.repeat_interval ? '<span class="badge badge--repeat">&#128257; ' + t.every + ' ' + repeatMin + t.min + '</span>' : '';
  var cond   = alert.condition_entity ? '<span class="badge badge--condition">&#9889; auto-dismiss</span>' : '';
  var ttl    = alert.title ? '<span class="alert-title">' + alert.title + '</span>' : '';
  var ackCls = isAcked ? 'btn-ack btn-ack--done' : 'btn-ack';
  var ackLbl = isAcked ? '&#10003; ' + t.acknowledged : '&#128065; ' + t.acknowledge;
  var dis    = isAcked ? 'disabled="disabled"' : '';
  var typeLabel = t[alert.type] || alert.type.toUpperCase();
  var colors = {
    error:   { bg: 'rgba(239,68,68,0.13)',  border: '#ef4444', icon: '&#10060;', tagBg: 'rgba(239,68,68,0.22)',  tagColor: '#f87171' },
    warning: { bg: 'rgba(245,158,11,0.13)', border: '#f59e0b', icon: '&#9888;',  tagBg: 'rgba(245,158,11,0.22)', tagColor: '#fbbf24' },
    info:    { bg: 'rgba(59,130,246,0.13)', border: '#3b82f6', icon: '&#8505;',  tagBg: 'rgba(59,130,246,0.22)', tagColor: '#7fb3ff' },
    success: { bg: 'rgba(34,197,94,0.13)',  border: '#22c55e', icon: '&#10003;', tagBg: 'rgba(34,197,94,0.22)',  tagColor: '#4ade80' }
  };
  var c = colors[alert.type] || colors.info;
  var h = '';
  h += '<div class="alert-item" style="background:' + c.bg + ';border-left-color:' + c.border + ';" data-id="' + alert.id + '">';
  h +=   '<div class="alert-header">';
  h +=     '<span class="alert-icon">' + c.icon + '</span>';
  h +=     '<div class="alert-meta">';
  h +=       '<div class="title-row">' + ttl + '<span class="alert-time">' + haFormatTime(alert.created_at) + '</span></div>';
  h +=       '<div class="tags-row"><span class="alert-type-label" style="background:' + c.tagBg + ';color:' + c.tagColor + '">' + typeLabel + '</span>' + repeat + cond + '</div>';
  h +=     '</div>';
  h +=   '</div>';
  h +=   '<div class="alert-message">' + alert.message + '</div>';
  h +=   '<div class="alert-actions">';
  h +=     '<button class="' + ackCls + '" data-id="' + alert.id + '" ' + dis + '><span class="btn-label">' + ackLbl + '</span></button>';
  h +=     '<button class="btn-dismiss" data-id="' + alert.id + '"><span class="btn-label">&#10005; ' + t.dismiss + '</span></button>';
  h +=   '</div>';
  h += '</div>';
  return h;
}

function HAAlertCard() {
  var instance = HTMLElement.call(this) || this;
  instance._haConfig = {};
  instance._haHass = null;
  instance._haAcked = {};
  return instance;
}

HAAlertCard.prototype = Object.create(HTMLElement.prototype);
HAAlertCard.prototype.constructor = HAAlertCard;

HAAlertCard.prototype.connectedCallback = function() {
  if (!this.shadowRoot) {
    this.attachShadow({ mode: 'open' });
  }
};

HAAlertCard.prototype.setConfig = function(config) {
  if (!config.entity) throw new Error('Please provide an "entity".');
  this._haConfig = config;
  if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
  this._haRender();
};

HAAlertCard.prototype.getCardSize = function() { return 3; };

HAAlertCard.prototype._haCallService = function(service, data) {
  if (this._haHass) this._haHass.callService('ha_alert', service, data);
};

HAAlertCard.prototype._haRender = function() {
  if (!this._haHass || !this._haConfig || !this.shadowRoot) return;

  var lang = (this._haHass.language || this._haHass.locale && this._haHass.locale.language || 'en');
  var t = haGetT(lang);

  var stateObj = this._haHass.states[this._haConfig.entity];
  var title = this._haConfig.title || 'Active Alerts';
  var alerts = [];
  if (stateObj && stateObj.attributes && stateObj.attributes.alerts) {
    alerts = stateObj.attributes.alerts;
  }

  var self = this;
  var ids = {};
  var i, a;
  for (i = 0; i < alerts.length; i++) { ids[alerts[i].id] = true; }
  for (var kid in this._haAcked) {
    if (!ids[kid]) delete this._haAcked[kid];
  }

  var body = '';
  if (alerts.length === 0) {
    body = '<div class="no-alerts"><div class="no-alerts-icon">&#128276;</div><p>' + t.no_alerts + '</p></div>';
  } else {
    for (i = 0; i < alerts.length; i++) {
      a = alerts[i];
      body += haBuildAlert(a, a.acknowledged || !!self._haAcked[a.id], t);
    }
  }

  var badgeCls = alerts.length === 0 ? 'count-badge count-badge--zero' : 'count-badge';

  var css =
    ':host{display:block;font-family:var(--primary-font-family,Roboto,sans-serif)}' +
    'ha-card{padding:16px;box-sizing:border-box}' +
    '.card-header{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:space-between;justify-content:space-between;margin-bottom:12px}' +
    '.card-title{font-size:1.1rem;font-weight:600;color:var(--primary-text-color,#e8eaf2);display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;gap:8px}' +
    '.count-badge{background:var(--accent-color,#f59e0b);color:white;border-radius:20px;padding:3px 10px;font-size:.8rem;font-weight:700;min-width:24px;text-align:center}' +
    '.count-badge--zero{background:#4b5563}' +
    '.no-alerts{display:-webkit-flex;display:flex;-webkit-flex-direction:column;flex-direction:column;-webkit-align-items:center;align-items:center;padding:24px 0;color:var(--secondary-text-color,#9ca3af);gap:8px}' +
    '.no-alerts-icon{font-size:2rem;opacity:.5}' +
    '.no-alerts p{margin:0;font-size:.9rem}' +
    '.alert-item{border-left:4px solid;border-radius:10px;padding:12px 14px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,.25)}' +
    '.alert-item:last-child{margin-bottom:0}' +
    '.alert-header{display:-webkit-flex;display:flex;-webkit-align-items:flex-start;align-items:flex-start;gap:8px;margin-bottom:6px}' +
    '.alert-icon{font-size:1.1rem;-webkit-flex-shrink:0;flex-shrink:0;height:1.33rem;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center}' +
    '.alert-meta{-webkit-flex:1;flex:1;display:-webkit-flex;display:flex;-webkit-flex-direction:column;flex-direction:column;gap:3px;min-width:0}' +
    '.title-row{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:space-between;justify-content:space-between;gap:8px}' +
    '.alert-title{font-weight:700;font-size:.95rem;color:var(--primary-text-color,#e8eaf2)}' +
    '.alert-time{font-size:.72rem;color:var(--secondary-text-color,#9ca3af);-webkit-flex-shrink:0;flex-shrink:0;white-space:nowrap;margin-left:auto}' +
    '.tags-row{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;gap:5px;-webkit-flex-wrap:nowrap;flex-wrap:nowrap}' +
    '.alert-type-label{display:-webkit-inline-flex;display:inline-flex;-webkit-align-items:center;align-items:center;font-size:.7rem;font-weight:700;letter-spacing:.8px;padding:2px 7px;border-radius:4px;white-space:nowrap;border:1px solid transparent}' +
    '.alert-message{font-size:.88rem;color:var(--secondary-text-color,#c5cad8);line-height:1.5;margin-left:26px}' +
    '.badge{display:-webkit-inline-flex;display:inline-flex;-webkit-align-items:center;align-items:center;font-size:.7rem;padding:2px 7px;border-radius:4px;font-weight:500;white-space:nowrap}' +
    '.badge--repeat{background:rgba(59,130,246,.2);color:#93c5fd;border:1px solid rgba(59,130,246,.3)}' +
    '.badge--condition{background:rgba(167,139,250,.2);color:#c4b5fd;border:1px solid rgba(167,139,250,.3)}' +
    '.alert-actions{display:-webkit-flex;display:flex;gap:8px;margin-top:10px;margin-left:26px}' +
    'button{border:none;border-radius:8px;padding:6px 14px;font-size:.8rem;font-weight:600;cursor:pointer;position:relative;overflow:hidden;min-width:110px;text-align:center;-webkit-user-select:none;user-select:none}' +
    'button::before{content:"";position:absolute;border-radius:50%;background:rgba(255,255,255,.4);width:0;height:0;top:50%;left:50%;-webkit-transform:translate(-50%,-50%);transform:translate(-50%,-50%);pointer-events:none}' +
    'button.ripple-active::before{-webkit-animation:ripple .45s ease-out forwards;animation:ripple .45s ease-out forwards}' +
    '@-webkit-keyframes ripple{0%{width:0;height:0;opacity:.6}100%{width:220px;height:220px;opacity:0}}' +
    '@keyframes ripple{0%{width:0;height:0;opacity:.6}100%{width:220px;height:220px;opacity:0}}' +
    '.btn-label{position:relative;pointer-events:none}' +
    '.btn-ack{background:#2563eb;color:white}' +
    '.btn-ack--done{background:#374151;color:#6b7280;cursor:default}' +
    '.btn-dismiss{background:#dc2626;color:white;min-width:90px}';

  this.shadowRoot.innerHTML =
    '<style>' + css + '</style>' +
    '<ha-card>' +
      '<div class="card-header">' +
        '<div class="card-title">&#128276; ' + title + '</div>' +
        '<span class="' + badgeCls + '">' + alerts.length + '</span>' +
      '</div>' +
      '<div class="alerts-container">' + body + '</div>' +
    '</ha-card>';

  var container = this.shadowRoot.querySelector('.alerts-container');
  if (!container) return;

  container.addEventListener('click', function(e) {
    var target = e.target || e.srcElement;
    var btn = null;
    while (target && target !== container) {
      if (target.tagName === 'BUTTON') { btn = target; break; }
      target = target.parentNode;
    }
    if (!btn || btn.disabled) return;

    var alertId = btn.getAttribute('data-id');
    if (!alertId) return;

    btn.classList.remove('ripple-active');
    var dummy = btn.offsetWidth;
    btn.classList.add('ripple-active');

    function onEnd() {
      btn.removeEventListener('animationend', onEnd);
      btn.removeEventListener('webkitAnimationEnd', onEnd);
      btn.classList.remove('ripple-active');
    }
    btn.addEventListener('animationend', onEnd);
    btn.addEventListener('webkitAnimationEnd', onEnd);

    var curLang = (self._haHass.language || self._haHass.locale && self._haHass.locale.language || 'en');
    var curT = haGetT(curLang);

    if (btn.className.indexOf('btn-dismiss') !== -1) {
      self._haCallService('dismiss', { alert_id: alertId });
    } else if (btn.className.indexOf('btn-ack') !== -1) {
      self._haAcked[alertId] = true;
      self._haCallService('acknowledge', { alert_id: alertId });
      var lbl = btn.querySelector('.btn-label');
      if (lbl) lbl.textContent = '\u2713 ' + curT.acknowledged;
      btn.className = 'btn-ack btn-ack--done';
      btn.disabled = true;
    }
  });
};

HAAlertCard.getConfigElement = function() { return document.createElement('ha-alert-card-editor'); };
HAAlertCard.getStubConfig = function() { return { entity: 'sensor.ha_alert_active_alerts', title: 'Active Alerts' }; };

Object.defineProperty(HAAlertCard.prototype, 'hass', {
  set: function(hass) {
    this._haHass = hass;
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
    this._haRender();
  }
});

// --- Editor ---
function HAAlertCardEditor() {
  var instance = HTMLElement.call(this) || this;
  instance._edConfig = {};
  return instance;
}
HAAlertCardEditor.prototype = Object.create(HTMLElement.prototype);
HAAlertCardEditor.prototype.constructor = HAAlertCardEditor;

HAAlertCardEditor.prototype.setConfig = function(config) {
  this._edConfig = config;
  if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
  this._edRender();
};

Object.defineProperty(HAAlertCardEditor.prototype, 'hass', {
  set: function(h) { this._edHass = h; }
});

HAAlertCardEditor.prototype._edRender = function() {
  if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
  var self = this;
  this.shadowRoot.innerHTML =
    '<style>.row{display:flex;flex-direction:column;gap:4px;margin-bottom:12px}label{font-size:.85rem;font-weight:500;color:var(--primary-text-color)}input{padding:8px;border:1px solid var(--divider-color,#374151);border-radius:4px;font-size:.9rem;width:100%;box-sizing:border-box;background:var(--card-background-color);color:var(--primary-text-color)}</style>' +
    '<div>' +
      '<div class="row"><label>Entity</label><input id="entity" placeholder="sensor.ha_alert_active_alerts" value="' + (this._edConfig.entity || '') + '"></div>' +
      '<div class="row"><label>Title</label><input id="title" placeholder="Active Alerts" value="' + (this._edConfig.title || '') + '"></div>' +
    '</div>';

  var inputs = this.shadowRoot.querySelectorAll('input');
  for (var i = 0; i < inputs.length; i++) {
    (function(inp) {
      inp.configKey = inp.id;
      inp.addEventListener('change', function() {
        var cfg = {};
        for (var k in self._edConfig) cfg[k] = self._edConfig[k];
        cfg[inp.configKey] = inp.value;
        self.dispatchEvent(new CustomEvent('config-changed', { detail: { config: cfg } }));
      });
    })(inputs[i]);
  }
};

customElements.define('ha-alert-card', HAAlertCard);
customElements.define('ha-alert-card-editor', HAAlertCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({ type: 'ha-alert-card', name: 'HA Alert Card', description: 'Displays active HA Alert notifications.', preview: true });
console.info('%c HA-ALERT-CARD %c v1.2.5 ', 'color:white;background:#3b82f6;font-weight:700;padding:2px 6px;', 'color:#3b82f6;background:rgba(59,130,246,.15);font-weight:700;padding:2px 6px;');
