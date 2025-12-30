using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using TT_PPID_CS.UI.ViewModels;

namespace TT_PPID_CS.UI.Views
{
    public partial class UserDialog : Window
    {
        public UserDialog(UserViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (DataContext is UserViewModel vm)
            {
                if (string.IsNullOrWhiteSpace(vm.User.UserName))
                {
                    MessageBox.Show("用户名不能为空", "验证错误");
                    return;
                }

                if (!vm.IsEditMode)
                {
                    if (string.IsNullOrWhiteSpace(vm.Password))
                    {
                        MessageBox.Show("新建用户必须设置密码", "验证错误");
                        return;
                    }
                }

                if (!string.IsNullOrEmpty(vm.Password) && vm.Password != vm.ConfirmPassword)
                {
                    MessageBox.Show("两次输入的密码不一致", "验证错误");
                    return;
                }
            }
            
            DialogResult = true;
            Close();
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
        {
            if (DataContext is UserViewModel vm)
            {
                vm.Password = ((PasswordBox)sender).Password;
            }
        }

        private void ConfirmPasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
        {
            if (DataContext is UserViewModel vm)
            {
                vm.ConfirmPassword = ((PasswordBox)sender).Password;
            }
        }
    }
    
    // Simple InverseBooleanConverter since we don't have a shared library for converters yet
    [ValueConversion(typeof(bool), typeof(bool))]
    public class InverseBooleanConverter : IValueConverter
    {
        public object Convert(object value, System.Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            if (targetType != typeof(bool))
                throw new System.InvalidOperationException("The target must be a boolean");

            return !(bool)value;
        }

        public object ConvertBack(object value, System.Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            throw new System.NotSupportedException();
        }
    }
}
