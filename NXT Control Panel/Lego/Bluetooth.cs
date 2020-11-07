using System;
using System.IO.Ports;
using System.Collections.Generic;


namespace nxtControlPanel.Lego {
    public static class Bluetooth {
        public static void send_command_32(SerialPort BluetoothConnection, int mail_box, int com) {
            byte[] NxtMessage = { 0x00, 0x09, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00 };
            NxtMessage[2] = (byte)(mail_box - 1);
            int tmp = com;
            for (int ByteCtr = 0; ByteCtr <= 3; ByteCtr++) {
                NxtMessage[4 + ByteCtr] = (byte)tmp;
                tmp >>= 8;
            }
            _nxt_send_command(BluetoothConnection, NxtMessage);
        }

        private static void _nxt_send_command(SerialPort BluetoothConnection, byte[] Command) {
            Byte[] MessageLength = { 0x00, 0x00 };
            MessageLength[0] = (byte)Command.Length;

            BluetoothConnection.Write(MessageLength, 0, MessageLength.Length);
            BluetoothConnection.Write(Command, 0, Command.Length);
        }

        public static BTResult parse_msg(List<int> msg) {
            int len = msg.Count;

            if (len < 2) {
                return new BTResult("ERROR", null);
            }

            int m_len = msg[0] + msg[1] * 256;

            if (len != m_len + 2) {
                return new BTResult("ERROR", null);
            }

            if (m_len == 3 && msg[2] == 2 && msg[3] == 9 && msg[4] == 0) {
                return new BTResult("VALUE_SENT", null);
            }

            if (m_len == 9 && msg[2] == 128 && msg[3] == 9 && msg[5] == 5 && msg[10] == 0) {
                int v = 0;
                for (int i = 3; i >= 0; i--) {
                    v = v << 8;
                    v += msg[6 + i];
                }
                Lego.SensorData sd = new Lego.SensorData(v);

                return new BTResult("SENSOR_DATA", sd);
            }

            return new BTResult("UNKNOWN", null);
        }
    }

    public class BluetoothReading {
        private SerialPort BluetoothConnection;
        int state = 0;
        int len = -1;
        List<int> message = new List<int>();

        public BluetoothReading(SerialPort BluetoothConnection) {
            this.BluetoothConnection = BluetoothConnection;
        }

        public List<int> read_message() {
            try {
                int n = BluetoothConnection.ReadByte();

                message.Add(n);
                state += 1;

                if (state == 2) {
                    len = message[0] + message[1] * 256;
                }

                if (state > 2 && len == (state - 2)) {
                    state = 0;
                    List<int> res = new List<int>(message);
                    message = new List<int>();
                    return res;
                }
            } catch {
                state = 0;
                if (message.Count > 0) {
                    List<int> res = new List<int>(message);
                    message = new List<int>();
                    return res;
                }
            }

            return null;
        }
    }


    public struct BTResult {
        public string code;
        public Lego.SensorData sensor_data;

        public BTResult(string code, Lego.SensorData sensor_data) {
            this.code = code;
            this.sensor_data = sensor_data;
        }
    }
}
