from scapy import *
from scapy.packet import *
from scapy.fields import *

BPCD_CMD_IDS = {
    b"\x00\x01": "BPCD_FORK_CMD_RQST",
    b"\x00\x02": "BPCD_IMMED_CMD_RQST",
    b"\x00\x03": "BPCD_OPEN_FOR_READ_RQST",
    b"\x00\x04": "BPCD_OPEN_FOR_WRITE_RQST",
    b"\x00\x05": "BPCD_READ_RQST",
    b"\x00\x06": "BPCD_WRITE_RQST",
    b"\x00\x07": "BPCD_RM_FILE_RQST",
    b"\x00\x08": "BPCD_RM_DIR_RQST",
    b"\x00\t": "BPCD_CLOSE_FILE_RQST",
    b"\x00\n": "BPCD_BECOME_USER_RQST",
    b"\x00\x0b": "BPCD_SEND_MAIL_RQST",
    b"\x00\x0c": "BPCD_DISCONNECT_RQST",
    b"\x00\r": "BPCD_FORK_CMD_W_LOG_RQST",
    b"\x00\x0e": "BPCD_LOG_RQST",
    b"\x00\x0f": "BPCD_LOG_RQST_NO_STATUS",
    b"\x00\x10": "BPCD_PEERNAME_RQST",
    b"\x00\x11": "BPCD_BECOME_USER_GROUP_RQST",
    b"\x00\x12": "BPCD_SEND_SIGNAL_TO_PID",
    b"\x00\x13": "BPCD_HOSTNAME_RQST",
    b"\x00\x14": "BPCD_GET_STDOUT_SOCKET_RQST",
    b"\x00\x15": "BPCD_TIME_TO_KEY_RQST",
    b"\x00\x16": "BPCD_CLIENTNAME_RQST",
    b"\x00\x17": "BPCD_GET_STDIN_SOCKET_RQST",
    b"\x00\x18": "BPCD_GET_VERSION_RQST",
    b"\x00\x19": "BPCD_GET_LIST_JOBS_RQST",
    b"\x00\x1a": "BPCD_GET_JOB_FILE_RQST",
    b"\x00\x1b": "BPCD_GET_PLATFORM_RQST",
    b"\x00\x1c": "BPCD_GET_CRYPT_CONF_RQST",
    b"\x00\x1d": "BPCD_SET_CRYPT_CONF_RQST",
    b"\x00\x1e": "BPCD_GET_CRYPT_VERSIONS_RQST",
    b"\x00\x1f": "BPCD_RENAME_FILE_RQST",
    b"\x00 ": "BPCD_TEMP_FILE_RQST",
    b"\x00!": "BPCD_DELETE_JOB_FILE_RQST",
    b'\x00"': "BPCD_ADD_CRYPT_PASSPHRASE_RQST",
    b"\x00#": "BPCD_OPEN_FOR_WRITE_WITH_MODE_RQST",
    b"\x00$": "BPCD_READ_HOST_CONFIG_RQST",
    b"\x00%": "BPCD_READ_USERS_CONFIG_RQST",
    b"\x00&": "BPCD_UPDATE_HOST_CONFIG_RQST",
    b"\x00'": "BPCD_UPDATE_USERS_CONFIG_RQST",
    b"\x00-": "BPCD_GET_BE_VERSION_RQST",
    b"\x00.": "BPCD_ADD_CRYPT_KEYS_RQST",
    b"\x00/": "BPCD_CRYPT_KEYS_RQST",
    b"\x000": "BPCD_READ_DIR_RQST",
    b"\x001": "BPCD_FORK_CMD_W_STAT_RQST",
    b"\x003": "BPCD_READ_TEXT_FILE_RQST",
    b"\x004": "BPCD_GET_PROCESS_STATUS_RQST",
    b"\x007": "BPCD_READ_DIR_RQST_EX",
    b"\x00<": "BPCD_GET_STDIN_HOST_SOCKET_RQST",
    b"\x00;": "BPCD_GET_STDOUT_HOST_SOCKET_RQST",
    b"\x00=": "BPCD_GET_BPRD_SOCKET_RQST",
    b"\x00@": "BPCD_GET_REMOTE_INFO",
    b"\x00A": "BPCD_GET_PRIVILEGES_RQST",
    b"\x00B": "BPCD_FORK_OTHER_CMD_RQST",
    b"\x00C": "BPCD_GET_NB_VERSION_RQST",
    b"\x00D": "BPCD_GET_LICENSE_PLATFORM_RQST",
    b"\x00E": "BPCD_GET_UNAME_RQST",
    b"\x00F": "BPCD_SET_LOCALE_RQST",
    b"\x00G": "BPCD_SET_ALL_LOCALE_RQST",
    b"\x00H": "BPCD_MK_DIR_RQST",
    b"\x00I": "BPCD_GET_FILEINFO_RQST",
    b"\x00J": "BPCD_SNAPAPI_GET_SW_STATUS_RQST",
    b"\x00K": "BPCD_SNAPAPI_GET_FSLIST_RQST",
    b"\x00L": "BPCD_SNAPAPI_GET_VOLLIST_RQST",
    b"\x00M": "BPCD_SNAPAPI_GET_PARTLIST_RQST",
    b"\x00N": "BPCD_SNAPAPI_GET_FIMINFO_RQST",
    b"\x00O": "BPCD_SNAPAPI_GET_CACHESTS_RQST",
    b"\x00P": "BPCD_SNAPAPI_PREPARE_MIRROR_VOL",
    b"\x00Q": "BPCD_GET_BMR_CONFIG",
    b"\x00S": "BPCD_UL_RQST",
    b"\x00T": "BPCD_SEEK_RQST",
    b"\x00U": "BPCD_TEST_BPCD_RQST",
    b"\x00V": "BPCD_READ_LOG_FILES_DATE_RQST",
    b"\x00W": "BPCD_GET_EMM_INFO_RQST",
    b"\x00X": "BPCD_SNAPAPI_GET_DBLIST_RQST",
    b"\x00Y": "BPCD_FORK_W_PID_W_STAT_RQST",
    b"\x00Z": "BPCD_GET_TFI_INFO_RQST",
    b"\x00[": "BPCD_VOLUME_CLEANUP_RQST",
    b"\x00\\": "BPCD_FORK_OTHER_W_PID_RQST",
    b"\x00]": "BPCD_SPSV2_START_RECOVERY_ASST_RQST",
    b"\x00^": "BPCD_FORK_OUTPUT_RQST",
    b"\x00_": "BPCD_VMUTIL_CMD_RQST",
    b"\x00`": "BPCD_VSSAT_CMD_RQST",
    b"\x00a": "BPCD_VSSAZ_CMD_RQST",
    b"\x00b": "BPCD_PATCH_VERSION_RQST",
    b"\x00c": "BPCD_START_NBFSD_RQST",
    b"\x00d": "BPCD_REMOTE_FILE_COPY",
    b"\x00e": "BPCD_START_NBGRE_RQST",
    b"\x00f": "BPCD_GET_PROD_OPT_INST_LOG_RQST",
    b"\x00g": "BPCD_GET_PROD_OPT_CONF_RQST",
    b"\x00h": "BPCD_CHMOD_VLTRUN_RQST",
    b"\x00i": "BPCD_SLIBCLEAN_RQST",
    b"\x00j": "BPCD_AT_LOGINMACHINE_RQST",
    b"\x00k": "BPCD_AT_GETVXSSVER_RQST",
    b"\x00l": "BPCD_BPFIS_STATE_XFER_PREPARE_RQST",
    b"\x00m": "BPCD_TERMINATE_RQST",
    b"\x00n": "BPCD_GET_FILEINFO2_RQST",
    b"\x00o": "BPCD_GET_TIER_INFO_RQST",
    b"\x00p": "BPCD_GET_EXCLUDE_LIST_RQST",
    b"\x00q": "BPCD_SET_EXCLUDE_LIST_RQST",
    b"\x00r": "BPCD_GET_INCLUDE_LIST_RQST",
    b"\x00s": "BPCD_SET_INCLUDE_LIST_RQST",
    b"\x00t": "BPCD_SPS_VALIDATE_CREDENTIALS",
    b"\x00u": "BPCD_GET_BROKER_CERT_RQST",
    b"\x00v": "BPCD_GET_VXDBMS_CONF_RQST",
    b"\x00w": "BPCD_SET_VXDBMS_CONF_RQST",
    b"\x00x": "BPCD_GET_ALL_HOSTNAMES_RQST",
    b"\x00y": "BPCD_SET_CREDENTIALS_RQST",
    b"\x00{": "BPCD_STOP_PROXY_RQST",
    b"\x00\x80": "BPCD_GET_EXCH_VERSION_RQST",
    b"\x00\x81": "BPCD_GET_CHARSET_RQST",
    b"\x00\x82": "BPCD_OPEN_FOR_VM_READ_RQST",
    b"\x00\x83": "BPCD_UPDATE_HOST_CONFIG_W_AUDIT_RQST",
    b"\x00\x84": "BPCD_MANAGE_BROKER_RQST",
    b"\x00\x85": "BPCD_UPDATE_RESILIENCY_RQST",
    b"\x00\x86": "BPCD_GET_ACCL_CLIENT_BACKUP_IDS_RQST",
    b"\x00\x87": "BPCD_GET_ACCL_SUPPORTED_RQST",
    b"\x00\x89": "BPCD_START_PROXY2_RQST",
    b"\x00\x8a": "BPCD_GET_VALID_APP_GRT_PLATFORM_RQST",
    b"\x00\x8b": "BPCD_TOPOLOGY_TO_CLIENT",
    b"\x00\x8c": "BPCD_TOPOLOGY_TO_SERVER",
    b"\x00\x8d": "BPCD_GET_ACCL_APP_SUPPORTED_RQST",
    b"\x00\x8e": "BPCD_SPS_START_RECOVERY_ASST_RQST",
    b"\x00\x8f": "BPCD_GET_VM_CLIENT_ACCL_BACKUP_ID_RQST",
    b"\x00\x90": "BPCD_WANT_STATUSMSGS_RQST",
    b"\x00\x91": "BPCD_PUT_ACCL_CLIENT_BACKUP_IDS_RQST",
    b"\x00\x92": "BPCD_TEST_BPCD_2_RQST",
    b"\x00\x93": "BPCD_OPEN_TMPFILE_FOR_WRITE_RQST",
    b"\x00\x94": "BPCD_NBORABKUPSETS_RQST",
    b"\x00\x95": "BPCD_GET_REMOTE_FILE_STATUS_RQST",
    b"\x00\x96": "BPCD_GET_APPLIANCE_MODE_RQST",
    b"\x00\x97": "BPCD_GET_ACCL_NDMP_BACKUP_IDS_RQST",
    b"\x00\x98": "BPCD_EXPORT_IMAGE_RQST",
    b"\x00\x99": "BPCD_READ_LOG_FILES_DATE_USER_RQST",
    b"\x00\x9a": "BPCD_UNMOUNT_IMAGE_RQST",
    b"\x00\x9b": "BPCD_GET_RMAN_HEADER_RQST",
    b"\x00\x9c": "BPCD_REMOTE_FILE_READ_FROM_NB_TMP_DIR",
    b"\x00\x9d": "BPCD_REMOTE_FILE_WRITE_TO_NB_TMP_DIR",
    b"\x00\x9e": "BPCD_GET_VM_CLIENT_ACCL_BACKUP_ID_ON_MASTER_RQST",
    b"\x00\x9f": "BPCD_GET_CGD_TELEMETRY_INFO",
    b"\x00\xa0": "BPCD_GET_STDERR_SOCKET_RQST",
    b"\x00\xa1": "BPCD_TEST_BPCD_3_RQST",
    b"\x00\xa2": "BPCD_GET_STDIN_STDOUT_SOCKET_RQST",
    b"\x00\xa3": "BPCD_GET_STDERR_STDOUT_SOCKET_RQST",
    b"\x00\xa4": "BPCD_REMOVE_TEMP_FILE_RQST",
    b"\x00\xa5": "BPCD_SET_DOMAIN_CTX_RQST",
    b"\x00\xa6": "BPCD_GET_DOMAIN_CTX_RQST",
    b"\x00\xa7": "BPCD_CERT_MGMT",
    b"\x00\xa8": "BPCD_GET_SERVICE_STATUS_RQST",
    b"\x00\xa9": "BPCD_GET_INCLUDE_LISTS_RQST",
    b"\x00\xaa": "BPCD_GET_EXCLUDE_LISTS_RQST",
    b"\x00\xab": "BPCD_SET_INCLUDE_LISTS_RQST",
    b"\x00\xac": "BPCD_SET_EXCLUDE_LISTS_RQST",
    b"\x00\xad": "BPCD_NBAAPI_CMD_RQST",
    b"\x00\xae": "BPCD_DELETE_CONFIGURATION_SETTING_RQST",
}


class BpcdCmdField(StrFixedLenEnumField):
    def i2repr(self, pkt, v):
        r = v.rstrip(b"\0").decode()
        rr = repr(r)
        if self.enum:
            if v in self.enum:
                rr = self.enum[v]
            elif r in self.enum:
                rr = self.enum[r]
        return rr


class TLSBpcdPacket(Packet):
    fields_desc = [
        X3BytesField("TLSmagic", 0x5EC100),
        ByteField("client_state", 1),
        FieldLenField("tls_msg_size", None, fmt=">L"),
        BpcdCmdField(
            "data", "", length_from=lambda pkt: pkt.tls_msg_size, enum=BPCD_CMD_IDS
        ),
    ]


def main():
    d = TLSBpcdPacket(
        bytes.fromhex("5ec10001000000020005"),
    )
    d.show2()


if __name__ == "__main__":
    main()