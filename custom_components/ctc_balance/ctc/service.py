"""CTC 业务层：query* 接口族查询、旧版 XML 网关与客户端组装。"""
from __future__ import annotations

import re
import time
from .const import (
    CLIENT_VERSION,
    DEC,
    ENC,
    SHOP_ID,
    SOURCE,
    SOURCE_PASSWORD,
    UA,
    XML_URLS,
    CarrierAuthExpiredError,
    des3_encrypt_hex,
)
from .auth import AuthMixin
from .transport import LiuRenClientBase
from ..const import CACHE_SCHEMA, LOGGER

mask = lambda p: p[:3] + "****" + p[-4:] if len(p) == 11 else p

def _to_int(value, default: int = 0) -> int:
    """从可能带单位的字符串中提取整数（如 "100分钟" → 100、"1.5GB" → 1）。"""
    if value is None:
        return default
    # 先去除千分位逗号，避免 "1,234" 被截断为 1
    m = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    if not m:
        return default
    try:
        return int(float(m.group()))
    except (ValueError, OverflowError):
        return default

def _strip_unit(value, default: str = "0.00") -> str:
    """剥离字符串中的单位与千分位，只保留数值文本（单位由组装层统一添加）。"""
    if value is None:
        return default
    m = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return m.group() if m else default

class ServiceMixin:
    """业务查询混入。"""

    def _fetch_balance(self) -> dict:
        """业务块 1：话费余额、本月消费与近半年账单（queryPhoneBillBalance）。"""
        out = {}
        try:
            fd_bal = {
                "account": ENC(self.phone), "queryFlag": "1", "provinceCode": self.province_code,
                "cityCode": self.city_code, "shopId": "20004", "accessAuth": "0",
                "developCode": "", "isChinatelecom": "1", "netType": ""
            }
            _, res_bal = self._service_post("query/queryPhoneBillBalance", "queryPhoneBillBalance", fd_bal)
            bal_data = res_bal.get("data") or {}
            charge_bean = bal_data.get("chargeBean") or {}
            charge_title = str(charge_bean.get("chargeTitle") or "")
            voice_msg = str(bal_data.get("voiceMessage") or "")
            total_arrears = bal_data.get("totalArrears")
            # 欠费判据：只认上游的明确表述——文本含「欠费」或结构化欠费金额 > 0。
            is_arrears = (
                "欠费" in charge_title
                or "欠费" in voice_msg
                or (total_arrears is not None and float(total_arrears or 0) > 0)
            )
            # 余额提醒（与欠费无关）：上游把余额标红（isShowRed == "1"）表示余额偏低、
            warn_info = bal_data.get("balanceWarnInfo") or {}
            out["balance_warn"] = str(charge_bean.get("isShowRed") or "") == "1"
            out["balance_warn_tip"] = str(
                warn_info.get("tipDesc") or bal_data.get("outOfRemark") or ""
            ).strip()

            try:
                raw_charge = float(charge_bean.get("charge", 0.0))
            except Exception:
                raw_charge = 0.0

            if is_arrears:
                arr_amt = float(total_arrears) if (total_arrears and float(total_arrears or 0) > 0) else raw_charge
                out["balance"] = -abs(arr_amt)
                out["balance_title"] = charge_title or "当前欠费"
            else:
                out["balance"] = raw_charge
                out["balance_title"] = charge_title or "当前号码余额"

            out["balance_general"] = charge_bean.get("charge", "0.00")
            out["balance_special"] = "0.00"
            for cl in charge_bean.get("chargeList", []):
                if "专用" in cl.get("chargeListTitle", ""):
                    out["balance_special"] = _strip_unit(cl.get("chargeListCharge"))

            bill_exp = bal_data.get("billExpense") or {}
            val_list = bill_exp.get("valueList") or []
            try:
                out["charge"] = float(val_list[-1].get("amount", 0.0)) if val_list else 0.0
            except Exception:
                out["charge"] = 0.0

            history_bills = []
            for v in reversed(val_list):
                t_title = v.get("title", "")
                t_amt = v.get("amount", "")
                if t_title and t_amt:
                    history_bills.append({"title": t_title, "amount": t_amt})
            out["history_bills"] = history_bills
        except CarrierAuthExpiredError:
            raise
        except Exception as err:
            LOGGER.debug("拉取电话话费与消费异常: %s", err)
            out["balance"] = 0.0
            out["charge"] = 0.0
            out["history_bills"] = []
        return out

    def _fetch_integral(self) -> dict:
        """业务块 2：积分（queryIntegral）。"""
        out = {}
        try:
            fd_int = {"account": ENC(self.phone), "clientType": "1", "shopId": "20004"}
            _, res_int = self._service_post("query/queryIntegral", "queryIntegral", fd_int)
            int_data = res_int.get("data") or {}
            try:
                out["integral"] = int(int_data.get("integral", 0))
            except Exception:
                out["integral"] = 0
        except Exception as err:
            # 注意：与原实现一致，此处不透传 CarrierAuthExpiredError
            LOGGER.debug("拉取积分异常: %s", err)
            out["integral"] = 0
        return out

    def _fetch_flow(self) -> dict:
        """业务块 3：流量池与共享流量（userPackage + qryShareUsage）。"""
        out = {}
        ts_cycle = time.strftime("%Y%m")
        try:
            fd_pkg_flow = {
                "account": ENC(self.phone), "billingCycle": ts_cycle,
                "queryFlag": "0", "shopId": "20004", "clientType": "1"
            }
            _, res_pkg_flow = self._service_post("query/userPackage", "userPackage", fd_pkg_flow)
            flow_pkgs = ((res_pkg_flow.get("data") or {}).get("productOFFRatable")
                         or {}).get("ratableResourcePackages") or []

            u_kb_total = 0
            b_kb_total = 0
            flow_packages = []

            for fp in flow_pkgs:
                u_kb_total += int(fp.get("usageAmount") or 0)
                b_kb_total += int(fp.get("balanceAmount") or 0)
                for sub in fp.get("productInfos", []):
                    # 结构化判据（取自上游原始字段，不做名称匹配）：
                    #   ratableAmount == 0 → 无独立额度的基础/超出流量（只有已用，无总额）
                    #   transferAmount == "1" → 上月结转/转存流量
                    ratable_kb = int(sub.get("ratableAmount") or 0)
                    flow_packages.append({
                        "name": sub.get("productOFFName") or "流量包",
                        "remain_gb": round(int(sub.get("balanceAmount") or 0) / 1024 / 1024, 2),
                        "used_gb": round(int(sub.get("usageAmount") or 0) / 1024 / 1024, 2),
                        "total_gb": round(ratable_kb / 1024 / 1024, 2),
                        "has_quota": ratable_kb > 0,
                        "is_transfer": str(sub.get("transferAmount") or "0") == "1",
                    })

            out["flow_remain_gb"] = round(b_kb_total / 1024 / 1024, 2)
            out["flow_used_gb"] = round(u_kb_total / 1024 / 1024, 2)
            out["flow_total_gb"] = round((u_kb_total + b_kb_total) / 1024 / 1024, 2)
            out["flow_packages"] = flow_packages

            # 各成员已用流量明细（qryShareUsage）
            fd_share = {
                "account": ENC(self.phone), "billingCycle": ts_cycle,
                "queryFlag": "1", "shopId": "20004", "clientType": "1"
            }
            _, res_share = self._service_post("query/qryShareUsage", "qryShareUsage", fd_share)
            share_data = res_share.get("data") or {}
            self._share_data = share_data

            member_flow = {}
            for item in share_data.get("shareTypeBeans", []):
                if item.get("shareType") == "流量":
                    for info in item.get("shareUsageInfos", []):
                        for m in info.get("shareUsageAmounts", []):
                            raw_p = DEC(m.get("phoneNum"))
                            kb = int(m.get("usageAmount", 0))
                            member_flow[raw_p] = member_flow.get(raw_p, 0) + kb

            flow_members = []
            ordered_flow_phones = [self.phone] + [p for p in member_flow if p != self.phone]
            for p in ordered_flow_phones:
                if p in member_flow:
                    flow_members.append({
                        "is_self": p == self.phone,
                        "phone": mask(p),
                        "used_gb": round(member_flow[p] / 1024 / 1024, 2),
                    })
            out["flow_members"] = flow_members
        except CarrierAuthExpiredError:
            raise
        except Exception as err:
            LOGGER.debug("拉取流量池异常: %s", err)
            self._share_data = {}
            out["flow_remain_gb"] = 0.0
            out["flow_used_gb"] = 0.0
            out["flow_total_gb"] = 0.0
            out["flow_packages"] = []
            out["flow_members"] = []
        return out

    def _fetch_voice_usage(self) -> dict:
        """业务块 4：共享通话用量与套餐信息（qryUserUsage + qryShareUsage）。"""
        out = {}
        try:
            fd_usage = {
                "account": ENC(self.phone), "queryFlag": "1", "clientType": "1",
                "cityCode": self.city_code, "provinceCode": self.province_code, "isChinatelecom": "1",
                "netType": "", "userId": self.user_id, "developCode": "", "isNewUser": "0",
                "phoneType": "0", "shopId": "20004", "isFromInternational": "0"
            }
            _, res_usage = self._service_post("query/qryUserUsage", "qryUserUsage", fd_usage)
            usage_data = res_usage.get("data") or {}
            out["package_name"] = (usage_data.get("productOFFInformation") or {}).get("content", "5G畅享套餐")

            packages = usage_data.get("ratableResourcePackages") or []
            v_rem, v_used, v_total = 0, 0, 0
            voice_packages = []
            if packages:
                pkg = packages[0]
                prog = pkg.get("usageProgress") or {}
                tot_d = pkg.get("totalData") or {}
                # 字段可能是带单位的文本（如 "100分钟"），统一健壮解析
                v_rem = _to_int(tot_d.get("totalValue"))
                v_used = _to_int(prog.get("leftBottomTitle"))
                v_total = _to_int(prog.get("rightBottomTitle"))
                for pinfo in pkg.get("productInfos", []):
                    voice_packages.append({
                        "title": pinfo.get("title", ""),
                        "used": pinfo.get("leftHighlight", ""),
                        "remain": pinfo.get("rightHighlight", ""),
                        "total": pinfo.get("rightCommon", "").replace("/", ""),
                    })

            out["voice_remain"] = v_rem
            out["voice_used"] = v_used
            out["voice_total"] = v_total
            out["voice_packages"] = voice_packages

            share_data = getattr(self, "_share_data", {}) or {}
            member_voice = {}
            for item in (share_data.get("shareTypeBeans") or []):
                if item.get("shareType") == "语音":
                    for info in item.get("shareUsageInfos", []):
                        for m in info.get("shareUsageAmounts", []):
                            raw_p = DEC(m.get("phoneNum"))
                            mins = int(m.get("usageAmount", 0))
                            member_voice[raw_p] = member_voice.get(raw_p, 0) + mins

            voice_members = []
            ordered_voice_phones = [self.phone] + [p for p in member_voice if p != self.phone]
            for p in ordered_voice_phones:
                if p in member_voice:
                    voice_members.append({
                        "is_self": p == self.phone,
                        "phone": mask(p),
                        "used_mins": member_voice[p],
                    })
            out["voice_members"] = voice_members
        except CarrierAuthExpiredError:
            raise
        except Exception as err:
            LOGGER.debug("拉取通话用量异常: %s", err)
            out["package_name"] = "5G畅享套餐"
            out["voice_remain"] = 0
            out["voice_used"] = 0
            out["voice_total"] = 0
            out["voice_packages"] = []
            out["voice_members"] = []
        return out

    def _fetch_broadband(self) -> dict:
        """业务块 5：宽带信息（queryMyBroadBand）。"""
        out = {}
        try:
            fd_bb = {
                "account": ENC(self.phone), "phoneNum": ENC(self.phone), "type": "1",
                "provinceCode": self.province_code, "cityCode": self.city_code,
                "shopId": "20004", "clientType": "1"
            }
            _, res_bb = self._service_post("query/queryMyBroadBand", "queryMyBroadBand", fd_bb)
            bb_list = (res_bb.get("data") or {}).get("queryMyBroadBandInfos") or []
            broadbands = []
            if bb_list:
                b0 = bb_list[0]
                broadbands.append({
                    "account": b0.get("serialNumber", ""),
                    "product_name": b0.get("productName", "宽带"),
                    "rate": b0.get("broadbandRate", "1000MB"),
                    "start_date": b0.get("startDate", ""),
                    "end_date": b0.get("endDate", ""),
                    "remaining_days": b0.get("remainingDays", 0),
                    "address": b0.get("address", ""),
                })
            out["broadbands"] = broadbands
        except Exception as err:
            # 此处不透传 CarrierAuthExpiredError
            LOGGER.debug("拉取宽带信息异常: %s", err)
            out["broadbands"] = []
        return out

    def _fetch_account(self) -> dict:
        """业务块 6：账户资产与网龄信用（queryAccountInfo）。"""
        out = {}
        try:
            fd_acc = {"account": ENC(self.phone), "phoneNum": ENC(self.phone),
                      "shopId": "20004", "clientType": "1"}
            _, res_acc = self._service_post("query/queryAccountInfo", "queryAccountInfo", fd_acc)
            acc_data = res_acc.get("data") or {}
            out["user_level"] = acc_data.get("starLevel", "普通用户")
            out["account_name"] = acc_data.get("accountName", "")
            out["credit_limit"] = (acc_data.get("phoneConfig") or {}).get("accountDetail", {}).get("creditAvailable", "0")
            vm = acc_data.get("voiceMessage", "")
            out["voice_message"] = vm
            # 从语音欢迎词中动态正则提取真实网龄（如: 您网龄为一十年六个月）
            m_age = re.search(r"网龄为([^，,。]+)", vm)
            out["open_years"] = m_age.group(1) if m_age else "在网用户"
            fixed_lines = []
            for item in (acc_data.get("fixedLineConfig") or {}).get("otherNumbers", []):
                if item.get("account"):
                    fixed_lines.append(item.get("account"))
            out["fixed_lines"] = fixed_lines
        except Exception as err:
            # 此处不透传 CarrierAuthExpiredError
            LOGGER.debug("拉取账户资产信息异常: %s", err)
            out["user_level"] = "普通用户"
            out["account_name"] = ""
            out["credit_limit"] = "0"
            out["fixed_lines"] = []
            out["open_years"] = "在网用户"
        return out

class XmlGatewayMixin:
    """XML 网关混入。"""

    def get_cust_info_xml(self) -> str:
        """调用旧版 XML 网关业务码 custInfo，获取机主姓名（Cust_Name）。"""
        if not self.token:
            return ""

        ts = time.strftime("%Y%m%d%H%M%S")
        enc_phone = ENC(self.phone)
        client_type = f"#{CLIENT_VERSION}#channel50#{self.device_model or 'iPhone'}#"
        xml_req = (
            f"<Request><HeaderInfos><Code>custInfo</Code>"
            f"<UserLoginName>{enc_phone}</UserLoginName>"
            f"<Token>{self.token}</Token>"
            f"<ClientType>{client_type}</ClientType>"
            f"<Timestamp>{ts}</Timestamp>"
            f"<ShopId>{SHOP_ID}</ShopId>"
            f"<Source>{SOURCE}</Source>"
            f"<SourcePassword>{SOURCE_PASSWORD}</SourcePassword>"
            f"<BroadAccount></BroadAccount>"
            f"<BroadToken></BroadToken>"
            f"<FixedLineAccount></FixedLineAccount>"
            f"<FixedLineToken></FixedLineToken>"
            f"<ProvinceCode>{self.province_code}</ProvinceCode>"
            f"</HeaderInfos>"
            f"<Content><Attach>iPhone</Attach>"
            f"<FieldData><PhoneNbr>{self.phone}</PhoneNbr><PhoneType>0</PhoneType></FieldData>"
            f"</Content></Request>"
        )

        try:
            encrypted = des3_encrypt_hex(xml_req)
            headers = {
                "Content-Type": "application/xml; charset=utf-8",
                "User-Agent": UA
            }

            for url in XML_URLS:
                try:
                    resp = self.s.post(url, data=encrypted.encode("utf-8"), headers=headers, timeout=10)
                    if resp.status_code == 200:
                        text = resp.text
                        if ("<Code>X201</Code>" in text or "token 过期" in text
                                or "token失效" in text or "<Code>X110</Code>" in text):
                            LOGGER.debug("XML 网关凭据已失效，转静默续期: %s", text[:200])
                            raise CarrierAuthExpiredError("推演凭据已失效 (网关报 token 过期)")
                        m = re.search(r"<Cust_Name>(.*?)</Cust_Name>", text)
                        if m:
                            name = m.group(1).strip()
                            if name:
                                LOGGER.debug("XML 网关返回机主姓名: %s", name)
                                return name
                except CarrierAuthExpiredError:
                    raise
                except Exception as ex:
                    LOGGER.debug("请求 XML 网关 %s 失败: %s", url, ex)
        except CarrierAuthExpiredError:
            raise
        except Exception as e:
            LOGGER.debug("调用 custInfo XML 异常: %s", e)
        return ""

class LiuRenClient(AuthMixin, ServiceMixin, XmlGatewayMixin, LiuRenClientBase):
    """iOS APP 同源协议客户端（短信/密码登录 + query* 业务接口族）。"""

    def fetch_all_data(self) -> dict:
        """拉取全量业务数据（各业务块独立容错，失效异常透传）。"""
        if not self.token:
            raise CarrierAuthExpiredError("占测凭据缺失，须重新起课认证")
        data_out = {}
        data_out.update(self._fetch_balance())
        data_out.update(self._fetch_integral())
        data_out.update(self._fetch_flow())
        data_out.update(self._fetch_voice_usage())
        data_out.update(self._fetch_broadband())
        data_out.update(self._fetch_account())
        try:
            cust_name = self.get_cust_info_xml()
            if cust_name:
                data_out["account_name"] = cust_name
        except CarrierAuthExpiredError:
            raise
        except Exception as err:
            LOGGER.debug("获取机主姓名(Cust_Name)异常: %s", err)

        data_out["location"] = f"{self.province_name} {self.city_name}".strip()
        data_out["_schema"] = CACHE_SCHEMA
        return data_out