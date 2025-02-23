using System;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;

namespace ColorPicker
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private IntPtr _IntPtr;
        NativeLibManager.HookProc HookProc;
        public MainWindow()
        {
            InitializeComponent();

            HookProc = new NativeLibManager.HookProc(Excute);
            disableRadio.Checked += DisableRadio_Checked;
            enableRadio.Checked += EnableRadio_Checked;
            this.Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            ATxb.Text = "255";
            RTxb.Text = "65";
            GTxb.Text = "80";
            BTxb.Text = "90";
            TrySyncColorTextBox();
            enableRadio.IsChecked = true;
        }

        private void EnableRadio_Checked(object sender, RoutedEventArgs e)
        {
            ATxb.Text = "255";
            _IntPtr = NativeLibManager.SetWindowsHookEx(14, HookProc, IntPtr.Zero, 0);
        }

        private void DisableRadio_Checked(object sender, RoutedEventArgs e)
        {
            NativeLibManager.UnhookWindowsHookEx(_IntPtr);
        }

        private int Excute(int nCode, IntPtr wParam, IntPtr lParam)
        {
            if ((Int32)wParam == NativeLibManager.WM_LBUTTONDOWN)
            {
                CustomerPoint physicalpoint = new CustomerPoint();
                //获取物理坐标
                NativeLibManager.GetCursorPos(ref physicalpoint);
                //获取该坐标对应窗口的指针
                var winptr = NativeLibManager.WindowFromPoint((int)physicalpoint.x, (int)physicalpoint.y);
                //获取该设备的DC
                var wdc = NativeLibManager.GetDC(winptr);

                NativeLibManager.ScreenToClient(winptr, ref physicalpoint);
                var res = NativeLibManager.GetPixel(wdc, physicalpoint.x, physicalpoint.y);
                var red = res & 0x0000ff;
                var green = (res & 0x00ff00) / 256;
                var blue = (res & 0xff0000) / 65536;
                Application.Current.Dispatcher.Invoke(() =>
                {
                    //目前 GetPixel获取不到Alpha通道的值
                    RTxb.Text = red.ToString();
                    GTxb.Text = green.ToString();
                    BTxb.Text = blue.ToString();
                });
                NativeLibManager.ReleaseDC(IntPtr.Zero, wdc);

            }
            else if ((Int32)wParam == NativeLibManager.WM_RBUTTONDOWN)
            {
                Application.Current.Dispatcher.Invoke(() =>
                {
                    disableRadio.IsChecked = true;
                });
            }
            return NativeLibManager.CallNextHookEx(_IntPtr, nCode, wParam, lParam);
        }

        private bool isSync = false;

        private void TrySyncColorTextBox()
        {
            if (isSync)
            {
                return;
            }
            isSync = true;
            try
            {
                var color = new Color()
                {
                    A = byte.Parse(ATxb.Text.ToString()),
                    R = byte.Parse(RTxb.Text.ToString()),
                    G = byte.Parse(GTxb.Text.ToString()),
                    B = byte.Parse(BTxb.Text.ToString()),
                };
                ColorTxb.Text = color.ToString();
            }
            catch (Exception)
            {

                throw;
            }
            finally
            {
                isSync = false;
            }
        }

        private void TrySyncColorPropertyTextbox()
        {
            if (isSync)
            {
                return;
            }
            isSync = true;
            try
            {
                var color = (Color)ColorConverter.ConvertFromString(ColorTxb.Text);
                ATxb.Text = color.A.ToString();
                RTxb.Text = color.R.ToString();
                GTxb.Text = color.G.ToString();
                BTxb.Text = color.B.ToString();
            }
            catch (Exception)
            {
                throw;
            }
            finally
            {
                isSync = false;
            }
        }

        private void Txb_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            try
            {
                TrySyncColorTextBox();
            }
            catch (Exception)
            {

            }
        }

        private void Txb_LostFocus(object sender, RoutedEventArgs e)
        {
            try
            {
                TrySyncColorTextBox();
            }
            catch (Exception)
            {
                TrySyncColorPropertyTextbox();
            }
        }

        private void ColorTxb_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == Key.Enter)
            {
                try
                {
                    TrySyncColorPropertyTextbox();
                }
                catch (Exception)
                {
                   
                }
            }
        }

        private void ColorTxb_LostFocus(object sender, RoutedEventArgs e)
        {
            try
            {
                TrySyncColorPropertyTextbox();
            }
            catch (Exception)
            {
                TrySyncColorTextBox();
            }
        }
    }
}
