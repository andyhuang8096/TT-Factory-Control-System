using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.EntityFrameworkCore;
using TT_PPID_CS.Infrastructure.Persistence;
using TT_PPID_CS.Domain.Interfaces;
using TT_PPID_CS.Infrastructure.Repositories;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Application.Services;
using TT_PPID_CS.Infrastructure.Services;
using TT_PPID_CS.UI.Views;
using TT_PPID_CS.UI.ViewModels;
using System.Configuration;
using System.IO;

namespace TT_PPID_CS.UI
{
    public partial class App : System.Windows.Application
    {
        private ServiceProvider _serviceProvider;

        public App()
        {
            ServiceCollection services = new ServiceCollection();
            ConfigureServices(services);
            _serviceProvider = services.BuildServiceProvider();
            
            // 防止登录窗口关闭后程序直接退出
            this.ShutdownMode = ShutdownMode.OnExplicitShutdown;
            
            this.DispatcherUnhandledException += App_DispatcherUnhandledException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
        }

        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            MessageBox.Show($"发生未处理的异常: {e.Exception.Message}\n\n{e.Exception.InnerException?.Message}", "程序错误", MessageBoxButton.OK, MessageBoxImage.Error);
            e.Handled = true;
        }

        private void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
             MessageBox.Show($"发生致命错误: {(e.ExceptionObject as Exception)?.Message}", "致命错误", MessageBoxButton.OK, MessageBoxImage.Error);
        }

        private void ConfigureServices(ServiceCollection services)
        {
            // Database
            string connectionString = "Server=192.168.30.254,1433;Database=PPID_DB;User Id=TGUser;Password=Ydse%32gr7e#;Encrypt=True;TrustServerCertificate=True;";
            services.AddDbContext<AppDbContext>(options =>
                options.UseSqlServer(connectionString), ServiceLifetime.Transient);

            // Architecture layers
            services.AddTransient<IUnitOfWork, UnitOfWork>();
            services.AddSingleton<IAuthService, AuthService>(); // AuthService holds state (CurrentUser), so Singleton is appropriate
            services.AddTransient<IPPIDService, PPIDService>();
            services.AddTransient<IImportService, ImportService>();
            services.AddTransient<IBackupService, BackupService>();
            services.AddTransient<IUserService, UserService>();
            services.AddTransient<IReportService, ReportService>();

            // ViewModels
            services.AddSingleton<MainViewModel>();
            services.AddTransient<LoginViewModel>();
            services.AddTransient<PPIDManagementViewModel>();
            services.AddTransient<UserManagementViewModel>();
            services.AddTransient<StatisticsViewModel>();

            // Views
            services.AddSingleton<MainWindow>();
            services.AddTransient<LoginWindow>();
            services.AddTransient<PPIDManagementView>();
            services.AddTransient<UserManagementView>();
            services.AddTransient<StatisticsView>();
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            try
            {
                File.AppendAllText("app_debug.log", "App Starting OnStartup...\n");
                var loginWindow = _serviceProvider.GetRequiredService<LoginWindow>();
                
                File.AppendAllText("app_debug.log", "Showing LoginWindow...\n");
                if (loginWindow.ShowDialog() == true)
                {
                    File.AppendAllText("app_debug.log", "Login success, loading MainWindow...\n");
                    var mainWindow = _serviceProvider.GetRequiredService<MainWindow>();
                    this.MainWindow = mainWindow;
                    mainWindow.Closed += (s, args) => Shutdown();
                    
                    File.AppendAllText("app_debug.log", "Showing MainWindow...\n");
                    mainWindow.Show();
                    
                    // 延迟加载第一个视图，确保 MainWindow 已经完全就绪
                    if (mainWindow.DataContext is MainViewModel mainVm)
                    {
                        File.AppendAllText("app_debug.log", "Loading initial view...\n");
                        mainVm.SwitchToPPIDViewCommand.Execute(null);
                    }
                }
                else
                {
                    File.AppendAllText("app_debug.log", "Login cancelled.\n");
                    Shutdown();
                }
            }
            catch (Exception ex)
            {
                string error = $"启动失败: {ex.Message}\n{ex.StackTrace}\nInner: {ex.InnerException?.Message}";
                File.AppendAllText("app_debug.log", "CRASH: " + error + "\n");
                MessageBox.Show(error, "启动错误", MessageBoxButton.OK, MessageBoxImage.Error);
                Shutdown();
            }
        }
    }
}
