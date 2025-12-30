using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Threading.Tasks;
using TT_PPID_CS.Application.Interfaces;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class LoginViewModel : ObservableObject
    {
        private readonly IAuthService _authService;

        [ObservableProperty]
        private string _username = string.Empty;

        [ObservableProperty]
        private string _password = string.Empty;

        [ObservableProperty]
        private string _statusMessage = string.Empty;

        [ObservableProperty]
        private bool _isBusy;

        public LoginViewModel(IAuthService authService)
        {
            _authService = authService;
        }

        [RelayCommand]
        private async Task LoginAsync(object? parameter)
        {
            if (string.IsNullOrWhiteSpace(Username) || string.IsNullOrWhiteSpace(Password))
            {
                StatusMessage = "请输入用户名和密码";
                return;
            }

            IsBusy = true;
            StatusMessage = "正在登录...";

            try
            {
                var user = await _authService.LoginAsync(Username, Password);
                if (user != null)
                {
                    StatusMessage = "登录成功";
                    // In a real WPF app, we might use an event or a messaging system to close the window
                    // For now, we'll use the parameter as the window
                    if (parameter is System.Windows.Window window)
                    {
                        window.DialogResult = true;
                        window.Close();
                    }
                }
                else
                {
                    StatusMessage = "用户名或密码错误";
                }
            }
            catch (System.Exception ex)
            {
                StatusMessage = $"错误: {ex.Message}";
            }
            finally
            {
                IsBusy = false;
            }
        }
    }
}
