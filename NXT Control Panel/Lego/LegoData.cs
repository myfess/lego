using System;

namespace nxtControlPanel.Lego {
    public class SensorData {
        public int sensor_number;
        public int value;

        public SensorData(int inc_value) {
            sensor_number = (inc_value >> 16) & 0xFFFF;
            value = inc_value & 0xFFFF;
        }

        public SensorData(int sn, int v) {
            sensor_number = sn;
            value = v;
        }
    }

    public class ColorData {
        public int color;
        public long dt;

        public ColorData(int color_in) {
            color = color_in;
            dt = DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond;
        }
    }

    public class CommandData {
        public int command;
        public long dt;

        public CommandData(int _command, long _dt) {
            command = _command;
            dt = _dt;
        }
    }

    public enum Color: int {
        BLACK = 1, // ничего/черный
        BLUE = 2,
        GREEN = 3,
        YELLOW = 4,
        RED = 5,
        WHITE = 6
    }
}
