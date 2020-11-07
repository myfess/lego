using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Windows.Forms;
using System.IO.Ports;
using System.Threading;


namespace nxtControlPanel {
    public partial class Form1 : Form {
        string DEFAULT_COM_PORT = "COM1";
        string NXT_NAME = "NXT22";

        int SENSOR_COLOR = 3;
        int SENSOR_DISTANCE = 4;
        int SENSOR_MOTOR = 5;

        // Номер ящика
        int MAIL_BOX = 1;

        private SerialPort BluetoothConnection = new SerialPort();
        BlockingCollection<List<int>> messages2 = new BlockingCollection<List<int>>();
        BlockingCollection<Lego.SensorData> incoming = new BlockingCollection<Lego.SensorData>();
        BlockingCollection<int> commands = new BlockingCollection<int>();

        BlockingCollection<Lego.ColorData> colors_history = new BlockingCollection<Lego.ColorData>();
        BlockingCollection<Lego.CommandData> deferred_commands = new BlockingCollection<Lego.CommandData>();

        Src.MySwing swing = new Src.MySwing();
        Src.Radar radar = new Src.Radar();

        public Form1() {
            InitializeComponent();

            swing.commands = commands;
            swing.deferred_commands = deferred_commands;

            Dictionary<string, string> ports = Src.Bluetooth.get_com_ports();
            string nxt22_comport = DEFAULT_COM_PORT;
            if (ports.ContainsKey(NXT_NAME)) {
                nxt22_comport = ports[NXT_NAME];
            }

            this.textBox1.Text = nxt22_comport;
        }

        private void buttonConnect_Click(object sender, EventArgs e) {
            string[] ports = SerialPort.GetPortNames();

            this.buttonConnect.Enabled = false;
            if (BluetoothConnection.IsOpen) {
                BluetoothConnection.Close();
                this.buttonConnect.Text = "Connect";
            } else {
                this.buttonConnect.Text = "Disconnect";

                this.BluetoothConnection.PortName = this.textBox1.Text.Trim();
                BluetoothConnection.Open();
                BluetoothConnection.ReadTimeout = 1500;

                Thread colorDebounceThread = new Thread(new ThreadStart(this.ThreadColorDebounce));
                colorDebounceThread.Start();

                Thread sendCommandThread = new Thread(new ThreadStart(this.ThreadSendCommand));
                sendCommandThread.Start();

                Thread commandsThread = new Thread(new ThreadStart(this.ThreadCommands));
                commandsThread.Start();

                Thread demoThread = new Thread(new ThreadStart(this.ThreadProcSafe));
                demoThread.Start();

                Thread printMessagesThread = new Thread(new ThreadStart(this.ThreadPrintMessages));
                printMessagesThread.Start();

                Thread swingThread = new Thread(new ThreadStart(this.ThreadSwing));
                swingThread.Start();

            }
            this.buttonConnect.Enabled = true;
        }

        public void print_byte(int b) {
            this.textBox3.Text += b.ToString("X2") + " ";
        }

        private void ThreadProcSafe() {
            Lego.BluetoothReading br = new Lego.BluetoothReading(BluetoothConnection);

            while (true) {
                List<int> message = br.read_message();
                if (message is null) {
                    continue;
                }
                messages2.Add(message);
            }
        }

        private void ThreadPrintMessages() {
            foreach (var m in messages2.GetConsumingEnumerable()) {
                string comm = parse_msg(m);
                Interface.ThreadHelperClass.SetText(this, textBox4, comm + Environment.NewLine);
                // ThreadHelperClass.SetText(this, textBox4, Environment.NewLine);
            }
        }

        private void ThreadSwing() {
            foreach (var sd in incoming.GetConsumingEnumerable()) {
                swing.input_data(sd);
            }
        }

        private void ThreadCommands() {
            foreach (var com in commands.GetConsumingEnumerable()) {
                Lego.Bluetooth.send_command_32(BluetoothConnection, MAIL_BOX, com);
            }
        }

        private void ThreadSendCommand() {
            int sleep_time = 50;

            List<Lego.CommandData> local = new List<Lego.CommandData>();

            while (true) {
                System.Threading.Thread.Sleep(sleep_time);

                Lego.CommandData cd;
                while (deferred_commands.TryTake(out cd)) {
                    local.Add(cd);
                }

                int len = local.Count;

                if (len == 0) {
                    continue;
                }

                long dt = DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond;

                for (int i = len - 1; i >= 0; i--) {
                    if (local[i].dt < dt) {
                        commands.Add(local[i].command);
                        local.RemoveAt(i);
                    }
                }
            }
        }

        private void ThreadColorDebounce() {
            int current_color = 1;
            int time_diff = 200;
            int sleep_time = 50;

            List<Lego.ColorData> local = new List<Lego.ColorData>();

            while (true) {
                System.Threading.Thread.Sleep(sleep_time);

                Lego.ColorData cd;
                while (colors_history.TryTake(out cd)) {
                    local.Add(cd);
                }

                long dt = DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond;
                int len = local.Count;

                if (len == 0) {
                    continue;
                }

                int next_color = current_color;
                if (dt - local[len - 1].dt > time_diff) {
                    // Сначала проверяем последний элемент, сколько прошло после него времени
                    next_color = local[len - 1].color;
                    ;
                } else {
                    for (int i = len - 1; i >= 0; i--) {
                        if (dt - local[i].dt > time_diff) {
                            break;
                        }
                        if (local[i].color != 1) {
                            next_color = local[i].color;
                            break;
                        }
                    }
                }

                if (next_color != current_color) {
                    current_color = next_color;

                    Interface.ThreadHelperClass.SetColor(this, textBox_Sensor3, current_color);

                    string msg = "NEW COLOR: " + current_color.ToString() + Environment.NewLine;
                    Interface.ThreadHelperClass.SetText(this, textBox4, msg);

                    Lego.SensorData sd = new Lego.SensorData(3, current_color);
                    incoming.Add(sd);
                }
            }
        }

        private void button2_Click(object sender, EventArgs e) {
            commands.Add(swing.turn_on_motor());
        }

        private void button3_Click(object sender, EventArgs e) {
            commands.Add(swing.turn_off_motor());
        }

        private string parse_msg(List<int> msg) {
            Lego.BTResult r = Lego.Bluetooth.parse_msg(msg);

            if (r.code == "VALUE_SENT") {
                return "Int value sent";
            }

            if (r.code == "SENSOR_DATA") {
                // string s = "DATA: " + v.ToString();
                string s = "";
                if (r.sensor_data.sensor_number == SENSOR_COLOR) {
                    colors_history.Add(new Lego.ColorData(r.sensor_data.value));
                    // s += " Color: " + sd.value.ToString();
                } else if (r.sensor_data.sensor_number == SENSOR_MOTOR) {
                    Interface.ThreadHelperClass.SetMotorLine(this, pictureBox1, r.sensor_data.value);
                } else if (r.sensor_data.sensor_number == SENSOR_DISTANCE) {
                    radar.add_data(r.sensor_data.value);
                    Interface.ThreadHelperClass.SetDistance(this, labelDistance, r.sensor_data.value);
                } else {
                    incoming.Add(r.sensor_data);
                }
                return s;
            }

            return r.code;
        }
    }
}