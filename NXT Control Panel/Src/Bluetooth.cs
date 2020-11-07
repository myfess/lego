using System.Collections.Generic;

namespace nxtControlPanel.Src {
    public static class Bluetooth {
        public static Dictionary<string, string> get_com_ports() {
            Dictionary<string, string> res = new Dictionary<string, string>();

            Libs.AvailablePorts ports = new Libs.AvailablePorts();
            ports.GetBluetoothCOMPort();
            System.Collections.ObjectModel.ObservableCollection<Libs.COMPort> obs = ports.COMPorts;

            List<string> ls = Libs.ComHelper.GetPairedNxtBluetoothCom();
            Dictionary<string, string> ls2 = Libs.ComHelper.GetPairedNxtBluetoothBTAddress();
            
            foreach (var p in obs) {
                if (p.Direction != Libs.Direction.OUTGOING) {
                    continue;
                }
                res.Add(p.Name, p.SerialPort);
            }

            return res;
        }
    }
}
