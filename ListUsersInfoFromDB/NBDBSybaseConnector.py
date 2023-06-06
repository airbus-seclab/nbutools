#!/usr/bin/python3
import logging

import jpype
import jaydebeapi


class NBDBSybaseConnector(object):
    """SybaseConnector"""

    def __init__(self, password, host, port, jconn4_file_path):
        self.con = None
        try:
            logging.debug(
                "Attempting to start JVM with classes from %s", jconn4_file_path
            )
            jvm_path = jpype.getDefaultJVMPath()
            jpype.addClassPath(jconn4_file_path)
            jpype.startJVM(jvm_path)
            SybDriver = jpype.JClass("com.sybase.jdbc4.jdbc.SybDriver")
            drivers = SybDriver()
            logging.debug("Successfully loaded Sybase driver")
        except Exception as e:
            logging.error("Failed to load Sybase driver: %s", e)
            return

        try:
            url = f"jdbc:sybase:Tds:{host}:{port}?ServiceName=NBDB"
            logging.debug("Attempting to connect to database on %s", url)
            self.con = jaydebeapi.connect(
                jclassname="com.sybase.jdbc4.jdbc.SybDriver",
                url=url,
                driver_args={"user": "dba", "password": password},
            )

            logging.debug(
                "Connection to %s with DBA password %s successful", host, password
            )
        except Exception as e:
            logging.error(
                "Failed to authenticate on host %s with DBA password %s: %s",
                host,
                password,
                e,
            )

    def exec_sql(self, query):
        if self.con:
            curs = self.con.cursor()
            curs.execute(query)
            try:
                return curs.fetchall()
            except jaydebeapi.Error:
                return None

    def get_username_and_hashedpwd_from_ndbd(self):
        if self.con == None:
            logging.error("Connection failed")
            return None

        query = """SELECT users.user_name, pwd.password 
                   FROM SYS.SYSUSERPASSWORD as pwd 
                   INNER JOIN SYS.SYSUSER as users 
                   ON users.user_id=pwd.user_id"""

        logging.debug(
            "Executing SQL query '%s'", query.replace("\n", " ").replace("  ", "")
        )
        curs = self.exec_sql(query)
        return curs


def test():
    nbdbcntr = NBDBSybaseConnector("aaaaaa", "127.0.0.1")
    if nbdbcntr.con:
        curs = nbdbcntr.get_username_and_hashedpwd_from_ndbd()


if __name__ == "__main__":
    test()
