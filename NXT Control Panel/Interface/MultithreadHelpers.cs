using System;
using System.Drawing;
using System.Windows.Forms;


namespace nxtControlPanel.Interface {
    public static class ThreadHelperClass {
        delegate void SetTextCallback(Form f, Control ctrl, string text);

        public static void SetText(Form form, Control ctrl, string text) {
            if (ctrl.InvokeRequired) {
                SetTextCallback d = new SetTextCallback(SetText);
                form.Invoke(d, new object[] { form, ctrl, text });
            } else {
                ctrl.Text = text + ctrl.Text;
            }
        }

        delegate void SetColorCallback(Form f, Control ctrl, int color);

        public static void SetColor(Form form, Control ctrl, int color) {
            if (ctrl.InvokeRequired) {
                SetColorCallback d = new SetColorCallback(SetColor);
                form.Invoke(d, new object[] { form, ctrl, color });
            } else {
                Color cv = Color.Black;
                if (color == 1) {
                    cv = Color.Black;
                } else if (color == 2) {
                    cv = Color.Blue;
                } else if (color == 3) {
                    cv = Color.Green;
                } else if (color == 4) {
                    cv = Color.Yellow;
                } else if (color == 5) {
                    cv = Color.Red;
                } else if (color == 6) {
                    cv = Color.White;
                }

                ctrl.BackColor = cv;
            }
        }

        delegate void SetDistanceCallback(Form f, Label ctrl, int distance);

        public static void SetDistance(Form form, Label ctrl, int distance) {
            if (ctrl.InvokeRequired) {
                SetDistanceCallback d = new SetDistanceCallback(SetDistance);
                form.Invoke(d, new object[] { form, ctrl, distance });
            } else {
                ctrl.Text = distance.ToString();
            }
        }


        delegate void SetMotorLineCallback(Form f, PictureBox ctrl, int motor);

        public static void SetMotorLine(Form form, PictureBox ctrl, int motor) {
            if (ctrl.InvokeRequired) {
                SetMotorLineCallback d = new SetMotorLineCallback(SetMotorLine);
                form.Invoke(d, new object[] { form, ctrl, motor });
            } else {
                if (ctrl.Image == null) {
                    Bitmap bmp = new Bitmap(ctrl.Width, ctrl.Height);
                    ctrl.Image = bmp;
                }

                using (Graphics g = Graphics.FromImage(ctrl.Image)) {
                    System.Drawing.SolidBrush myBrush = new System.Drawing.SolidBrush(System.Drawing.Color.Black);

                    double angle = Math.PI * motor / 180.0;
                    double sin_angle = Math.Sin(angle);
                    double cos_angle = Math.Cos(angle);

                    int center_x = 250;
                    int center_y = 250;
                    int x = center_x + Convert.ToInt32(cos_angle * 200);
                    int y = center_y + Convert.ToInt32(sin_angle * 200);
                    Point s = new Point(center_x, center_y);
                    Point f = new Point(x, y);
                    g.FillRectangle(myBrush, new Rectangle(0, 0, 500, 500));
                    g.DrawLine(new Pen(Color.Green, 2), s, f);

                    myBrush.Dispose();
                }

                ctrl.Invalidate();
            }
        }
    }
}
