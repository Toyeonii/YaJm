# -*- coding: utf-8 -*-
# noinspection PyMethodMayBeStatic

"""
eps_session.py : Control the External Power Supply
"""
import time
import UTIL.SCPI_socket as scpi
import UTIL.xmlParser as xml
import argparse

EPSHOST = ['HOST1', 'HOST2', 'HOST3']


def str2bool(v):
    if isinstance(v, bool):
        return v

    if v.lower() in ('yes', 'true', 'True', 'TRUE', 't', 'y', '1'):
        return True

    elif v.lower() in ('no', 'false', 'False', 'FASSE', 'f', 'n', '0'):
        return False

    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class OpenSessionEPS:
    def __init__(self):
        super(OpenSessionEPS, self).__init__()

        # Handle Session
        self.OpenedSESSION: dict = {}

        # HOST Info / Settings Value
        self.setv: dict = {}
        self.vrsc: dict = {}

        # Load 'config.xml'
        self.cfgXML: xml.ConfigXML = xml.ConfigXML()

        # Load Enable Flag
        self.enable: bool = str2bool(self.cfgXML.getContent(fe='EPSParams', se='EPS_Enable'))

        # Load EPS Quantity
        self.quantity: int = int(self.cfgXML.getContent(fe='EPSParams', se='EPS_Quantity'))

        # Load OVP Rate
        self.pr: float = float(self.cfgXML.getContent(fe='EPSParams', se='PROTECTIVE_RATIO'))

        # Apply Protective Ratio
        self.aPR = str2bool(self.cfgXML.getContent(fe='EPSParams', se='AppPRRatio'))

        # Load OCP Level
        self.ocpLevel: list = \
            list(map(float, self.cfgXML.getContent(fe='EPSParams', se='OCP_LEVEL').split(',')))

        # Load VISA resource & set value(voltage/current)
        for i, host in enumerate(EPSHOST):
            self.vrsc[host] = self.cfgXML.getContent(fe='EPSParams', se=f'HOST{i+1}')
            self.setv[host] = self.cfgXML.getContent(fe='EPSParams', se=f'SETVALUE{i+1}')

    def __del__(self):
        """
        소멸자에 Power Supply Off 기능을 추가한다.
        GUI OnClose() = closeEvent()에서 OpenSessionEPS를 Delete.
        'del OpenSessionEPS' 이렇게
        """
        print('Close - OpenSessionEPS')
        for i in range(self.quantity):
            if self.OpenedSESSION[EPSHOST[i]] is not None:
                print(f'HOST - {EPSHOST[i]} | SESSION - {self.OpenedSESSION[EPSHOST[i]]}')
                self.epsOff(self.OpenedSESSION[EPSHOST[i]])
                print('Done - OpenSessionEPS')

    def epsConnect(self) -> bool:
        ret: bool = False

        for i in range(self.quantity):
            _ip_ = self.vrsc[EPSHOST[i]].split(',')[0]
            port = int(self.vrsc[EPSHOST[i]].split(',')[1])

            # open session
            session = scpi.SCPI_sock_connect(_ip_, port)
            self.OpenedSESSION[EPSHOST[i]] = session

            # check IDN?
            query = scpi.SCPI_sock_query(session, '*IDN?').rsplit('\n')
            print(query)

            # set
            volt = float(self.setv[EPSHOST[i]].split(',')[0])
            curr = float(self.setv[EPSHOST[i]].split(',')[1])
            ret = self.epsSet(epsid=i, session=session, voltage=volt, current=curr, pr=self.pr)

            # print(f'{"First" if i == 0 else "Second" if i == 1 else "Third"} EPS setup completed')
            print(f'{EPSHOST[i]} | {_ip_} / {port} | {volt:.2f}V_{volt + (volt * self.pr):.2f}V / '
                  f'{curr:.2f}A_{curr + (curr * self.pr) if self.aPR else self.ocpLevel[i]:.2f}A | EPS setup completed')

            time.sleep(.5)

        return ret

    # query = scpi.SCPI_sock_query(session=session, command='OUTP?').rsplit('\n')
    # query = scpi.SCPI_sock_query(session=session, command='*OPC?').rsplit('\n')

    # noinspection PyMethodMayBeStatic
    def epsSet(self, epsid, session, voltage: float, current: float, pr: float) -> bool:
        ret: bool = True
        self.epsOff(session)

        # q = ['OUTP?', 'VOLT?', 'CURR?']
        # query = scpi.SCPI_sock_query(session=session, command=q[0]).rsplit('\n')
        # outp: bool = str2bool(query[0])
        #
        # if outp:
        #     query = scpi.SCPI_sock_query(session=session, command=q[1]).rsplit('\n')
        #     volt: float = float(query[0])
        #
        #     query = scpi.SCPI_sock_query(session=session, command=q[2]).rsplit('\n')
        #     curr: float = float(query[0])

        # OUTP?가 '0' = 'Off' = False면 설정할려고 했는데 그냥 무조건 설정 하는걸로
        # if not outp:
        # # set remote / reset
        # ret = scpi.SCPI_sock_send(session=session, command='SYST:REM;*RST')
        # query = scpi.SCPI_sock_query(session=session, command='*OPC?').rsplit('\n')

        # check Error
        while True:
            query = scpi.SCPI_sock_query(session=session, command='SYST:ERR?').rsplit('\n')
            if 'No error' in query[0]:
                break

        # set Voltage, Current and Output Enable
        ret = scpi.SCPI_sock_send(session=session, command=f'VOLT {voltage:.2f};CURR {current:.2f};OUTP 1')

        # clear Over-Voltage Protection / Over-Current Protection
        ret = scpi.SCPI_sock_send(session=session, command=f'PROTection:CLEar')

        # set OVP - Status On / Level / Delay
        ovpl = voltage + (voltage * pr)
        ret = scpi.SCPI_sock_send(session=session, command=f'VOLT:PROT:STAT ON')
        ret = scpi.SCPI_sock_send(session=session, command=f'VOLT:PROT {ovpl:.2f}')
        ret = scpi.SCPI_sock_send(session=session, command=f'VOLT:PROT:DEL 1')
        # scpi.SCPI_sock_send(session=session, command=f'VOLT:PROT:STAT ON;VOLT:PROT {ovp:.2f};VOLT:PROT:DEL 1')

        # set OCP - Status On / Level / Delay
        ocpl = current + (current * pr) if self.aPR else self.ocpLevel[epsid]
        ret = scpi.SCPI_sock_send(session=session, command=f'CURR:PROT:STAT ON')
        ret = scpi.SCPI_sock_send(session=session, command=f'CURR:PROT {ocpl:.2f}')
        ret = scpi.SCPI_sock_send(session=session, command=f'CURR:PROT:DEL 1')
        # scpi.SCPI_sock_send(session=session, command=f'CURR:PROT {ocpl:.2f};CURR:PROT:DEL 1;CURR:PROT:STAT ON')

        # check Error
        while True:
            query = scpi.SCPI_sock_query(session=session, command='SYST:ERR?').rsplit('\n')
            if 'No error' in query[0]:
                break

        return ret

    # noinspection PyMethodMayBeStatic
    def epsOn(self, session) -> bool:
        ret: bool = scpi.SCPI_sock_send(session=session, command='OUTP 1')
        time.sleep(.5)

        return ret

    # noinspection PyMethodMayBeStatic
    def epsOff(self, session) -> bool:
        # set remote / reset
        ret = scpi.SCPI_sock_send(session=session, command='SYST:REM;*RST')
        query = scpi.SCPI_sock_query(session=session, command='*OPC?').rsplit('\n')

        ret: bool = scpi.SCPI_sock_send(session=session, command='OUTP 0')
        time.sleep(.5)

        return ret

# IDN="*IDN?$"
# OCP="CURR:PROT %s$;CURR:PROT:DEL 1$;CURR:PROT:STAT ON$"
# OCP_Set="1"
# OFF="OUTP 0$"
# ON="VOLT %s$;CURR %s$;OUTP 1$"
# OPC="*OPC?$"
# OVP="VOLT:PROT %.2f$;VOLT:PROT:DEL 1$;VOLT:PROT:STAT ON$"
# OVP_Set="1"
# RST="SYST:REM$;*RST$"
# SYS_ERR="SYSTEM:ERROR?$"


if __name__ == "__main__":
    print("Module Name - eps_session.py")

    vr = OpenSessionEPS()
    r = vr.epsConnect()

    for a in range(5):
        print(f'wait - {a + 1}')
        time.sleep(1)

    del vr

    print("Done")
