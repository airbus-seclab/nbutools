from scapy import *
from scapy.packet import *
from scapy.fields import *

BprdSEP = " "
BPRD_CMD_IDS = {
    "0": "REREAD_CONFIG",
    "1": "ALIVE",
    "2": "LOGSTATUS",
    "3": "TERMINATE",
    "4": "VERBOSE",
    "5": "RECYCLE_LOGS",
    "6": "MASTER",
    "7": "BE_MASTER",
    "8": "SUICIDE",
    "9": "RECYCLE_JOBS",
    "10": "WAKEUP",
    "11": "USER_BPBACKUP_SYNC",
    "12": "BPBACKUP_SYNC",
    "13": "USER_BPARCHIVE_SYNC",
    "14": "BPRESTORE_SYNC",
    "15": "TIR_RESTORE_SYNC",
    "16": "UNUSED_16",
    "17": "UNUSED_17",
    "18": "UNUSED_18",
    "19": "USER_BPBACKUP",
    "20": "USER_BPARCHIVE",
    "21": "START_SCHED",
    "22": "SUNUSED4",
    "23": "BPBACKUP",
    "24": "BPRESTORE",
    "25": "BPLIST",
    "26": "IMAGE_LIST",
    "27": "LIKELY_DATE",
    "28": "USER_BPBACKUP_1_7",
    "29": "USER_BPARCHIVE_1_7",
    "30": "BPBACKUP_1_7",
    "31": "BPRESTORE_1_7",
    "32": "BPLIST_1_7",
    "33": "IMAGE_LIST_1_7",
    "34": "LIKELY_DATE_1_7",
    "35": "BPLIST_2_0",
    "36": "TIR_LIST",
    "37": "TIR_RESTORE",
    "38": "BPLIST_2_1",
    "39": "BPRESTORE_2_1",
    "40": "TIR_LIST_2_1",
    "41": "TIR_RESTORE_2_1",
    "42": "AUNUSED2",
    "43": "REMOTE_HOST_VERSION",
    "44": "VERSION",
    "45": "CLIENT_ID",
    "46": "DEL_IMAGE_BY_FILE",
    "47": "MEDIA_LIST_BY_FILE",
    "48": "SYNC",
    "49": "USER_BPBACKUP_SYNC_3_0",
    "50": "USER_BPARCHIVE_SYNC_3_0",
    "51": "BPBACKUP_SYNC_3_0",
    "52": "BPRESTORE_SYNC_3_0",
    "53": "USER_BPBACKUP_3_0",
    "54": "USER_BPARCHIVE_3_0",
    "55": "BPBACKUP_3_0",
    "56": "BPRESTORE_3_0",
    "57": "BPLIST_3_0",
    "58": "IMAGE_LIST_3_0",
    "59": "LIKELY_DATE_3_0",
    "60": "SET_DYNAMIC_CLIENT",
    "61": "BPRESTORE_SYNC_3_1",
    "62": "BPRESTORE_3_1",
    "63": "BPBACKUP_DB_3_2",
    "64": "BPBACKUP_DB_SYNC_3_2",
    "65": "BPRESTORE_SYNC_3_2",
    "66": "BPRESTORE_3_2",
    "67": "MEDIA_LIST_BY_FILE_3_2",
    "68": "GET_KEY_FILE",
    "69": "AUTHORIZE_CHECK",
    "70": "DONOTUSE",
    "71": "REMOTE_WRITE",
    "72": "GET_FEATURES",
    "73": "READ_HOST_CONFIG",
    "74": "READ_USER_CONFIG",
    "75": "UPDATE_HOST_CONFIG",
    "76": "UPDATE_USER_CONFIG",
    "77": "CLLIST",
    "78": "OBSOLETE",
    "79": "BPRESTORE_SYNC_4_5",
    "80": "BPRESTORE_4_5",
    "81": "IMAGE_LIST_4_5",
    "82": "BPLIST_4_5",
    "83": "DBTMPL_LIST",
    "84": "DBTMPL_GET",
    "85": "DBTMPL_PUT",
    "86": "DBTMPL_DELETE",
    "87": "DBTMPL_RENAME",
    "88": "CLNTLIST",
    "89": "DBTMPL_LIST_4_5_1",
    "90": "RESTART_RESTORE",
    "91": "VAULT_PROFILES",
    "92": "REMOTE_BROWSE",
    "93": "GET_POLICY_INFO",
    "94": "FORK_CMD",
    "95": "GET_USR_POLICY",
    "96": "CHECK_VXSS_AUTH",
    "97": "READ_TEXT_FILE",
    "98": "SUSPEND_OR_CANCEL_ALL",
    "99": "REMOTE_BPKEYUTIL",
    "100": "SNAPAPI_SW_STATUS",
    "101": "SNAPAPI_FSLIST",
    "102": "SNAPAPI_VOLLIST",
    "103": "SNAPAPI_PARTLIST",
    "104": "SNAPAPI_GETFIMINFO",
    "105": "SNAPAPI_VALCACHE",
    "106": "SNAPAPI_GET_DBTMPL",
    "107": "SNAPAPI_GET_VFMCONF",
    "108": "SNAPAPI_PREPAREMIRROR_VOL",
    "109": "SNAPAPI_SELECTMETHOD",
    "110": "VAULT_REPORTS",
    "111": "BPBACKUP_DB_6_0",
    "112": "PFI_ROTATION",
    "113": "GET_PREVIEW_MEDIA_IDS",
    "114": "GET_HOSTINFO",
    "115": "REREAD_AZ_HANDLE_CACHE",
    "116": "GET_NBAC_PDR_INFO",
    "117": "BPRESTORE_SYNC_6_5",
    "118": "BPRESTORE_6_5",
    "119": "GET_EMM_SERVER_NAME",
    "120": "UNUSED_120",
    "121": "SPSRCVASST",
    "122": "GET_POLICY_INFO_EX",
    "123": "BPRESTORE_SYNC_6_5_2",
    "124": "BPRESTORE_6_5_2",
    "125": "BPRESTORE_SYNC_6_5_2_2",
    "126": "BPRESTORE_6_5_2_2",
    "127": "BPLIST_6_5_2",
    "128": "BPFIS_STATE_XFER_TO_CLIENT",
    "129": "BPFIS_STATE_XFER_TO_SERVER",
    "130": "SUSPEND_OR_CANCEL_SELECTIVE",
    "131": "SPS_VALIDATE_CREDENTIALS",
    "132": "DARS_SEND_XML",
    "133": "SET_CLIENT_NBAC_CREDENTIALS",
    "134": "BPRESTORE_DAG",
    "135": "BPRESTORE_SYNC_DAG",
    "136": "BPRD_VM_PROXY_QUERY",
    "137": "BPRESTORE_SYNC_7_0",
    "138": "BPRESTORE_7_0",
    "139": "DARS_RUN_RESTORE",
    "140": "GET_VTS_CLIENT_LIST",
    "141": "DEL_FILE_IN_IMAGE",
    "142": "RESTORE_SFR_7_0_1",
    "143": "SET_CLIENT_NUGGET_UNUSED",
    "144": "BPFIS_STATE_DELETE_FROM_SERVER",
    "145": "CREATE_PARENT_JOB",
    "146": "SET_PARENT_JOB_STATUS",
    "147": "BPRD_GET_LOG_DAYS",
    "148": "LOG_JOB_INFO",
    "149": "SET_CLIENT_NBAC_CREDENTIALS_2",
    "150": "MANAGE_REMOTE_BROKER",
    "151": "GET_JOB_EXISTS",
    "152": "BPFIS_GET_SNAP_REPLICA_INFO",
    "153": "BPFIS_UPDATE_CATALOG",
    "154": "BPFIS_CREATE_BASE_STATE_FILES",
    "155": "CREATE_JOB",
    "156": "BPBACKUP_SYNC_7_5",
    "157": "USER_BPBACKUP_SYNC_7_5",
    "158": "USER_BPARCHIVE_SYNC_7_5",
    "159": "BPBACKUP_7_5",
    "160": "USER_BPBACKUP_7_5",
    "161": "USER_BPARCHIVE_7_5",
    "162": "GET_PREVIEW_MEDIA_IDS_7_5",
    "163": "BPLIST_7_5",
    "164": "IMAGE_LIST_7_5",
    "165": "CLEANUP_MPX_MSGQ",
    "166": "CREATE_JOB_7_6",
    "167": "INSTANCE_ADMIN",
    "168": "BPRD_VM_INSTANT_RECOVERY",
    "169": "BPRESTORE_7_6",
    "170": "BPRESTORE_SYNC_7_6",
    "171": "UPDATE_HOST_FIPS_CONFIG",
    "172": "SPSRCVASST_76",
    "173": "BPBACKUP_SYNC_7_6",
    "174": "USER_BPBACKUP_SYNC_7_6",
    "175": "USER_BPARCHIVE_SYNC_7_6",
    "176": "BPBACKUP_7_6",
    "177": "USER_BPBACKUP_7_6",
    "178": "USER_BPARCHIVE_7_6",
    "179": "BPFIS_STATE_TOPOLOGY_TO_CLIENT",
    "180": "BPFIS_STATE_TOPOLOGY_TO_SERVER",
    "181": "VM_SEARCH",
    "182": "BPLIST_7_6",
    "183": "IMAGE_LIST_7_6",
    "184": "EXCHANGE_VALIDATE_CREDENTIALS",
    "185": "READ_TEXT_FILE_7_6",
    "186": "TRUSTED_MASTER",
    "187": "TRUSTED_MASTER_LOCAL",
    "188": "SET_CLIENT_SECURITY_CREDENTIALS",
    "189": "ADD_MEDIA_DESCR_TO_IMPORT_ENTRY",
    "190": "GET_MEDIAID_SERVERS",
    "191": "BPBACKUP_DB_7_6",
    "192": "GET_PREVIEW_MEDIA_IDS_7_5_0_7",
    "193": "BPLIST_7_6_1",
    "194": "GET_TL_LATEST_APP_DATA",
    "195": "GET_TL_BACKUP_INFO",
    "196": "XFER_TL_TO_SERVER",
    "197": "XFER_TL_TO_CLIENT",
    "198": "XFER_TL_MSG_TO_SERVER",
    "199": "XBSA_PCB_XFER_TO_CLIENT",
    "200": "XBSA_PCB_XFER_TO_SERVER",
    "201": "USER_BPBACKUP_7_7",
    "202": "BPBACKUP_DB_7_7",
    "203": "NBORABKUPSETS",
    "204": "GET_REMOTE_FILE_STATUS",
    "205": "IS_SERVER_AN_APPLIANCE",
    "206": "BPRESTORE_7_7",
    "207": "BPLIST_7_7",
    "208": "BPBACKUP_SYNC_7_7",
    "209": "USER_BPBACKUP_SYNC_7_7",
    "210": "USER_BPARCHIVE_SYNC_7_7",
    "211": "BPBACKUP_7_7",
    "212": "USER_BPARCHIVE_7_7",
    "213": "GET_ORACLE_RMAN_HEADER_SIZE",
    "214": "MEDIA_LIST_BY_FILE_7_7",
    "215": "RELEASE_LEVEL",
    "216": "BPRESTORE_SYNC_7_7_1",
    "217": "BPRESTORE_7_7_1",
    "218": "SET_CLIENT_ENHANCE_AUDITING",
    "219": "READ_GUI_CONF",
    "220": "IS_USER_ACCOUNT_LOCKED",
    "221": "AUTO_UNLOCK_USER",
    "222": "UPDATE_USER_LOGIN_DETAILS",
    "223": "UNLOCK_USER",
    "224": "GET_JOB_INFO",
    "225": "BPRESTORE_SYNC_7_7_2",
    "226": "BPRESTORE_7_7_2",
    "227": "GET_LIST_LOCKED_USERS",
    "228": "BPRESTORE_SYNC_7_7_3",
    "229": "BPRESTORE_7_7_3",
    "230": "GET_RESTORE_INFO",
    "231": "XFER_TRACKLOG",
    "232": "AUDIT_USER_LOGIN_DETAILS",
    "233": "ORA_INSTANT_RECOVERY",
    "234": "VALIDATE_RESTORE_SPEC",
    "235": "BPBACKUP_JSON_8_1",
    "236": "XFER_ACC_LICENSE_INFO",
    "237": "GET_MASTER_TIMEZONE_OFFSET",
    "238": "USER_BPBACKUP_8_1",
    "239": "BPRESTORE_8_1_2",
    "240": "USER_BPBACKUP_8_1_2_1",
    "241": "CLIENT_TEST_REVERSE_CONNECT",
    "242": "BPRD_NBCS_REQ",
    "243": "BPBACKUP_8_2",
    "244": "BPIMPORT_8_2",
    "245": "RECOVEREC2_8_2",
    "246": "BPRESTORE_8_2",
    "247": "LOG_PROGRESS_INFO",
    "248": "USE_CONTROL_JOB_8_2",
    "249": "DARS_SEND_SQL_TOPOLOGY_JSON",
    "250": "GET_PROCESS_STATUS",
    "251": "GET_SERVICE_STATUS",
    "252": "GET_INCLUDE_LISTS",
    "253": "GET_EXCLUDE_LISTS",
    "254": "SET_EXCLUDE_LISTS",
    "255": "SET_INCLUDE_LISTS",
    "256": "BPBACKUP_SYNTHDUP",
    "257": "GET_APP_SERVER_DETAILS",
    "258": "READ_PROGRESS_INFO",
    "259": "SET_JOB_VALUES",
    "260": "LOG_JOB_ERROR",
    "261": "LIKELY_DATE_8_2",
    "262": "IMAGE_LIST_8_2",
    "263": "GET_JOB_INFO_JSON",
    "264": "COMPOUND_RESTORE",
    "265": "CREATE_JOB_COMPOUND_RESTORE",
    "266": "USER_PASSWORD_EXPIRATION_INFO",
    "267": "BPRESTORE_BIGDATA_APPPROXY_ASYNC",
    "268": "IMAGE_LIST_BIGDATA_APPROXY_QUERY",
    "269": "DELETE_CONFIGURATION_SETTING",
}


class BprdParamPacket(Packet):
    fields_desc = [
        StrStopField("value", default=None, stop=b" "),
        StrFixedLenField("sep", default=BprdSEP, length=1),
    ]

    def extract_padding(self, s):
        return b"", s

    def i2repr(self, pkt, v):
        return v.value.rstrip(b"\0").decode()


class BprdParamsPacketList(PacketListField):
    def i2repr(self, pkt, v):
        params_repr = [f'"{param.i2repr(pkt, param)}"' for param in v]
        return f"[{' '.join(params_repr)}]"


class StrStopField(StrField):
    __slots__ = ["stop", "enum"]

    def __init__(self, name, default, stop, enum={}):
        Field.__init__(self, name, default)
        self.stop = stop
        self.enum = enum

    def getfield(self, pkt, s):
        len_str = s.find(self.stop)
        if len_str < 0:
            return b"", s
        return s[len_str:], s[:len_str]

    def i2repr(self, pkt, v):
        r = v.rstrip(b"\0").decode()
        rr = repr(r)
        if self.enum:
            if v in self.enum:
                rr = self.enum[v]
            elif r in self.enum:
                rr = self.enum[r]
        return rr


class BprdPacket(Packet):
    fields_desc = [
        FieldLenField("msg_size", None, fmt=">L"),
        StrStopField("magic", "329199", stop=b" "),
        StrFixedLenField("sep1", default=BprdSEP, length=1),
        StrStopField("cmd", "43", stop=b" ", enum=BPRD_CMD_IDS),
        StrFixedLenField("sep2", default=BprdSEP, length=1),
        BprdParamsPacketList("param", "nbu-primary-a", BprdParamPacket),
    ]


class TLSBprdPacket(Packet):
    fields_desc = [
        X3BytesField("TLSmagic", 0x5EC100),
        ByteField("client_state", 1),
        FieldLenField("tls_msg_size", None, fmt=">L"),
        FieldLenField("msg_size", None, fmt=">L"),
        StrStopField("magic", "329199", stop=b" "),
        StrFixedLenField("sep1", default=BprdSEP, length=1),
        StrStopField("cmd", "43", stop=b" ", enum=BPRD_CMD_IDS),
        StrFixedLenField("sep2", default=BprdSEP, length=1),
        BprdParamsPacketList("param", "nbu-primary-a", BprdParamPacket),
    ]


def main():
    c = BprdPacket(bytes.fromhex("00000015333239313939203433206e62752d7072696d617279"))
    c.show2()


if __name__ == "__main__":
    main()