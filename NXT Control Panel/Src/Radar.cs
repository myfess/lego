using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace nxtControlPanel.Src {
    class Radar {
        List<DistanceData> data = new List<DistanceData>();

        public void add_data(int distance) {
            if (distance == 255) {
                return;
            }

            data.Add(new DistanceData(distance));
        }

        public List<int> get_last_points() {
            List<int> res = new List<int>();

            DateTime dt = DateTime.Now.AddSeconds(-10);

            for (int i = data.Count; i >= 0; i--) {
                if (data[i].dt < dt) {
                    break;
                }
                res.Add(data[i].distance);
            }

            return res;

        }
    }

    public struct DistanceData {
        public int distance;
        public DateTime dt;

        public DistanceData(int distance) {
            this.distance = distance;
            this.dt = DateTime.Now;
        }
    }
}
