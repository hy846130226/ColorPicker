using System;
using System.Globalization;
using System.Windows.Data;
using System.Windows.Media;

namespace ColorPicker
{
    internal class MultiColorStringToBrushConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            try
            {
                if (values.Length == 4
                    && byte.TryParse(values[0].ToString(), out byte aValue) && aValue >= 0 && aValue <= 255
                    && byte.TryParse(values[1].ToString(), out byte rValue) && rValue >= 0 && rValue <= 255
                    && byte.TryParse(values[2].ToString(), out byte gValue) && gValue >= 0 && gValue <= 255
                    && byte.TryParse(values[3].ToString(), out byte bValue) && bValue >= 0 && bValue <= 255
                    )
                {
                    return new SolidColorBrush(new Color() { A = aValue, R = rValue, G = gValue, B = bValue });
                }
                else
                {
                    return new SolidColorBrush(Colors.Transparent);
                }
            }
            catch (Exception)
            {
                return new SolidColorBrush(Colors.Transparent);
            }
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
