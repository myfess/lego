using System;
using System.Collections.Concurrent;

namespace nxtControlPanel.Src {
    public class MySwing {
        const int MOTOR_B = 2;

        int direction = 1;
        int last_color = (int)Lego.Color.BLACK;
        long kick_milliseconds = 0;

        public BlockingCollection<int> commands;
        public BlockingCollection<Lego.CommandData> deferred_commands;

        public int turn_on_motor() {
            int motor_number = 1;
            int motor_power = 60;
            int com = (motor_number << 8) + (100 + motor_power * direction);
            return com;
        }

        public int turn_off_motor() {
            int motor_number = 1;
            int motor_power = 0;
            int com = (motor_number << 8) + (100 + motor_power * direction);
            return com;
        }

        int rotate_360(int motor) {
            int motor_number = motor;
            int motor_power = 100;
            int motor_mode = 1;
            int com = (motor_mode << 16) + (motor_number << 8) + (100 + motor_power);
            return com;
        }

        public void input_data(Lego.SensorData sd) {
            return;

            if (sd.sensor_number == 1) {
                direction *= -1;
                commands.Add(turn_on_motor());
            } else if (sd.sensor_number == 2) {
                commands.Add(turn_off_motor());
            } else if (sd.sensor_number == 3) {
                if (last_color == sd.value) {
                    return;
                }
                last_color = sd.value;

                long now_milliseconds = DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond;
                long diff = now_milliseconds - kick_milliseconds;

                if (diff < 2000) {
                    return;
                }

                if (sd.value == (int)Lego.Color.RED) {
                    deferred_commands.Add(new Lego.CommandData(
                        rotate_360(MOTOR_B),
                        now_milliseconds + 3300
                    ));
                    // commands.Add(rotate_360(MOTOR_B));
                    kick_milliseconds = now_milliseconds;
                }

            }
        }
    }
}
