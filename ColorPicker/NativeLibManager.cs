using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ColorPicker
{
    [StructLayout(LayoutKind.Sequential)]
    public struct CustomerPoint
    {
        public int x;
        public int y;
    }
    [StructLayout(LayoutKind.Sequential)]
    public class MouseHookStruct
    {
        public CustomerPoint pt;
        public int hwnd;
        public int wHitTestCode;
        public int dwExtraInfo;
    }

    public static class NativeLibManager

    {
        /// <summary>
        /// 返回参数坐标对应的窗口的Intptr
        /// </summary>
        /// <param name="xpoint"></param>
        /// <param name="ypoint"></param>
        /// <returns></returns>
        [DllImport("user32.dll", EntryPoint = "WindowFromPoint")]
        public static extern IntPtr WindowFromPoint(int xpoint, int ypoint);

        /// <summary>
        /// 获取鼠标位置
        /// </summary>
        /// <param name="point"></param>
        /// <returns>鼠标当前相当于屏幕坐标系的位置</returns>
        [DllImport("user32.dll", EntryPoint = "GetCursorPos")]
        public static extern bool GetCursorPos(ref CustomerPoint point);

        /// <summary>
        /// 将全局坐标转换到某个窗口的坐标系
        /// </summary>
        /// <param name="hwnd"></param>
        /// <param name="p"></param>
        /// <returns>Long，非零表示成功，零表示失败</returns>
        [DllImport("user32.dll", EntryPoint = "ScreenToClient")]
        public static extern long ScreenToClient(IntPtr hwnd, ref CustomerPoint p);

        /// <summary>
        /// 获取设备驱动器句柄
        /// </summary>
        /// <param name="hwnd"></param>
        /// <returns></returns>
        [DllImport("user32.dll", EntryPoint = "GetDC")]
        public static extern IntPtr GetDC(IntPtr hwnd);

        /// <summary>
        /// 释放由调用GetDC或GetWindowDC函数获取的指定设备场景。它对类或私有设备场景无效（但这样的调用不会造成损害）
        /// </summary>
        /// <param name="hwnd"></param>
        /// <param name="hdc"></param>
        /// <returns></returns>
        [DllImport("user32.dll", EntryPoint = "ReleaseDC")]
        public static extern int ReleaseDC(IntPtr hwnd, IntPtr hdc);

        /// <summary>
        /// 在指定的设备场景中取得一个像素的RGB值
        /// </summary>
        /// <param name="hdc"></param>
        /// <param name="x">逻辑坐标</param>
        /// <param name="y"></param>
        /// <returns></returns>
        [DllImport("gdi32.dll", EntryPoint = "GetPixel")]
        public static extern long GetPixel(IntPtr hdc, int x, int y);

        public static int hMouseHook = 0;
        public const int WM_MOUSEMOVE = 0x200;
        public const int WM_LBUTTONDOWN = 0x201;
        public const int WM_RBUTTONDOWN = 0x204;
        public const int WM_MBUTTONDOWN = 0x207;
        public const int WM_LBUTTONUP = 0x202;
        public const int WM_RBUTTONUP = 0x205;
        public const int WM_MBUTTONUP = 0x208;
        public const int WM_LBUTTONDBLCLK = 0x203;
        public const int WM_RBUTTONDBLCLK = 0x206;
        public const int WM_MBUTTONDBLCLK = 0x209;

        public delegate int HookProc(int nCode, IntPtr wParam, IntPtr lParam);
        /// <summary>
        /// 安装钩子
        /// </summary>
        /// <param name="idHook">钩子类型 13键盘和14鼠标,用来对底层输入事件监视</param>
        /// <param name="callback">函数指针</param>
        /// <param name="hInstance">包含SetWindowsHookEx函数的模块地址,user32.dll入口</param>
        /// <param name="threadId">0表示系统钩子,</param>
        /// <param name="str"></param>
        /// <returns></returns>
        [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
        public static extern IntPtr SetWindowsHookEx(int idHook, HookProc lpfn, IntPtr hInstance, int threadId);
        //卸载钩子
        [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
        public static extern bool UnhookWindowsHookEx(IntPtr idHook);
        //调用下一个钩子
        [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
        public static extern int CallNextHookEx(IntPtr idHook, int nCode, IntPtr wParam, IntPtr lParam);

        /// <summary>
        /// 判断窗口是否存在
        /// </summary>
        /// <param name="hWnd"></param>
        /// <returns></returns>
        [DllImport("user32", EntryPoint = "IsWindow")]
        public static extern bool IsWindow(IntPtr hWnd);

        /// <summary>
        /// 设置窗口标题
        /// </summary>
        /// <param name="hwnd"></param>
        /// <param name="text"></param>
        /// <returns></returns>
        [DllImport("user32", EntryPoint = "SetWindowText")]
        public static extern long SetWindowText(IntPtr hwnd, string text);
    }
}
