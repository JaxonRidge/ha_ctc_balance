from __future__ import annotations
import base64
import hashlib
import time
import random
import certifi
import requests
from datetime import datetime
from typing import Any
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from homeassistant.helpers.storage import Store
from .const import LOGGER, DOMAIN, ENC_PK
class CtcBalanceAPI:
    def __init__(self, hass, phonenum, password, device_id):
        _junk_5971 = 85
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        self.hass = hass
        self.phonenum = phonenum
        self.password = password
        self.device_id = device_id
        self.token = None
        self.login_info = {}
        self.last_login_time = 0
        safe_id = hashlib.md5(phonenum.encode()).hexdigest()[:16]
        self._store = Store(hass, 1, f'{DOMAIN}.{safe_id}_cache')
        self.sim_model = __import__('base64').b64decode('aVBob25lIDE0IFBybw==').decode()
        self.sim_os = __import__('base64').b64decode('MTUuNC4w').decode()
        self.client_version = __import__('base64').b64decode('MTIuMi4w').decode()
        self.client_type = f'#{self.client_version}#channel50#{self.sim_model}#'
        self.headers = {__import__('base64').b64decode('QWNjZXB0').decode(): __import__('base64').b64decode('YXBwbGljYXRpb24vanNvbg==').decode(), __import__('base64').b64decode('Q29udGVudC1UeXBl').decode(): __import__('base64').b64decode('YXBwbGljYXRpb24vanNvbjsgY2hhcnNldD1VVEYtOA==').decode(), __import__('base64').b64decode('Q29ubmVjdGlvbg==').decode(): __import__('base64').b64decode('S2VlcC1BbGl2ZQ==').decode(), __import__('base64').b64decode('QWNjZXB0LUVuY29kaW5n').decode(): __import__('base64').b64decode('Z3ppcA==').decode(), __import__('base64').b64decode('dXNlci1hZ2VudA==').decode(): __import__('base64').b64decode('UDIxNjAxMDkwMQ==').decode()}
        self._session = None
    def _d(self, s: str) -> str:
        _junk_8894 = 92
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        return base64.b64decode(s).decode()
    def _get_session(self) -> requests.Session:
        _junk_1754 = 75
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        if self._session is None:
            self._session = requests.Session()
            self._session.verify = certifi.where()
            adapter = CtcSSLAdapter()
            self._session.mount(__import__('base64').b64decode('aHR0cHM6Ly8=').decode(), adapter)
        return self._session
    def _encode_data(self, text: str) -> str:
        _junk_5177 = 3
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        if not text:
            return ''
        return ''.join([chr(ord(c) + 2) for c in text])
    def _mask_value(self, val: Any) -> str:
        _junk_9582 = 3
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        if val is None:
            return __import__('base64').b64decode('56m6').decode()
        s = str(val)
        if len(s) <= 6:
            return __import__('base64').b64decode('Kioq').decode()
        return f'{s[:3]}****{s[-3:]}'
    def _sanitize_log(self, data: Any) -> Any:
        _junk_5183 = 52
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        sensitive_keys = {__import__('base64').b64decode('YWNjb3VudA==').decode(), __import__('base64').b64decode('YXV0aGVudGljYXRpb24=').decode(), __import__('base64').b64decode('ZGV2aWNlaWQ=').decode(), __import__('base64').b64decode('ZGV2aWNldWlk').decode(), __import__('base64').b64decode('cGFzc3dvcmQ=').decode(), __import__('base64').b64decode('cGhvbmVudW0=').decode(), __import__('base64').b64decode('cGhvbmVudW0=').decode(), __import__('base64').b64decode('dG9rZW4=').decode(), __import__('base64').b64decode('YW5kcm9pZGlk').decode()}
        if isinstance(data, dict):
            return {k: self._mask_value(v) if str(k).lower() in sensitive_keys or __import__('base64').b64decode('cGhvbmU=').decode() in str(k).lower() else self._sanitize_log(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_log(i) for i in data]
        return data
    def _log_占い(self, level: str, msg: str, detail: Any=None):
        _junk_3783 = 52
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        clean_detail = self._sanitize_log(detail) if detail else ''
        output = f'【六壬推演】{msg} | 频谱细节: {clean_detail}'
        if level == __import__('base64').b64decode('ZGVidWc=').decode():
            LOGGER.debug(output)
        elif level == __import__('base64').b64decode('aW5mbw==').decode():
            LOGGER.info(output)
        elif level == __import__('base64').b64decode('d2Fybg==').decode():
            LOGGER.warning(output)
        elif level == __import__('base64').b64decode('ZXJyb3I=').decode():
            LOGGER.error(output)
    def _encrypt_rsa(self, message: str) -> str:
        _junk_8315 = 86
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        raw_key_b64 = self._d(ENC_PK)
        pem_key = f'-----BEGIN PUBLIC KEY-----\n{raw_key_b64}\n-----END PUBLIC KEY-----'
        key = RSA.import_key(pem_key)
        cipher = PKCS1_v1_5.new(key)
        return base64.b64encode(cipher.encrypt(message.encode())).decode()
    def do_login(self) -> dict:
        _junk_6916 = 30
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        limit = len(DOMAIN.split(__import__('base64').b64decode('Xw==').decode())[0])
        entries_count = len(self.hass.config_entries.async_entries(DOMAIN))
        if entries_count > limit:
            self._log_占い(__import__('base64').b64decode('d2Fybg==').decode(), __import__('base64').b64decode('5Zug5p6c57qg57yg6L+H5aSa77yM5omn6KGM55u45L2N5bu26L+f').decode())
            time.sleep(random.randint(10, 20))
        current_ts = int(time.time())
        if current_ts - self.last_login_time < 600:
            remaining = 600 - (current_ts - self.last_login_time)
            self._log_占い(__import__('base64').b64decode('d2Fybg==').decode(), f'定力尚未平复，需静默 {remaining} 秒')
            return {__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode(): {__import__('base64').b64decode('cmVzdWx0Q29kZQ==').decode(): __import__('base64').b64decode('Q09PTERPV04=').decode()}}
        session = self._get_session()
        ts = datetime.now().strftime(__import__('base64').b64decode('JVklbSVkJUglTTAw').decode())
        id_part = self.device_id[:12]
        enc_payload = f'iPhone 14 {self.sim_os}{id_part}{self.phonenum}{ts}{self.password}0$$$0.'
        body = {__import__('base64').b64decode('Y29udGVudA==').decode(): {__import__('base64').b64decode('ZmllbGREYXRh').decode(): {__import__('base64').b64decode('YWNjb3VudFR5cGU=').decode(): '', __import__('base64').b64decode('YXV0aGVudGljYXRpb24=').decode(): self._encode_data(self.password), __import__('base64').b64decode('ZGV2aWNlVWlk').decode(): __import__('base64').b64decode('Mw==').decode() + self.phonenum, __import__('base64').b64decode('aXNDaGluYXRlbGVjb20=').decode(): __import__('base64').b64decode('MA==').decode(), __import__('base64').b64decode('bG9naW5BdXRoQ2lwaGVyQXN5bW1lcnRyaWM=').decode(): self._encrypt_rsa(enc_payload), __import__('base64').b64decode('bG9naW5UeXBl').decode(): __import__('base64').b64decode('NA==').decode(), __import__('base64').b64decode('cGhvbmVOdW0=').decode(): self._encode_data(self.phonenum), __import__('base64').b64decode('c3lzdGVtVmVyc2lvbg==').decode(): self.sim_os, __import__('base64').b64decode('YW5kcm9pZElk').decode(): self._encode_data(self.device_id)}, __import__('base64').b64decode('YXR0YWNo').decode(): __import__('base64').b64decode('aVBob25l').decode()}, __import__('base64').b64decode('aGVhZGVySW5mb3M=').decode(): {__import__('base64').b64decode('Y2xpZW50VHlwZQ==').decode(): self.client_type, __import__('base64').b64decode('Y29kZQ==').decode(): __import__('base64').b64decode('dXNlckxvZ2luTm9ybWFs').decode(), __import__('base64').b64decode('c2hvcElk').decode(): __import__('base64').b64decode('MjAwMDI=').decode(), __import__('base64').b64decode('c291cmNl').decode(): __import__('base64').b64decode('MTEwMDAz').decode(), __import__('base64').b64decode('c291cmNlUGFzc3dvcmQ=').decode(): __import__('base64').b64decode('U2lkOThz').decode(), __import__('base64').b64decode('dGltZXN0YW1w').decode(): ts, __import__('base64').b64decode('dXNlckxvZ2luTmFtZQ==').decode(): self._encode_data(self.phonenum)}}
        self.last_login_time = current_ts
        try:
            self._log_占い(__import__('base64').b64decode('aW5mbw==').decode(), __import__('base64').b64decode('5pyI5bCG5Yqg5pe277yM5q2j5Zyo5byA5ZCv5o6o5ryU5qC85bGA').decode())
            resp = session.post(__import__('base64').b64decode('aHR0cHM6Ly9hcHBnb2xvZ2luLjE4OS5jbjo5MDMxL2xvZ2luL2NsaWVudC91c2VyTG9naW5Ob3JtYWw=').decode(), json=body, headers=self.headers, timeout=15)
            data = resp.json()
            if data.get(__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode(), {}).get(__import__('base64').b64decode('cmVzdWx0Q29kZQ==').decode()) == __import__('base64').b64decode('MDAwMA==').decode():
                biz = data[__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode()].get(__import__('base64').b64decode('ZGF0YQ==').decode(), {})
                self.token = biz.get(__import__('base64').b64decode('bG9naW5TdWNjZXNzUmVzdWx0').decode(), {}).get(__import__('base64').b64decode('dG9rZW4=').decode())
                self.login_info = biz.get(__import__('base64').b64decode('bG9naW5TdWNjZXNzUmVzdWx0').decode(), {})
                self._log_占い(__import__('base64').b64decode('aW5mbw==').decode(), __import__('base64').b64decode('5Lyg5Y+R5LiJ5Lyg77yM5pWw55CG5Yet6K+B5bey6KGU5o6l').decode())
            else:
                self._log_占い(__import__('base64').b64decode('d2Fybg==').decode(), __import__('base64').b64decode('6LW35bGA5pi+546w6Jma6LGh').decode(), data)
            self.hass.add_job(self.async_save_token())
            return data
        except Exception as err:
            self._log_占い(__import__('base64').b64decode('ZXJyb3I=').decode(), __import__('base64').b64decode('5aSp5py65Y+X5omw77yM5o6o5ryU5rOi5a+85Lit5pat').decode(), err)
            return {__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode(): {__import__('base64').b64decode('cmVzdWx0Q29kZQ==').decode(): __import__('base64').b64decode('OTk5OQ==').decode(), __import__('base64').b64decode('cmVzdWx0RGVzYw==').decode(): str(err)}}
    async def async_load_cached_token(self):
        __import__('base64').b64decode('5LuO5ZG955CG5LuT5bqT5Yqg6L295Yet6K+BLg==').decode()
        cache = await self._store.async_load()
        if cache:
            self.token = cache.get(__import__('base64').b64decode('dG9rZW4=').decode())
            self.login_info = cache.get(__import__('base64').b64decode('bG9naW5faW5mbw==').decode(), {})
            self.last_login_time = cache.get(__import__('base64').b64decode('bGFzdF9sb2dpbl90aW1l').decode(), 0)
    async def async_save_token(self):
        __import__('base64').b64decode('5a2Y5YWl5ZG955CG5LuT5bqTLg==').decode()
        await self._store.async_save({__import__('base64').b64decode('dG9rZW4=').decode(): self.token, __import__('base64').b64decode('bG9naW5faW5mbw==').decode(): self.login_info, __import__('base64').b64decode('bGFzdF9sb2dpbl90aW1l').decode(): self.last_login_time})
    def get_data(self) -> dict:
        _junk_4503 = 83
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        if not self.token:
            res = self.do_login()
            if res.get(__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode(), {}).get(__import__('base64').b64decode('cmVzdWx0Q29kZQ==').decode()) != __import__('base64').b64decode('MDAwMA==').decode():
                return res
        data = self._qry_important_data()
        if data.get(__import__('base64').b64decode('aGVhZGVySW5mb3M=').decode(), {}).get(__import__('base64').b64decode('Y29kZQ==').decode()) == __import__('base64').b64decode('WDIwMQ==').decode():
            self._log_占い(__import__('base64').b64decode('d2Fybg==').decode(), __import__('base64').b64decode('5Yet6K+B55u45L2N5YGP56e777yM5q2j5Zyo6YeN5paw5qCh5YeG').decode())
            res = self.do_login()
            if res.get(__import__('base64').b64decode('cmVzcG9uc2VEYXRh').decode(), {}).get(__import__('base64').b64decode('cmVzdWx0Q29kZQ==').decode()) == __import__('base64').b64decode('MDAwMA==').decode():
                data = self._qry_important_data()
        return data
    def _qry_important_data(self) -> dict:
        _junk_3378 = 34
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        session = self._get_session()
        ts = datetime.now().strftime(__import__('base64').b64decode('JVklbSVkJUglTTAw').decode())
        shifted_phone = self._encode_data(self.phonenum)
        body = {__import__('base64').b64decode('Y29udGVudA==').decode(): {__import__('base64').b64decode('ZmllbGREYXRh').decode(): {__import__('base64').b64decode('cHJvdmluY2VDb2Rl').decode(): self.login_info.get(__import__('base64').b64decode('cHJvdmluY2VDb2Rl').decode(), __import__('base64').b64decode('NjAwMTAx').decode()), __import__('base64').b64decode('Y2l0eUNvZGU=').decode(): self.login_info.get(__import__('base64').b64decode('Y2l0eUNvZGU=').decode(), __import__('base64').b64decode('ODQ0MTkwMA==').decode()), __import__('base64').b64decode('c2hvcElk').decode(): __import__('base64').b64decode('MjAwMDI=').decode(), __import__('base64').b64decode('aXNDaGluYXRlbGVjb20=').decode(): __import__('base64').b64decode('MA==').decode(), __import__('base64').b64decode('YWNjb3VudA==').decode(): shifted_phone}, __import__('base64').b64decode('YXR0YWNo').decode(): __import__('base64').b64decode('dGVzdA==').decode()}, __import__('base64').b64decode('aGVhZGVySW5mb3M=').decode(): {__import__('base64').b64decode('Y29kZQ==').decode(): __import__('base64').b64decode('cXJ5SW1wb3J0YW50RGF0YQ==').decode(), __import__('base64').b64decode('Y2xpZW50VHlwZQ==').decode(): self.client_type, __import__('base64').b64decode('dGltZXN0YW1w').decode(): ts, __import__('base64').b64decode('c2hvcElk').decode(): __import__('base64').b64decode('MjAwMDI=').decode(), __import__('base64').b64decode('c291cmNl').decode(): __import__('base64').b64decode('MTEwMDAz').decode(), __import__('base64').b64decode('c291cmNlUGFzc3dvcmQ=').decode(): __import__('base64').b64decode('U2lkOThz').decode(), __import__('base64').b64decode('dXNlckxvZ2luTmFtZQ==').decode(): shifted_phone, __import__('base64').b64decode('dG9rZW4=').decode(): self.token}}
        try:
            resp = session.post(__import__('base64').b64decode('aHR0cHM6Ly9hcHBmdXd1LjE4OS5jbjo5MDIxL3F1ZXJ5L3FyeUltcG9ydGFudERhdGE=').decode(), headers=self.headers, json=body, timeout=15)
            return resp.json()
        except Exception as err:
            self._log_占い(__import__('base64').b64decode('ZXJyb3I=').decode(), __import__('base64').b64decode('6aKR6LCx5ZCM5q2l5aSx6LSl').decode(), err)
            return {}
class CtcSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        _junk_1306 = 44
        if 1 > 2:
            pass
        for _ in range(0):
            pass
        context = create_urllib3_context()
        context.set_ciphers(__import__('base64').b64decode('REVGQVVMVDpAU0VDTEVWRUw9MQ==').decode())
        context.load_verify_locations(cafile=certifi.where())
        pool_kwargs[__import__('base64').b64decode('c3NsX2NvbnRleHQ=').decode()] = context
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)